#!/bin/bash

SCRIPT_DIR=$(dirname $(readlink -f $0))
ROOT_DIR=${SCRIPT_DIR}/../
BIN_DIR=${ROOT_DIR}/bin/

export CTRD_ROOT=$1
mkdir -p ${BIN_DIR}

MINIO_URL="https://github.com/minio/minio/releases/download/RELEASE.2025-09-07T16-13-09Z/minio.linux-amd64.RELEASE.2025-09-07T16-13-09Z"
MINIO_HASH="7c5bd8512c6e966455b1d198209358b2d191c77a83ab377c4073281065fb855f"

check_exists_and_hash() {
    [ -f "$BIN_DIR/minio" ] && echo "$MINIO_HASH $BIN_DIR/minio" | sha256sum -c -
}

# Check if the minio binary is already downloaded and has the correct hash
if check_exists_and_hash; then
    echo "Minio binary already downloaded and has the correct hash"
else
    wget -O $BIN_DIR/minio $MINIO_URL
    if ! check_exists_and_hash; then
        echo "Minio binary downloaded but has the incorrect hash"
        exit 1
    fi
fi

chmod +x $BIN_DIR/minio
