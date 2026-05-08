import json
import os
import time

import minio_helper
import psutil
from args import ARGS
from dirs import (
    BIN_DIR,
    SPICE_SNAPSHOTS,
    CALADAN_DIR,
    CHROOT_DIR,
    FUNCTIONS,
    JIFTOOL,
    JRUN,
    NODE_BIN,
    NODE_PATH,
    READJIF,
)
from func_args import FUNCTION_ARGS
from ip_alloc import IPAllocator, addr_to_str
from test import Test
from util import dropcache, jifpager_installed, run

KTHREADS_PER_INSTANCE = 1
KERNEL_TRACE_RUNS = 20


def get_allowed_cores():
    physical_cores = psutil.cpu_count(logical=False)
    # core 0 is often noisy with interrupts
    # core 1 = iokerneld
    # core 2 = page pool
    # core 3 = minor prefetcher
    # cores 4,5 = major prefetchers
    return f"6-{physical_cores}"


def run_iok(output_log):
    run(f"sudo {CALADAN_DIR}/scripts/setup_machine.sh nouintr")
    logf = f"{output_log}_iokernel.log"

    run(
        f"sudo {CALADAN_DIR}/iokerneld ias noht nobw no_hw_qdel numanode -1 -- --allow 00:00.0 --vdev=net_tap0 {get_allowed_cores()} > {logf} 2>&1 &"
    )

    while os.system(f"grep -q 'running dataplan' {logf}") != 0:
        time.sleep(0.3)

    run("sudo ip addr add 192.168.120.1/16 dev dtap0 || true")


def kill_iok():
    run("(sudo pkill iokerneld && sleep 1) || true")


def config_jifpager(
    prefault: bool = False,
    minor_prefault: bool = False,
    use_page_pool: bool = False,
    pre_cow: bool = False,
    trace: bool = False,
    parallel: bool = False,
    prefetch_direct: bool = False,
):
    run(f"echo {1 if prefault else 0} | sudo tee /sys/kernel/jifpager/prefault")
    run(
        f"echo {1 if minor_prefault else 0} | sudo tee /sys/kernel/jifpager/prefault_minor"
    )
    run(
        f"echo {1 if use_page_pool else 0} | sudo tee /sys/kernel/jifpager/use_folio_pool"
    )
    run(f"echo {1 if pre_cow else 0} | sudo tee /sys/kernel/jifpager/pre_cow")
    run(f"echo {1 if trace else 0} | sudo tee /sys/kernel/jifpager/trace")
    run(f"echo {1 if parallel else 0} | sudo tee /sys/kernel/jifpager/parallel")
    run(
        f"echo {1 if prefetch_direct else 0} | sudo tee /sys/kernel/jifpager/prefetch_direct"
    )
    run("echo 1 | sudo tee /sys/kernel/jifpager/reset")


def chroot_args():
    if not ARGS.use_chroot:
        return ""
    return f" --chroot={CHROOT_DIR} --cache_linux_fs"


def gen_lc_config(file, ip, mask, gw, cores, quantum=0):
    cfg = [
        f"host_addr {addr_to_str(ip)}",
        f"host_netmask {addr_to_str(mask)}",
        f"host_gateway {addr_to_str(gw)}",
        f"runtime_kthreads {cores}",
        "runtime_spinning_kthreads 0",
        "runtime_guaranteed_kthreads 0",
        "runtime_priority lc",
        "runtime_quantum_us 100",
    ]
    with open(file, "w") as f:
        f.write("\n".join(cfg))


class SpiceTest(Test):
    def __init__(
        self,
        lang: str,
        name: str,
        cmd: str,
        arg_map,
        s3=False,
        env="",
    ):
        if s3:
            d = json.loads(arg_map)
            d["minio_addr"] = f"{minio_helper.MINIO_IP}:9000"
            arg_map = json.dumps(d)

        super().__init__(lang, name, cmd, arg_map, s3=s3, env=env)

    def snapshot_prefix(self, with_chroot=False):
        func_id = self.id()

        if with_chroot and ARGS.use_chroot:
            return f"{CHROOT_DIR}/tmp/{func_id}"

        if ARGS.use_chroot:
            return f"/tmp/{func_id}"

        return f"{SPICE_SNAPSHOTS}/{func_id}"

    def run(self, junction_args, cmd, log, result_dir):
        ip_alloc = IPAllocator()

        ip = ip_alloc.next()
        cfg = f"{result_dir}/junction.config"
        gen_lc_config(
            cfg, ip, ip_alloc.get_netmask(), ip_alloc.get_base(), KTHREADS_PER_INSTANCE
        )

        run(f"sudo -E {JRUN} {cfg} {junction_args} -- {cmd} >> {log} 2>&1")

    def snapshot_shelf(self, output_log: str, result_dir: str):
        junction_args = (
            f"--function_arg '{self.args}' --function_name {self.id()} {self._env()}"
        )
        prefix = self.snapshot_prefix()

        if ARGS.cold_uarch:
            junction_args += " --bench_cold_uarch_state"

        self.run(
            f"{junction_args} {chroot_args()} --jif --madv_remap --snapshot-prefix {prefix}",
            self.cmd,
            f"{output_log}_snap_shelf",
            result_dir,
        )

    def build_itree(self, output_log: str):
        prefix = self.snapshot_prefix(with_chroot=True)
        chroot_dir = CHROOT_DIR if ARGS.use_chroot else ""

        run(
            f'stdbuf -e0 -i0 -o0 {JIFTOOL} {prefix}.jif "build-itrees {chroot_dir}" "write {prefix}_itrees.jif" >> {output_log}_build_itrees 2>&1'
        )

    def add_access_trace(self, output_log: str, itrees: bool = True):
        itrees_str = "_itrees" if itrees else ""
        prefix = self.snapshot_prefix(with_chroot=True)

        jiftool_cmds = (
            f'"add-ord {prefix}.ord" tag-vmas "write {prefix}{itrees_str}_ord.jif" '
            f'setup-prefetch tag-vmas "write {prefix}{itrees_str}_ord_reorder.jif" '
        )

        run(
            f"stdbuf -e0 -i0 -o0 {JIFTOOL} {prefix}{itrees_str}.jif {jiftool_cmds} >> {output_log}_add_ord 2>&1"
        )

    def do_kernel_trace(self, output_log: str, result_dir: str):
        path = self.snapshot_prefix(with_chroot=True)
        dropcache()
        last_ws_count = 0
        n_unchanged = 0
        for i in range(KERNEL_TRACE_RUNS):
            self.jifpager_restore_shelf(
                f"{output_log}_build_ord",
                result_dir,
                cold=True,
                prefault=True,
                minor_prefault=i % 2 == 0,
                prefetch_direct=True,
                use_page_pool=True,
                cow=True,
                trace=True,
            )
            run(f"sudo cat /sys/kernel/debug/jifpager/mem_trace {path}.ord > /tmp/ord")
            run(f"sort -n /tmp/ord | sudo tee {path}.ord > /dev/null")
            self.add_access_trace(output_log)
            ws_pages = run(f"{READJIF} {path}_itrees_ord_reorder.jif ord.pages").decode(
                "utf-8"
            )
            ws_pages = json.loads(ws_pages)["ord.pages"]
            if ws_pages == last_ws_count:
                n_unchanged += 1
            else:
                n_unchanged = 0

            print("ws pages", ws_pages, "n_unchanged", n_unchanged)

            last_ws_count = ws_pages

    def generate_images(self, output_log: str, result_dir: str):
        kill_iok()
        run_iok(output_log)

        if self.s3:
            minio_helper.start_minio_server()

        # take initial snapshot
        self.snapshot_shelf(output_log, result_dir)
        # dedupe shared pages
        self.build_itree(output_log)

        # generate access trace
        self.userspace_restore_shelf(
            f"{output_log}_build_ord", result_dir, trace=True, cold=True
        )
        self.add_access_trace(output_log, itrees=False)
        self.add_access_trace(output_log)

        if jifpager_installed():
            self.do_kernel_trace(output_log, result_dir)

        if self.s3:
            minio_helper.kill_minio_server()

    def userspace_restore_shelf(
        self,
        output_log: str,
        result_dir: str,
        trace: bool = False,
        itrees: bool = False,
        reorder: bool = False,
        cold: bool = False,
        ord: bool = False,
    ):
        def construct_jif_fname(self, itrees: bool, reorder: bool) -> str:
            fname = self.snapshot_prefix()
            if itrees:
                fname += "_itrees"
            if ord or reorder:
                fname += "_ord"
            if reorder:
                fname += "_reorder"

            fname += ".jif"
            return fname

        junction_args = f"--function_arg '{self.args}' --function_name {self.id()}"
        prefix = self.snapshot_prefix()
        mem_flags = (
            f"--stackswitch --mem-trace --mem-trace-out {prefix}.ord" if trace else ""
        )

        jif_fname = construct_jif_fname(self, itrees, reorder)
        if cold:
            dropcache()

        self.run(
            f"{junction_args} {mem_flags} {chroot_args()} --jif -r",
            f"{prefix}.jm {jif_fname}",
            f"{output_log}_jif",
            result_dir,
        )

    def jifpager_restore_shelf(
        self,
        output_log: str,
        result_dir: str,
        prefault: bool = False,
        cold: bool = False,
        minor_prefault: bool = False,
        use_page_pool: bool = False,
        reorder: bool = True,
        trace: bool = False,
        cow: bool = False,
        parallel: bool = False,
        prefetch_direct: bool = True,
    ):
        config_jifpager(
            prefault=prefault,
            minor_prefault=minor_prefault,
            use_page_pool=use_page_pool,
            trace=trace,
            pre_cow=cow,
            parallel=parallel,
            prefetch_direct=prefetch_direct,
        )

        if cold:
            dropcache()

        suffix = "_reorder" if reorder else ""

        if self.s3:
            minio_helper.start_minio_server()

        restore_args = self.args
        junction_args = f"--function_arg '{restore_args}' --function_name {self.id()}"
        prefix = self.snapshot_prefix()

        self.run(
            f"{chroot_args()} {junction_args} --jif -rk",
            f"{prefix}.jm {prefix}_itrees_ord{suffix}.jif",
            f"{output_log}_itrees_jif_k",
            result_dir,
        )

        stats = run("sudo cat /sys/kernel/debug/jifpager/stats")
        stats = json.loads(stats)
        print(dict(stats))

        stats["prefault"] = prefault
        stats["cold"] = cold
        stats["key"] = self.id()
        with open(f"{output_log}_itrees_jif_k_kstats", "a") as f:
            f.write(json.dumps(stats))
            f.write("\n")

    def restore_image(self, output_log: str, result_dir: str):
        kill_iok()
        run_iok(output_log)

        if self.s3:
            minio_helper.start_minio_server()

        if jifpager_installed():
            self.jifpager_restore_shelf(
                output_log,
                result_dir,
                prefault=True,
                cold=True,
                minor_prefault=True,
                use_page_pool=True,
                cow=True,
                parallel=True,
                prefetch_direct=True,
            )

        if self.s3:
            minio_helper.kill_minio_server()


class PyFBenchTest(SpiceTest):
    def __init__(self, name: str, s3=False):
        super().__init__(
            "python",
            name,
            f"{BIN_DIR}/venv/bin/python3 -u {FUNCTIONS}/python/run.py {name}",
            FUNCTION_ARGS[name],
            s3=s3,
        )


class JavaFBenchTest(SpiceTest):
    def __init__(self, name: str, s3=False):
        runner = f"{FUNCTIONS}/java/runner/"
        func = f"{FUNCTIONS}/java/{name}/"

        runner_libs = open(f"{runner}/deps.out").readline()
        func_libs = open(f"{func}/deps.out").readline()

        class_name = os.listdir(f"{FUNCTIONS}/java/{name}/build/classes/java/main")
        print(class_name)
        assert len(class_name) == 1, "Function must be a single .class file!"
        class_name = class_name[0].split(".")[0]
        libs = (
            f"{runner_libs}:{func_libs}:{FUNCTIONS}/java/{name}/build/classes/java/main"
        )
        java_lib_path = (
            f"{BIN_DIR}/java/include:{BIN_DIR}/java/include/linux:{FUNCTIONS}"
        )
        cmd = f"{BIN_DIR}/java/bin/java -Djava.library.path={java_lib_path} -cp {libs} Runner {class_name}"

        super().__init__(
            "java",
            name,
            cmd,
            FUNCTION_ARGS[name],
            s3=s3,
        )


class NodeFBenchTest(SpiceTest):
    def __init__(self, name: str, s3=False):
        super().__init__(
            "node",
            name,
            f"{NODE_BIN} --expose-gc --no-flush-bytecode {FUNCTIONS}/node/run.js {name}",
            FUNCTION_ARGS[name],
            s3=s3,
            env=f"NODE_PATH={NODE_PATH}",
        )

    def run(self, junction_args, cmd, log, result_dir):
        super().run(f"--ld_path {BIN_DIR}/lib {junction_args}", cmd, log, result_dir)


TESTS = [
    PyFBenchTest("helloworld"),
    PyFBenchTest("chameleon"),
    PyFBenchTest("pyaes"),
    PyFBenchTest("rnn_serving"),
    PyFBenchTest("lr_serving"),
    PyFBenchTest("cnn_serving"),
    PyFBenchTest("image_rotate_s3", s3=True),
    PyFBenchTest("json_serdes_s3", s3=True),
    PyFBenchTest("lr_training_s3", s3=True),
    PyFBenchTest("video_processing_s3", s3=True),
    JavaFBenchTest("matmul"),
    JavaFBenchTest("image_rotate_s3", s3=True),
    NodeFBenchTest("json_serdes_s3", s3=True),
    NodeFBenchTest("image_rotate_s3", s3=True),
]
