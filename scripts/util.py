import atexit
import os
import stat
import subprocess
import sys
import time
from datetime import datetime

from args import ARGS
from dirs import (
    BIN_DIR,
    BLINK_SNAPSHOTS,
    CHROOT_DIR,
    FUNCTIONS,
    JINSTALL,
    JRUN,
    RESULT_DIR,
    SCRIPT_DIR,
    SNAPSHOT_DIR,
)


def is_running_as_root():
    return os.geteuid() == 0


def run(cmd):
    print(cmd)
    sys.stdout.flush()
    p = subprocess.Popen(cmd, shell=True, stdin=subprocess.PIPE, stdout=subprocess.PIPE)
    out, _ = p.communicate()
    return out


def run_async(cmd):
    print(cmd)
    sys.stdout.flush()
    return subprocess.Popen(cmd, shell=True, stdin=subprocess.PIPE)


def dropcache():
    for i in range(3):
        run("echo 3 | sudo tee /proc/sys/vm/drop_caches")
        # if i > 0:
        #     time.sleep(1)

    for i in range(3):
        run(f"cat {JRUN} > /dev/null")


def kill_chroot():
    run(f"{SCRIPT_DIR}/chroot_mount.sh -u || true")
    run(f"sudo rm -f {CHROOT_DIR}/dev/jif_pager")


def jifpager_installed():
    try:
        stat.S_ISCHR(os.stat("/dev/jif_pager").st_mode)
        return True
    except BaseException:
        return False


def setup_chroot():
    if not ARGS.use_chroot:
        return
    run(
        f"sudo mkdir -p {CHROOT_DIR}/{BIN_DIR} {CHROOT_DIR}/{FUNCTIONS} {CHROOT_DIR}/{JINSTALL}"
    )

    if not os.access(SNAPSHOT_DIR, os.R_OK | os.W_OK):
        print(
            f"!!!!!! SNAPSHOT_DIR={SNAPSHOT_DIR} lacking r/w permissions, aborting !!!!!!"
        )
        exit(0)

    os.makedirs(BLINK_SNAPSHOTS, exist_ok=True)
    if not os.access(BLINK_SNAPSHOTS, os.R_OK | os.W_OK):
        print(
            f"!!!!!! BLINK_SNAPSHOTS={BLINK_SNAPSHOTS} lacking r/w permissions, aborting !!!!!!"
        )
        exit(0)

    run(f"touch {BLINK_SNAPSHOTS}/.perm_test")

    # clean old mounts
    kill_chroot()
    print(run(f"{SCRIPT_DIR}/chroot_mount.sh").decode("utf-8"))

    if jifpager_installed():
        st = os.stat("/dev/jif_pager")
        major = os.major(st.st_rdev)
        minor = os.minor(st.st_rdev)

        run(f"sudo mknod -m 666 {CHROOT_DIR}/dev/jif_pager c {major} {minor} || true")

    atexit.register(kill_chroot)


def get_result_dir(name="run"):
    exp_name = f"{name}.{datetime.now().strftime('%Y_%m_%d_%H_%M_%S')}"
    result_dir = f"{RESULT_DIR}/{exp_name}"
    os.system(f"mkdir -p {result_dir}")
    os.system(f"ln -sfn {exp_name} {RESULT_DIR}/{name}.recent")
    return result_dir
