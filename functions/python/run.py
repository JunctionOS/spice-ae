import ctypes
import gc
import importlib
import json
import sys

# try:

# except ImportError:
# pass

libc = ctypes.CDLL(None)


def snapshot_prepare():
    sys.stdout.flush()
    for _ in range(3):
        gc.collect()
    libc.malloc_trim(0)


def run(handler):
    with open("/serverless/chan0", "r+") as f:
        while True:
            cmd = f.readline().strip()
            if cmd == "SNAPSHOT_PREPARE":
                snapshot_prepare()
                f.write("OK")
                continue
            json_req = json.loads(cmd)
            f.write(str(handler(json_req)))


if __name__ == "__main__":
    name = sys.argv[1]
    prog = name
    if name == "chameleon" or name == "pyaes":
        prog = name + "1"

    handler = importlib.import_module(f"{prog}.{prog}").function_handler
    run(handler)
