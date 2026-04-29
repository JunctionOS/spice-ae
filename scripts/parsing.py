import json
import os
import re
import subprocess
from collections import defaultdict

import numpy as np

# Single config tag emitted by blink_tests.jifpager_restore_shelf
BLINK_TAG = "itrees_jif_k"

# CRIU run configs in preferred order for e2e plotting
CRIU_CONFIGS = ["lazy_pages", "eager", "mmap_only", "mmap_only_no_cow"]


def get_one_log(log_name: str):
    """Parse a junction restore log, return per-program records."""
    try:
        with open(log_name) as x:
            dat = x.read().splitlines()
    except BaseException:
        return {}

    progs = {}
    prev_restore = None
    thread_map = {}
    function_kthreads = []
    for line in dat:
        if "created thread" in line:
            thread = int(line.split("created thread")[-1].split(" ")[1])
            ktid = int(line.split("tid: ")[-1].split("]")[0])
            thread_map[ktid] = thread
        if "FUNCTION KTHREAD" in line:
            thread = int(line.split("FUNCTION KTHREAD = ")[-1])
            if thread not in function_kthreads:
                function_kthreads.append(thread)

        if "DATA  " not in line:
            if "restore time" in line:
                prev_restore = line
            continue

        lx = line.split("DATA  ")[-1].strip()
        xx = json.loads(lx)
        if "generate" not in log_name:
            assert xx["program"] not in progs, f"{xx['program']} already in {progs}"
        xx["thread_map"] = thread_map
        xx["function_kthreads"] = function_kthreads
        if prev_restore:
            line = prev_restore.split("restore time")[1].split()
            xx["metadata_restore"] = int(line[2])
            xx["data_restore"] = int(line[4])
            xx["fs_restore"] = int(line[6])
            prev_restore = None
        progs[xx["program"]] = xx

    return progs


def getstats(d):
    return {
        "cold_first_iter": d.get("first_iter"),
        "data_restore": d.get("data_restore"),
        "prefetch": d.get("prefetch"),
        "warm_iter": np.min(d["times"]),
        "uncached_iter": np.min(d["times"][1:5]),
        "metadata_restore": d.get("metadata_restore"),
        "fs_restore": d.get("fs_restore"),
        "thread_map": d.get("thread_map"),
        "function_kthreads": d.get("function_kthreads"),
    }


def get_kstats(fname: str, data, exp_n: str):
    try:
        with open(fname, "r") as f:
            for line in f.readlines():
                jx = json.loads(line)
                data[jx["key"]][exp_n]["jifpager_stats_ns"] = jx
    except BaseException:
        pass


def parse_blink_logs(result_dir: str, log_name: str = "restore_images"):
    """Parse blink restore logs. Single config (all optimizations)."""
    out = defaultdict(dict)
    log_path = f"{result_dir}/{log_name}_{BLINK_TAG}"

    for prog, d in get_one_log(log_path).items():
        out[prog][BLINK_TAG] = getstats(d)

    get_kstats(f"{log_path}_kstats", out, BLINK_TAG)
    return out


def _tsc_freq_hz():
    """Return TSC frequency in Hz, or None if it cannot be determined."""
    try:
        out = subprocess.check_output(
            [
                "cpuid",
                "--one-cpu",
            ],
            text=True,
        )
    except (FileNotFoundError, subprocess.CalledProcessError):
        return None

    num = den = art_hz = None
    for line in out.splitlines():
        m = re.search(r"TSC/clock ratio.*=\s*(\d+)\s*/\s*(\d+)", line)
        if m:
            num, den = int(m.group(1)), int(m.group(2))
        m = re.search(r"nominal core crystal clock\s*=\s*(\d+)", line)
        if m:
            art_hz = int(m.group(1))

    if num and den and art_hz:
        return art_hz * num // den
    return None


def _criu_config_name(suffix: str) -> str:
    """Map output suffix (without leading underscore) to a config key."""
    s = suffix.strip("_")
    return s if s else "eager"


_CRIU_TS_RE = re.compile(r"^\(\s*(\d+)\.(\d+)\)")
_CRIU_TSC_RE = re.compile(r"tsc=(\d+)")

# Memory-class events emitted by CRIU's verbose restore log; matched as
# substrings against the full line (after stripping the leading timestamp).
_CRIU_MEMORY_EVENTS = [
    "mmap VMAs",
    "read private VMA content",
    "unmap guard pages",
    "open vmas",
    "find restorer location",
    "unmap CRIU VMAs",
    "mremap VMAs",
    "restore vma mappings",
    "overlay mmap",
    "mprotect VMAs",
]


def _ts_us(line):
    m = _CRIU_TS_RE.match(line)
    if not m:
        return None
    return int(m.group(1)) * 1_000_000 + int(m.group(2))


def _parse_criu_restore_log(path, tsc_hz):
    """Extract init/memory/metadata + reap_zombies_begin from CRIU verbose log."""
    if not os.path.exists(path) or tsc_hz is None:
        return None

    def tsc_to_us(tsc):
        return tsc * 1e6 / tsc_hz

    setup_begin_tsc = setup_end_tsc = None
    os_begin_tsc = os_end_tsc = None
    reap_begin_tsc = None

    # For each memory event, sum begin/end pairs (us based on log timestamps).
    pending = {}  # event_name -> begin_ts_us
    memory_us = 0.0

    with open(path, errors="replace") as f:
        for raw in f:
            if "bench |" not in raw:
                continue

            if "restore setup tsc=" in raw:
                m = _CRIU_TSC_RE.search(raw)
                if m:
                    if "begin" in raw:
                        setup_begin_tsc = int(m.group(1))
                    elif "end" in raw:
                        setup_end_tsc = int(m.group(1))
                continue

            if "OS state tsc=" in raw:
                m = _CRIU_TSC_RE.search(raw)
                if m:
                    if "begin" in raw:
                        os_begin_tsc = int(m.group(1))
                    elif "end" in raw:
                        os_end_tsc = int(m.group(1))
                continue

            if "reap zombies tsc=" in raw and "begin" in raw:
                m = _CRIU_TSC_RE.search(raw)
                if m:
                    reap_begin_tsc = int(m.group(1))
                continue

            for ev in _CRIU_MEMORY_EVENTS:
                if ev not in raw:
                    continue
                ts = _ts_us(raw)
                if ts is None:
                    break
                if "| begin" in raw or raw.rstrip().endswith("begin"):
                    pending[ev] = ts
                elif "| end" in raw or raw.rstrip().endswith("end"):
                    start = pending.pop(ev, None)
                    if start is not None:
                        memory_us += ts - start
                break

    init_us = (
        tsc_to_us(setup_end_tsc - setup_begin_tsc)
        if setup_begin_tsc is not None and setup_end_tsc is not None
        else None
    )
    os_state_us = (
        tsc_to_us(os_end_tsc - os_begin_tsc)
        if os_begin_tsc is not None and os_end_tsc is not None
        else None
    )
    metadata_us = (
        os_state_us - memory_us
        if os_state_us is not None
        else None
    )

    if init_us is None or os_state_us is None:
        restore_us = None
    else:
        restore_us = init_us + os_state_us  # = init + memory + metadata

    return {
        "init_us": init_us,
        "memory_us": memory_us,
        "metadata_us": metadata_us,
        "restore_us": restore_us,
        "reap_begin_tsc": reap_begin_tsc,
    }


def parse_criu_logs(d):
    """Parse CRIU test outputs from {result_dir}/output/.

    Returns: {func_id: {config: {restore_us, post_resume_iter_us,
              cold_first_iter_us, warm_us, init_us, memory_us, metadata_us}}}

    restore_us is taken from CRIU's verbose log: init + memory + metadata.
    post_resume_iter_us is iteration_finish (DATA) - reap_zombies_begin (log).
    """
    out_dir = os.path.join(d, "output")
    if not os.path.isdir(out_dir):
        return {}

    tsc_hz = _tsc_freq_hz()

    def cycles_to_us(cycles):
        if cycles is None or tsc_hz is None:
            return None
        return cycles * 1e6 / tsc_hz

    data = defaultdict(dict)
    for name in sorted(os.listdir(out_dir)):
        if not name.endswith(".output"):
            continue
        base = name[: -len(".output")]
        if "-" not in base:
            continue
        func_id, suffix = base.rsplit("-", 1)
        config = _criu_config_name(suffix)

        cold_cycles = None
        warm_cycles = None
        iter_finish_tsc = None

        with open(os.path.join(out_dir, name)) as f:
            for line in f:
                if line.startswith("DATA"):
                    try:
                        payload = json.loads(line.split("DATA", 1)[1].strip())
                    except (ValueError, IndexError):
                        continue
                    warmups = payload.get("warmup") or []
                    if warmups:
                        warm_cycles = min(warmups)
                    cold = payload.get("cold")
                    if isinstance(cold, list):
                        cold = cold[0] if cold else None
                    cold_cycles = cold
                elif "iteration finish" in line:
                    try:
                        iter_finish_tsc = int(line.rsplit(":", 1)[1])
                    except ValueError:
                        pass

        # Restore log copied to output dir as "{func_id}_restore{suffix}.log"
        # where suffix has the leading underscore (or is empty for eager).
        restore_log = os.path.join(out_dir, f"{func_id}_restore{suffix}.log")
        log_stats = _parse_criu_restore_log(restore_log, tsc_hz) or {}

        post_resume_iter_us = None
        reap_begin_tsc = log_stats.get("reap_begin_tsc")
        if iter_finish_tsc is not None and reap_begin_tsc is not None:
            post_resume_iter_us = (iter_finish_tsc - reap_begin_tsc) * 1e6 / tsc_hz

        entry = {
            "restore_us": log_stats.get("restore_us"),
            "init_us": log_stats.get("init_us"),
            "memory_us": log_stats.get("memory_us"),
            "metadata_us": log_stats.get("metadata_us"),
            "post_resume_iter_us": post_resume_iter_us,
            "cold_first_iter_us": cycles_to_us(cold_cycles),
            "warm_us": cycles_to_us(warm_cycles),
        }
        data[func_id][config] = entry

    return dict(data)


def parse_faasnap_logs(d):
    """Parse FaaSnap/REAP zipkin-style trace logs from result dir."""
    data = {"reap": {}, "faasnap": {}, "faasnap_no_prefetch": {}}
    if not os.path.isdir(d):
        return data

    runs = os.listdir(d)
    for r in runs:
        if "faasnap_" not in r and "reap_" not in r:
            continue

        name_idx = 1
        if "no_prefetch" in r:
            name_idx = 3

        name = "_".join(r.split("_")[name_idx:-1])
        this_data = {}

        run_dir = f"{d}/{r}"
        logs = os.listdir(run_dir)
        mcst_logs = [l for l in logs if "mcst" in l]
        if not mcst_logs:
            continue
        runid = mcst_logs[0].split("-")[0]
        log_file = f"{runid}.json"

        for stats_name in ("fault_stats", "sched_stats", "sched_stats_fifo"):
            path = f"{run_dir}/{stats_name}.json"
            if os.path.exists(path):
                with open(path) as f:
                    this_data[stats_name] = json.load(f)

        fc_log_path = f"{run_dir}/log"
        if os.path.exists(fc_log_path):
            restore_stats = {}
            with open(fc_log_path) as f:
                for line in f:
                    if "done mmaps in" in line:
                        restore_stats["mmap"] = int(line.split(" ")[-1][:-3])
                    if "create vmm took" in line:
                        restore_stats["create_vmm"] = int(line.split(" ")[-1])
                    if "restore kvm took" in line:
                        restore_stats["restore_kvm"] = int(line.split(" ")[-1])
                    if "restore devices took" in line:
                        restore_stats["restore_devices"] = int(line.split(" ")[-1])
                    if "start vcpus took" in line:
                        restore_stats["start_vcpus"] = int(line.split(" ")[-1])
                    if "restore vcpus took" in line:
                        restore_stats["restore_vcpus"] = int(line.split(" ")[-1])
                    if "install seccomp took" in line:
                        restore_stats["install_seccomp"] = int(line.split(" ")[-1])
            this_data["restore_stats"] = restore_stats

        trace_path = f"{run_dir}/{log_file}"
        if os.path.exists(trace_path):
            with open(trace_path) as f:
                trace_log = json.load(f)
            for trace in trace_log:
                tname = trace.get("name", "")
                dur = trace.get("duration")
                if tname == "vm_dial":
                    this_data["vm_dial"] = dur
                elif tname == "request_load_snapshot":
                    this_data["request_load_snapshot"] = dur
                elif tname == "vm_resume":
                    this_data["vm_resume"] = dur
                elif tname == "load_ws_file":
                    this_data["load_ws"] = dur
                elif tname == "installworkingsetpages":
                    this_data["install_ws"] = dur
                elif tname == "reap.activate":
                    this_data["fetch_state"] = dur
                elif "invoke" in tname:
                    this_data["invoke"] = dur
                elif tname == "/invocations":
                    this_data["e2e"] = dur

        if "reap" in r:
            data["reap"][name] = this_data
        elif "no_prefetch" in r:
            data["faasnap_no_prefetch"][name] = this_data
        else:
            data["faasnap"][name] = this_data

    return data
