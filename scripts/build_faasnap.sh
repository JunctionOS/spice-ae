#!/bin/bash

SCRIPT_DIR=$(dirname $(readlink -f $0))
ROOT_DIR=${SCRIPT_DIR}/../
FUNCTIONS_DIR=${ROOT_DIR}/functions/
FAASNAP_DIR=${ROOT_DIR}/faasnap
FAASNAP_LINUX_DIR=${ROOT_DIR}/faasnap-kernel
FAASNAP_FC_DIR=${ROOT_DIR}/firecracker
BIN_DIR=${ROOT_DIR}/bin/
GUEST_DIR=${ROOT_DIR}/faasnap/rootfs/guest

FAASNAP_ROOTFS=${FAASNAP_ROOTFS:-${FAASNAP_DIR}/rootfs}

set -x

mkdir -p ${BIN_DIR}

# build faasnap firecracker
pushd $FAASNAP_FC_DIR
tools/devtool build --release
cp ./build/cargo_target/x86_64-unknown-linux-musl/release/firecracker $BIN_DIR/faasnap-fc
popd

# build faasnap daemon
pushd $FAASNAP_DIR
go get -u ./...
go build ./cmd/faasnap-server/main.go

# build rootfs
mkdir -p ${GUEST_DIR}/node
cp ${FUNCTIONS_DIR}/node/*.js ${GUEST_DIR}/node
cp -r ${BIN_DIR}/node_modules ${GUEST_DIR}/node
cp -r ${BIN_DIR}/node_modules_addon ${GUEST_DIR}/node
cp -r ${FUNCTIONS_DIR}/python/* ${GUEST_DIR}/python
cp -r ${FUNCTIONS_DIR}/java/* ${GUEST_DIR}/java
cp -r ${FUNCTIONS_DIR}/data ${GUEST_DIR}/

sudo mkdir -p ${FAASNAP_ROOTFS}
sudo chown ${USER} ${FAASNAP_ROOTFS}

make -C ./rootfs debian-rootfs.ext4 OUTDIR=${FAASNAP_ROOTFS}

sudo mount ${FAASNAP_ROOTFS}/debian-rootfs.ext4 ${FAASNAP_ROOTFS}/mountpoint
sudo mkdir -p ${FAASNAP_ROOTFS}/mountpoint/$FUNCTIONS_DIR
sudo cp -r $FUNCTIONS_DIR/data ${FAASNAP_ROOTFS}/mountpoint/$FUNCTIONS_DIR/
sudo umount ${FAASNAP_ROOTFS}/mountpoint

popd

# build faasnap guest kernel
pushd $FAASNAP_LINUX_DIR
docker run --rm -v "$(pwd)":/workspace -w /workspace ubuntu:18.04 /bin/bash -c "
  set -x
  apt-get update && apt-get install -y \
  build-essential \
  libncurses-dev \
  bison \
  flex \
  libssl-dev \
  libelf-dev \
  bc \
  cpio \
  wget \
  git

  cp ftrace.config .config
  make -j$(nproc)
"
cp ./arch/x86/boot/compressed/vmlinux.bin $BIN_DIR/faasnap-linux.bin
popd
