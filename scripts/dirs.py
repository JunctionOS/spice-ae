import os

SCRIPT_DIR = os.path.split(os.path.realpath(__file__))[0]
ROOT_DIR = os.path.split(SCRIPT_DIR)[0]
BIN_DIR = f"{ROOT_DIR}/bin"
FUNCTIONS = f"{ROOT_DIR}/functions"
FAASNAP_DIR = f"{ROOT_DIR}/faasnap"

SNAPSHOT_DIR = os.environ.get("SNAPSHOT_DIR", "/tmp")

_faasnap_default = (
    f"{SNAPSHOT_DIR}/faasnap"
    if "SNAPSHOT_DIR" in os.environ
    else f"{FAASNAP_DIR}/snapshots"
)
FAASNAP_SNAPSHOTS = os.environ.get("FAASNAP_SNAPSHOTS", _faasnap_default)
FAASNAP_LINUX = f"{BIN_DIR}/faasnap-linux.bin"
FAASNAP_ROOTFS = f"{FAASNAP_DIR}/rootfs/debian-rootfs.ext4"
FAASNAP_FC = f"{BIN_DIR}/faasnap-fc"
CHROOT_DIR = f"{ROOT_DIR}/chroot"
MINIO_DATA_PATH = f"{ROOT_DIR}/minio_data"
PATH_TO_FBENCH = f"{ROOT_DIR}/functions/data/"
RESULT_DIR = f"{ROOT_DIR}/results"
RESULT_LINK = f"{ROOT_DIR}/results/run.recent"
JUNCTION_DIR = f"{ROOT_DIR}/junction"
CALADAN_DIR = f"{JUNCTION_DIR}/lib/caladan"
JRUN = f"{JUNCTION_DIR}/build/junction/junction_run"
JIFTOOL = f"{ROOT_DIR}/jiftools/target/release/jiftool"
READJIF = f"{ROOT_DIR}/jiftools/target/release/readjif"
JINSTALL = f"{JUNCTION_DIR}/install"
NODE_BIN = f"{ROOT_DIR}/bin/bin/node"
NODE_PATH = (
    f"{ROOT_DIR}/bin/node_modules:{ROOT_DIR}/bin/node_modules_addon:{FUNCTIONS}/node"
)
CRIU = f"{ROOT_DIR}/criu/criu/criu"
BLOCK_IO_URING = f"{ROOT_DIR}/criu/block_io_uring.so"
