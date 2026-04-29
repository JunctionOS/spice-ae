import json
import os
import subprocess
import sys
import time

from dirs import (
    BIN_DIR,
    BLOCK_IO_URING,
    CRIU,
    FUNCTIONS,
    NODE_PATH,
    ROOT_DIR,
)
from func_args import FUNCTION_ARGS
from test import Test
from util import dropcache, run, run_async

sys.path.append(f"{ROOT_DIR}/bin/venv/lib/python3.12/site-packages")


class CRIUTest(Test):
    def __init__(self, lang: str, name: str, cmd: str, s3=False, env=None):
        arg_map = FUNCTION_ARGS[name]
        if s3:
            d = json.loads(arg_map)
            d["minio_addr"] = f"localhost:9000"
            arg_map = json.dumps(d)

        self.cmd_env = env if env is not None else os.environ.copy()
        super().__init__(lang, name, cmd, arg_map, s3=s3)

    def _suffix(self, lazy_pages, mmap_only, no_cow, strace):
        log = ""
        if lazy_pages:
            log += "_lazy_pages"
        if mmap_only:
            log += "_mmap_only"
        if no_cow:
            log += "_no_cow"
        if strace:
            log += "_strace"
        return log

    def run(
        self, result_dir, lazy_pages=False, mmap_only=False, no_cow=False, strace=False
    ):
        run(f"mkdir -p {result_dir}/images")
        run(f"mkdir -p {result_dir}/output")

        log = self._suffix(lazy_pages, mmap_only, no_cow, strace)
        stdout_path = f"{result_dir}/output/{self.id()}-{log}.output"
        f = open(stdout_path, "w")

        cmd = self.cmd.split(" ")
        cmd.append(self.args)
        env = dict(self.cmd_env)
        env["LD_PRELOAD"] = BLOCK_IO_URING
        proc = subprocess.Popen(cmd, stdout=f, stderr=f, env=env)
        pid = proc.pid
        time.sleep(1)

        while os.system(f"grep -q looping {stdout_path}") != 0:
            if proc.poll() is not None:
                raise ValueError("proc failed")
            time.sleep(0.1)

        time.sleep(1)
        return pid

    def snapshot(
        self, result_dir, lazy_pages=False, mmap_only=False, no_cow=False, strace=False
    ):
        pid = self.run(
            result_dir,
            lazy_pages=lazy_pages,
            mmap_only=mmap_only,
            no_cow=no_cow,
            strace=strace,
        )
        image_dir = f"{result_dir}/images/{self.id()}"
        run(f"mkdir -p {image_dir}")
        run(
            f"sudo -E {CRIU} dump --tcp-established -t {pid} -vvvv "
            f"-o snapshot.log -D {image_dir} --shell-job"
        )
        print("sleeping for 15 seconds")
        dropcache()
        time.sleep(15)
        return pid

    def restore(
        self,
        pid,
        result_dir,
        lazy_pages=False,
        mmap_only=False,
        no_cow=False,
        strace=False,
    ):
        image_dir = f"{result_dir}/images/{self.id()}"
        pidfile = f"{image_dir}/script_pidfile"
        run(f"rm -rf {pidfile}")

        dropcache()
        time.sleep(1)

        lazy_pages_arg = ""
        if lazy_pages:
            run_async(f"sudo -E {CRIU} lazy-pages -D {image_dir} -o lazy_page.log")
            lazy_pages_arg = " --lazy-pages"
            time.sleep(2)

        no_cow_arg = " --no-cow" if no_cow else ""
        mmap_only_arg = " --mmap-only" if mmap_only else ""
        log = self._suffix(lazy_pages, mmap_only, no_cow, strace)

        strace_cmd = ""
        if strace:
            strace_out = f"{result_dir}/output/{self.id()}-{log}.strace"
            strace_cmd = f" strace -e trace=!write -Cfo {strace_out}"

        cmd = (
            f"sudo -E{strace_cmd} {CRIU} restore -o restore{log}.log "
            f"-D {image_dir} --tcp-established --pidfile {pidfile}"
            f"{mmap_only_arg}{no_cow_arg} --shell-job{lazy_pages_arg}"
        )

        print(cmd)
        cmd = cmd.split(" ")
        start_ns = time.time_ns()
        proc = subprocess.Popen(cmd)
        proc.wait()
        end_ns = time.time_ns()
        print(end_ns - start_ns)
        time.sleep(1)

        stdout_path = f"{result_dir}/output/{self.id()}-{log}.output"
        run(f"echo 'restore start ns: {start_ns}' >> {stdout_path}")
        run(f"echo 'restore end ns: {end_ns}' >> {stdout_path}")

        run("sudo killall criu 2> /dev/null; true")

        run(f"sudo chmod 444 {result_dir}/images/{self.id()}/restore{log}.log")
        run(
            f"cp {result_dir}/images/{self.id()}/restore{log}.log "
            f"{result_dir}/output/{self.id()}_restore{log}.log"
        )


class CRIUPythonTest(CRIUTest):
    def __init__(self, name: str, s3=False):
        env = os.environ.copy()
        super().__init__(
            "python",
            name,
            f"{BIN_DIR}/venv/bin/python3 {FUNCTIONS}/python/criu_runner.py {name}",
            s3=s3,
            env=env,
        )


class CRIUNodeTest(CRIUTest):
    def __init__(self, name: str, s3=False):
        env = os.environ.copy()
        env["NODE_PATH"] = NODE_PATH
        super().__init__(
            "node",
            name,
            f"/usr/bin/node {FUNCTIONS}/node/criu_runner.mjs {name}",
            s3=s3,
            env=env,
        )


class CRIUJavaTest(CRIUTest):
    def __init__(self, name: str, s3=False):
        runner = f"{FUNCTIONS}/java/criu_runner/"
        func = f"{FUNCTIONS}/java/{name}"

        runner_libs = open(f"{runner}/deps.out").readline()
        func_libs = open(f"{func}/deps.out").readline()

        class_name = os.listdir(f"{FUNCTIONS}/java/{name}/build/classes/java/main")
        assert len(class_name) == 1, "Function must be a single .class file!"
        class_name = class_name[0].split(".")[0]

        libs = (
            f"{runner_libs}:{func_libs}:{FUNCTIONS}/java/{name}/build/classes/java/main"
        )
        java_lib_path = (
            f"{BIN_DIR}/java/include:{BIN_DIR}/java/include/linux:"
            f"{FUNCTIONS}/java/criu_runner/build/libs/"
        )
        cmd = (
            f"{BIN_DIR}/java/bin/java -Djava.library.path={java_lib_path} "
            f"-cp {libs} CRIURunner {class_name}"
        )

        super().__init__("java", name, cmd, s3=s3, env=os.environ.copy())


TESTS = [
    CRIUPythonTest("helloworld"),
    CRIUPythonTest("chameleon"),
    CRIUPythonTest("pyaes"),
    CRIUPythonTest("image_rotate_s3", s3=True),
    CRIUPythonTest("json_serdes_s3", s3=True),
    CRIUPythonTest("rnn_serving"),
    CRIUPythonTest("video_processing_s3", s3=True),
    CRIUPythonTest("lr_training_s3", s3=True),
    CRIUPythonTest("lr_serving"),
    CRIUPythonTest("cnn_serving"),
    CRIUNodeTest("image_rotate_s3", s3=True),
    CRIUNodeTest("json_serdes_s3", s3=True),
    CRIUJavaTest("image_rotate_s3", s3=True),
    CRIUJavaTest("matmul"),
]
