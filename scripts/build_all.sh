#!/bin/bash

set -euo pipefail

SCRIPT_DIR=$(dirname "$(readlink -f "$0")")
ROOT_DIR=$(realpath "${SCRIPT_DIR}/../")
BIN_DIR=${ROOT_DIR}/bin
VENV_DIR=${BIN_DIR}/venv
JUNCTION_DIR=${ROOT_DIR}/junction
JIFTOOLS_DIR=${ROOT_DIR}/jiftools
JIFPAGER_DIR=${ROOT_DIR}/jifpager
CRIU_DIR=${ROOT_DIR}/criu
CHROOT_DIR=${ROOT_DIR}/chroot

export DEBIAN_FRONTEND=noninteractive

log() { printf '\n\033[1;36m[build_all]\033[0m %s\n' "$*"; }

# ---------------------------------------------------------------- 1. apt deps
log "Installing top-level apt prerequisites"
sudo apt-get update
sudo -E apt-get install -y \
    python3.12-venv \
    build-essential pkg-config \
    libprotobuf-dev libprotobuf-c-dev protobuf-c-compiler protobuf-compiler \
    python3-protobuf libnet-dev libnl-3-dev libnl-route-3-dev \
    libbsd0 libbsd-dev libcap-dev libaio-dev python3-yaml \
    asciidoc xmlto libdrm-dev libgnutls28-dev libnftables-dev \
    iproute2 \
    curl wget git docker.io

# rust (needed for jiftools); install via rustup if missing
if ! command -v cargo >/dev/null 2>&1; then
    log "Installing rust toolchain via rustup"
    curl --proto '=https' --tlsv1.2 -sSf https://sh.rustup.rs \
        | sh -s -- -y --default-toolchain stable
    # shellcheck disable=SC1091
    source "$HOME/.cargo/env"
fi
# Make cargo visible for the remainder of this script even if it was just installed
if [ -f "$HOME/.cargo/env" ]; then
    # shellcheck disable=SC1091
    source "$HOME/.cargo/env"
fi

# ---------------------------------------------------------------- 2. submodules
log "Initializing submodules (uninitialized only)"
pushd "$ROOT_DIR" >/dev/null
# `git submodule status` prefixes uninitialized entries with '-'.
mapfile -t uninit < <(git submodule status | awk '/^-/ {print $2}')
if [ "${#uninit[@]}" -eq 0 ]; then
    log "All top-level submodules already initialized; skipping"
else
    log "Initializing: ${uninit[*]}"
    git submodule update --init --recursive --jobs="$(nproc)" -- "${uninit[@]}"
fi
popd >/dev/null

# ---------------------------------------------------------------- 3. junction
log "Building junction (install + build)"
pushd "$JUNCTION_DIR" >/dev/null
if [ ! -f "${JUNCTION_DIR}/.install_script_ran" ]; then
    ./scripts/install.sh
fi
./scripts/build.sh
popd >/dev/null

# ---------------------------------------------------------------- 4. jiftools
log "Building jiftools (cargo --release)"
pushd "$JIFTOOLS_DIR" >/dev/null
cargo build --release
popd >/dev/null

# ---------------------------------------------------------------- 5. jifpager
log "Building jifpager kernel module"
if [ ! -d "/lib/modules/$(uname -r)/build" ]; then
    log "Installing kernel headers for $(uname -r)"
    sudo -E apt-get install -y "linux-headers-$(uname -r)" || \
        sudo -E apt-get install -y linux-headers-generic
fi
pushd "$JIFPAGER_DIR" >/dev/null
make -j"$(nproc)"
popd >/dev/null

# ---------------------------------------------------------------- 6. criu
log "Building CRIU"
pushd "$CRIU_DIR" >/dev/null
make -j"$(nproc)"
gcc -shared -fPIC -o block_io_uring.so block_iouring.c -lseccomp
popd >/dev/null

# ---------------------------------------------------------------- 7. functions
log "Building user functions (./scripts/build_functions.sh)"
"${SCRIPT_DIR}/build_functions.sh"

# ---------------------------------------------------------------- 8. faasnap
log "Building faasnap stack (./scripts/build_faasnap.sh)"
"${SCRIPT_DIR}/build_faasnap.sh"

# ---------------------------------------------------------------- 9. minio
log "Installing minio"
mkdir -p "$BIN_DIR"
"${SCRIPT_DIR}/install_minio.sh"

# ---------------------------------------------------------------- 10. chroot
log "Setting up chroot at ${CHROOT_DIR}"
if [ -d "$CHROOT_DIR" ] && [ -n "$(ls -A "$CHROOT_DIR" 2>/dev/null)" ]; then
    log "chroot already populated; skipping (rm -rf ${CHROOT_DIR} to rebuild)"
else
    "${SCRIPT_DIR}/install_chroot.sh"
fi

log "All components built."
log "Sanity-check artifacts:"
log "  bin/venv               -> $([ -x ${VENV_DIR}/bin/python3 ] && echo OK || echo MISSING)"
log "  bin/minio              -> $([ -x ${BIN_DIR}/minio ] && echo OK || echo MISSING)"
log "  bin/faasnap-fc         -> $([ -x ${BIN_DIR}/faasnap-fc ] && echo OK || echo MISSING)"
log "  bin/faasnap-linux.bin  -> $([ -f ${BIN_DIR}/faasnap-linux.bin ] && echo OK || echo MISSING)"
log "  faasnap daemon         -> $([ -x ${ROOT_DIR}/faasnap/main ] && echo OK || echo MISSING)"
log "  jiftools/jiftool       -> $([ -x ${JIFTOOLS_DIR}/target/release/jiftool ] && echo OK || echo MISSING)"
log "  jifpager.ko            -> $([ -f ${JIFPAGER_DIR}/jif_pager.ko ] && echo OK || echo MISSING)"
log "  criu                   -> $([ -x ${CRIU_DIR}/criu/criu ] && echo OK || echo MISSING)"
log "  junction_run           -> $([ -x ${JUNCTION_DIR}/build/junction/junction_run ] && echo OK || echo MISSING)"
log "  chroot                 -> $([ -d ${CHROOT_DIR}/usr ] && echo OK || echo MISSING)"
