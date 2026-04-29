#!/usr/bin/env python3

import time

import minio_helper
from args import ARGS
from criu_test import TESTS
from test import compile_tests
from util import get_result_dir, is_running_as_root, setup_chroot


def run_all(tests, result_dir):
    for test in tests:
        if ARGS.criu_eager:
            pid = test.snapshot(result_dir)
            test.restore(pid, result_dir, lazy_pages=not ARGS.no_lazy_pages)
            time.sleep(1)

        if ARGS.criu_mmap_only:
            pid = test.snapshot(result_dir, lazy_pages=False, mmap_only=True)
            test.restore(pid, result_dir, lazy_pages=False, mmap_only=True)
            time.sleep(1)

        if ARGS.criu_no_cow:
            pid = test.snapshot(
                result_dir, lazy_pages=False, mmap_only=True, no_cow=True
            )
            test.restore(pid, result_dir, lazy_pages=False, mmap_only=True, no_cow=True)

        if ARGS.criu_strace:
            pid = test.snapshot(
                result_dir, lazy_pages=False, mmap_only=True, strace=True
            )
            test.restore(pid, result_dir, lazy_pages=False, mmap_only=True, strace=True)


def main(tests, name="criu"):
    minio_helper.start_minio_server(ip="localhost")
    result_dir = get_result_dir(name=name)
    run_all(tests, result_dir)


if __name__ == "__main__":
    if is_running_as_root():
        print("re-run without root")
        exit(-1)

    tests = compile_tests(TESTS)
    setup_chroot()
    main(tests)
