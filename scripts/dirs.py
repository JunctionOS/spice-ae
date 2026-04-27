import os

SCRIPT_DIR = os.path.split(os.path.realpath(__file__))[0]
ROOT_DIR = os.path.split(SCRIPT_DIR)[0]
BIN_DIR = f"{ROOT_DIR}/bin"
FUNCTIONS = f"{ROOT_DIR}/functions"
FAASNAP_DIR = f"{ROOT_DIR}/faasnap"
FAASNAP_SNAPSHOTS = f"{FAASNAP_DIR}/snapshots"
FAASNAP_LINUX = f"{BIN_DIR}/faasnap-linux.bin"
FAASNAP_ROOTFS = f"{FAASNAP_DIR}/rootfs/debian-rootfs.ext4"
FAASNAP_FC = f"{BIN_DIR}/faasnap-fc"
CHROOT_DIR = f"{ROOT_DIR}/chroot"
MINIO_DATA_PATH = f"{ROOT_DIR}/minio_data"
PATH_TO_FBENCH = f"{ROOT_DIR}/functions/data/"
RESULT_DIR = f"{ROOT_DIR}/results"
RESULT_LINK = f"{ROOT_DIR}/results/run.recent"
