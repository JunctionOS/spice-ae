#!/bin/bash

SCRIPT_DIR=$(dirname $(readlink -f $0))
ROOT_DIR=${SCRIPT_DIR}/../
BIN_DIR=${ROOT_DIR}/bin/

export CTRD_ROOT=$1

if ! [ -f $BIN_DIR/minio ]; then
    wget -O $BIN_DIR/minio https://dl.min.io/server/minio/release/linux-amd64/minio
    chmod +x $BIN_DIR/minio
fi
