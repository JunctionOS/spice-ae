import atexit
import getpass
import os
import time

from args import ARGS
from dirs import BIN_DIR, CHROOT_DIR, MINIO_DATA_PATH, PATH_TO_FBENCH
from minio import Minio
from util import run, run_async

MINIO = f"{BIN_DIR}/minio"
MINIO_BUCKET = "mybucket"
MINIO_MASK = "255.255.0.0"
MINIO_IP = "192.168.120.1"


def kill_minio_server():
    run("sudo pkill junction_run || true")
    run("sudo pkill minio || true")
    time.sleep(1)

    path = f"{CHROOT_DIR}/{MINIO_DATA_PATH}" if ARGS.use_chroot else MINIO_DATA_PATH
    run(f"sudo rm -rf {path}")


atexit.register(kill_minio_server)


def prefix_fbench(fname: str):
    return PATH_TO_FBENCH + fname


OBJECTS = [
    prefix_fbench("images/img2.jpeg"),
    prefix_fbench("images/img3.jpeg"),
    prefix_fbench("images/image.jpg"),
    prefix_fbench("json/1.json"),
    prefix_fbench("json/2.json"),
    prefix_fbench("ml/dataset.csv"),
    prefix_fbench("ml/dataset2.csv"),
    prefix_fbench("video/vid1.mp4"),
    prefix_fbench("video/vid2.mp4"),
]


def setup_minio(output_log: str):
    run(f"mkdir -p {MINIO_DATA_PATH}")

    path = f"{CHROOT_DIR}/{MINIO_DATA_PATH}" if ARGS.use_chroot else MINIO_DATA_PATH
    minio = run_async(f"sudo -E {MINIO} server {path} >> {output_log} 2>&1")
    time.sleep(1)

    client = Minio(
        "localhost:9000", access_key="minioadmin", secret_key="minioadmin", secure=False
    )

    if not client.bucket_exists(MINIO_BUCKET):
        client.make_bucket(MINIO_BUCKET)

    for obj in OBJECTS:
        client.fput_object(MINIO_BUCKET, os.path.basename(obj), obj)

    run("sudo pkill minio || true")
    run("sudo pkill minio || true")
    run("sudo pkill minio || true")

    minio.wait()


def start_minio_server(ip=None):
    minio_ip = MINIO_IP
    if ip:
        minio_ip = ip
    kill_minio_server()
    user = getpass.getuser()
    setup_minio(f"/tmp/minio_{user}.log")
    data_path = (
        f"{CHROOT_DIR}/{MINIO_DATA_PATH}" if ARGS.use_chroot else MINIO_DATA_PATH
    )
    run_async(f"sudo {MINIO} server {data_path} --address '{minio_ip}:9000'")
    time.sleep(1)
