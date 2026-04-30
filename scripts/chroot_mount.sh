#!/bin/bash

set -e

SCRIPT_DIR=$(dirname $(readlink -f $0))
ROOT_DIR=$(realpath ${SCRIPT_DIR}/../)
JUNCTION_DIR=${ROOT_DIR}/junction
CHROOT_DIR=${ROOT_DIR}/chroot
# "${ROOT_DIR}/build-debug"
MOUNT_POINTS=("${ROOT_DIR}/functions" "${JUNCTION_DIR}/install" "${ROOT_DIR}/bin")

SNAPSHOT_DIR=${SNAPSHOT_DIR:-/tmp}
SNAPSHOT_DIR=/mnt/snapshots

mount_bind() {
  for mnt in "${MOUNT_POINTS[@]}"; do
    if ! mountpoint -q "$CHROOT_DIR/$mnt"; then
      echo "Mounting $mnt..."
      sudo mkdir -p "$CHROOT_DIR/$mnt"
      sudo mount --bind "/$mnt" "$CHROOT_DIR/$mnt"
    else
      echo "$mnt is already mounted."
    fi
  done

  if ! mountpoint -q "$CHROOT_DIR/tmp"; then
    echo "Mounting snapshot dir $SNAPSHOT_DIR -> $CHROOT_DIR/tmp..."
    sudo mkdir -p "$CHROOT_DIR/tmp" "$SNAPSHOT_DIR"
    sudo mount --bind "$SNAPSHOT_DIR" "$CHROOT_DIR/tmp"
  else
    echo "$CHROOT_DIR/tmp is already mounted."
  fi

  read major minor < <(stat -c '%t %T' /dev/jif_pager); major=$((0x$major)); minor=$((0x$minor))
  echo $major $minor
  sudo mknod -m 666 $CHROOT_DIR/dev/jif_pager c $major $minor || true
}

unmount_bind() {
  while mountpoint -q "$CHROOT_DIR/tmp"; do
    echo "Unmounting $CHROOT_DIR/tmp..."
    sudo umount "$CHROOT_DIR/tmp"
  done
  for mnt in "${MOUNT_POINTS[@]}"; do
    while mountpoint -q "$CHROOT_DIR/$mnt"; do
      echo "Unmounting $mnt..."
      sudo umount "$CHROOT_DIR/$mnt"
    done
  done
}

if [ ! -d ${CHROOT_DIR} ]; then
    echo "missing chroot dir"
    exit -1
fi

if [[ $1 == "-u" ]]; then
  unmount_bind
else
  mount_bind
fi
