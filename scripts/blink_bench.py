#!/usr/bin/env python3

import atexit
import os

from args import ARGS
from blink_tests import TESTS, kill_iok
from dirs import BLINK_SNAPSHOTS, REEXEC_DIR, SNAPSHOT_DIR
from test import compile_tests
from util import (
    get_result_dir,
    is_running_as_root,
    jifpager_installed,
    run,
    setup_chroot,
)


def run_microbenchmark(result_dir: str, tests):
    for app in tests:
        app.restore_image(f"{result_dir}/restore_images", result_dir)


def generate_plots(result_dir: str):
    pass
    # data = {}
    # data["junction"] = parse_junction_logs(result_dir)
    # plot_microbenchmarks(result_dir, data)


def main(tests):
    result_dir = get_result_dir(name="blink")
    if ARGS.redo_snapshot:
        for app in tests:
            app.generate_images(f"{result_dir}/generate_images", result_dir)

    run_microbenchmark(result_dir, tests)
    generate_plots(result_dir)


if __name__ == "__main__":
    if is_running_as_root():
        print("re-run without root")
        exit(-1)

    atexit.register(kill_iok)
    tests = compile_tests(TESTS)

    for d in (SNAPSHOT_DIR, BLINK_SNAPSHOTS):
        try:
            os.makedirs(d, exist_ok=True)
        except PermissionError:
            print(
                f"!!!!!! cannot create {d} without root; create it or fix perms !!!!!!"
            )
            exit(1)

    run(f"cd {REEXEC_DIR}; ./install.sh; cd ..")
    run(f"echo 256 | sudo tee /sys/kernel/jifpager/prefetch_sync_batch")

    setup_chroot()
    main(tests)
