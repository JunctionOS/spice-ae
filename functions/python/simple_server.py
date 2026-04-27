#!/usr/bin/python3

import sys
import os
import socket
import subprocess
import json
import importlib
import rdtsc

sys.path.append("/usr/local/lib/python3.7/site-packages")
import traceback
# sched_ret = None
#
param = os.sched_param(os.sched_get_priority_max(os.SCHED_FIFO))
sched_ret = os.sched_setscheduler(0, os.SCHED_FIFO, param)

def run(cmd, quiet=False):
    if not quiet:
        print(cmd)
        sys.stdout.flush()

    return subprocess.check_output(cmd, shell=True)

def serve():
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock.bind(('0.0.0.0', 5000))
    sock.listen()
    func_args = None
    while True:
        conn, addr = sock.accept()
        data = conn.recv(1024)
        try:
            if len(data) > 1:
                func_args = json.loads(data.decode('utf-8'))

            func_name = func_args['function']
            if func_name == "chameleon" or func_name == "pyaes":
                func_name = func_name + "1"

            if func_args['disable_sanpage']:
                run("echo 8 > /proc/sys/vm/drop_caches")

            handler = importlib.import_module(f"{func_name}.{func_name}").function_handler
            ret = handler(func_args)

            func_args['end_tsc'] = rdtsc.get_cycles()
            ret = json.dumps(func_args)

            conn.send(str(ret).encode('utf-8'))
        except Exception as e:
            tb = traceback.format_exc()
            conn.send(str(tb).encode('utf-8'))

        conn.close()

serve()
