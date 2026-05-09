#!/bin/bash

set -x

SCRIPT_DIR=$(dirname $(readlink -f $0))
ROOT_DIR=$(realpath ${SCRIPT_DIR}/../)
FUNCTIONS_DIR=${ROOT_DIR}/functions
PYTHON_DIR=${FUNCTIONS_DIR}/python
VENV_DIR=${ROOT_DIR}/bin/venv

PYTHON=${VENV_DIR}/bin/python3
BIN_DIR=${ROOT_DIR}/bin

mkdir -p ${ROOT_DIR}/bin/

build_python() {
    if ! [ -e $PYTHON ]; then
        python3 -m venv ${VENV_DIR}
        ${VENV_DIR}/bin/pip install chameleon pillow numpy pyaes six opencv-python scikit-learn pandas tensorflow-cpu grpcio grpcio-tools minio keras-preprocessing keras-applications psutil matplotlib setuptools==80.9.0 rdtsc
        ${VENV_DIR}/bin/pip install torch==2.6.0 torchvision --index-url https://download.pytorch.org/whl/cpu
    fi
}

build_java() {
    # download java
    if ! [ -x "$BIN_DIR/java/bin/java" ]; then
        wget https://download.oracle.com/java/21/latest/jdk-21_linux-x64_bin.tar.gz \
            -O /tmp/jdk21.tar.gz
        pushd $BIN_DIR
        tar -xvzf /tmp/jdk21.tar.gz
        extracted_dir=$(tar -tf /tmp/jdk21.tar.gz | head -1 | cut -f1 -d"/")
        mv "$extracted_dir" java
        rm /tmp/jdk21.tar.gz
        popd
    fi

    # build functions
    for dir in $(ls $FUNCTIONS_DIR/java/); do
      if [ -d "$FUNCTIONS_DIR/java/$dir" ]; then
          JAVA_HOME="${BIN_DIR}/java/" \
              GRADLE_OPTS="-Dorg.gradle.java.home=${BIN_DIR}/java/" \
              $FUNCTIONS_DIR/java/$dir/gradlew clean build \
              --project-dir "$FUNCTIONS_DIR/java/$dir" \
              --gradle-user-home "$FUNCTIONS_DIR/java/.gradle"
      fi
    done

    # kill gradle daemon
    kill -9 $(pgrep -f "gradle")
}

build_node() {
    # build patched node
    sudo -E apt-get install -y libc-ares-dev libnghttp2-dev libbrotli-dev
    pushd ${ROOT_DIR}/node
    ./configure --prefix=${ROOT_DIR}/bin/ --without-npm --without-corepack --shared --shared-zlib --shared-cares --shared-nghttp2 --shared-brotli --shared-builtin-undici/undici-path=/usr/share/nodejs/undici/undici-fetch.js --shared-builtin-acorn-path=/usr/share/nodejs/acorn/dist/acorn.js --shared-builtin-acorn_walk-path=/usr/share/nodejs/acorn-walk/dist/walk.js --shared-builtin-cjs_module_lexer/lexer-path=/usr/share/nodejs/cjs-module-lexer/lexer.js --shared-builtin-cjs_module_lexer/dist/lexer-path=/usr/share/nodejs/cjs-module-lexer/dist/lexer.js --with-intl=system-icu --shared-openssl --openssl-use-def-ca-store --arch-triplet=x86_64-linux-gnu --node-relative-path="lib/x86_64-linux-gnu/nodejs:share/nodejs" --shared-libuv --dest-os=linux --dest-cpu=x64

    make -j `nproc`
    make -j `nproc` install
    popd

    pushd ${ROOT_DIR}/bin/
    npm install node-gyp minio sharp
    popd

    pushd ${ROOT_DIR}/functions/node/addon
    node-gyp configure build --nodedir=${ROOT_DIR}/bin/
    mkdir -p ${ROOT_DIR}/bin/node_modules_addon
    cp build/Release/addon.node ${ROOT_DIR}/bin/node_modules_addon
    popd
}

build_python
build_java
build_node
