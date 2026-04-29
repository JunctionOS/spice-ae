#!/usr/bin/python3
import ctypes
import importlib
import json
import os
import sys
import time

import rdtsc

libc = ctypes.CDLL(None)

parent = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
sys.path.append(parent)

syscall = libc.syscall

WARMUP_ITERS = 10

prog = sys.argv[1]
json_string = sys.argv[2]
json_req = json.loads(json_string)

if prog == "chameleon" or prog == "pyaes":
    prog += "1"

main = importlib.import_module(f"{prog}.{prog}").function_handler

warmups = []
for _ in range(0, WARMUP_ITERS):
    start = rdtsc.get_cycles()
    print(main(json_req))
    end = rdtsc.get_cycles()
    warmups.append((end - start))

sys.stdout.write("looping\n")
sys.stdout.flush()

now = time.time()
while time.time() - now < 10:
    pass

sys.stdout.write("done looping\n")
sys.stdout.flush()

start = rdtsc.get_cycles()
main(json_req)
end = rdtsc.get_cycles()
cold = end - start

print(
    "DATA ",
    json.dumps({"warmup": warmups, "cold": cold, "program": sys.argv[1]}),
)
print(f"iteration finish: {rdtsc.get_cycles()}")
sys.stdout.flush()
syscall(231, 0)
