import os
import subprocess
import sys


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
