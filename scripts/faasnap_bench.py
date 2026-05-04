#!/usr/bin/env python3

import json
import os
import subprocess
import time

from args import ARGS
from dirs import (
    FAASNAP_DIR,
    FAASNAP_FC,
    FAASNAP_LINUX,
    FAASNAP_ROOTFS,
    FAASNAP_SNAPSHOTS,
    RESULT_DIR,
)
from faasnap_tests import TESTS
from func_args import FUNCTION_ARGS
from minio_helper import start_minio_server
from test import compile_tests
from util import run


def build_faasnap_config(tests):
    f = open(f"{FAASNAP_DIR}/test-2inputs.json")
    config = json.load(f)

    config["setting"] = []
    if ARGS.do_faasnap:
        config["setting"].append("faasnap")
    if ARGS.do_reap:
        config["setting"].append("reap")
    config["function"] = []
    config["functions"] = {}

    for test in tests:
        config["function"].append(test.id())
        fargs = json.loads(FUNCTION_ARGS[test.name])
        fargs["disable_sanpage"] = False
        alt_args = fargs

        if test.s3:
            fargs["minio_addr"] = "10.1.1.1:9000"
            alt_args["minio_addr"] = "10.1.1.1:9000"

        fargs["function"] = test.name
        alt_args["function"] = test.name
        fargs = json.dumps(fargs)
        alt_args = json.dumps(alt_args)

        config["functions"][test.id()] = {}
        config["functions"][test.id()]["lang"] = test.lang
        config["functions"][test.id()]["id"] = test.id()
        config["functions"][test.id()]["name"] = test.name
        config["functions"][test.id()]["image"] = "debian"
        config["functions"][test.id()]["kernel"] = "sanpage"
        config["functions"][test.id()]["params"] = [fargs, alt_args]

    INTERVAL_THRESH = 32

    config["faasnap"]["log_level"] = "Info"
    config["faasnap"]["base_path"] = FAASNAP_SNAPSHOTS
    config["faasnap"]["kernels"]["sanpage"] = FAASNAP_LINUX
    config["faasnap"]["kernels"]["v4.14"] = FAASNAP_LINUX
    config["faasnap"]["images"]["debian"] = FAASNAP_ROOTFS
    config["faasnap"]["executables"]["vanilla"] = FAASNAP_FC
    config["faasnap"]["executables"]["uffd"] = FAASNAP_FC
    config["home_dir"] = FAASNAP_DIR
    config["host"] = "http://127.0.0.1:8080"
    config["trace_api"] = "http://127.0.0.1:9411/api/v2/trace"
    config["test_dir"] = FAASNAP_SNAPSHOTS
    config["vcpu"] = 1
    config["memSize"] = 1024
    config["settings"]["faasnap"]["invocation"]["ws_single_read"] = False
    config["settings"]["faasnap"]["invocation"]["prefetch"] = True

    config["settings"]["faasnap"]["patch_mincore"]["interval_threshold"] = (
        INTERVAL_THRESH
    )
    config["settings"]["faasnap"]["record_regions"]["interval_threshold"] = (
        INTERVAL_THRESH
    )

    config["delay_record"] = False
    config["snapshot_only"] = ARGS.snapshot_only
    config["restore_only"] = ARGS.restore_only

    new_config = open(f"{FAASNAP_DIR}/config.json", "w")
    json.dump(config, new_config, indent=4)


def main(tests):
    os.makedirs(FAASNAP_SNAPSHOTS, exist_ok=True)
    build_faasnap_config(tests)
    curdir = os.getcwd()

    run("sudo rmmod kvm-intel; sudo rmmod kvm")
    run("sudo modprobe kvm nx_huge_pages=never; sudo modprobe kvm-intel")

    os.chdir(FAASNAP_DIR)
    run("bash ./clean.sh")
    run("bash ./prep.sh")

    start_minio_server(ip="10.1.1.1")
    time.sleep(1)

    env = os.environ.copy()
    env["RESULT_DIR"] = RESULT_DIR
    cmd = "sudo -E ./test.py config.json".split(" ")
    subprocess.run(cmd, env=env)
    os.chdir(curdir)

    run(f"sudo chown -R {os.getuid()}:{os.getgid()} {RESULT_DIR}")


if __name__ == "__main__":
    tests = compile_tests(TESTS)
    main(tests)
