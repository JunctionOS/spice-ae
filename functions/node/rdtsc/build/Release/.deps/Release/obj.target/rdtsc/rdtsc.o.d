cmd_Release/obj.target/rdtsc/rdtsc.o := g++ -o Release/obj.target/rdtsc/rdtsc.o ../rdtsc.cpp '-DNODE_GYP_MODULE_NAME=rdtsc' '-DUSING_UV_SHARED=1' '-DUSING_V8_SHARED=1' '-DV8_DEPRECATION_WARNINGS=1' '-DV8_DEPRECATION_WARNINGS' '-DV8_IMMINENT_DEPRECATION_WARNINGS' '-D_GLIBCXX_USE_CXX11_ABI=1' '-D_LARGEFILE_SOURCE' '-D_FILE_OFFSET_BITS=64' '-D__STDC_FORMAT_MACROS' '-DBUILDING_NODE_EXTENSION' -I/usr/include/nodejs/include/node -I/usr/include/nodejs/src -I/usr/include/nodejs/deps/openssl/config -I/usr/include/nodejs/deps/openssl/openssl/include -I/usr/include/nodejs/deps/uv/include -I/usr/include/nodejs/deps/zlib -I/usr/include/nodejs/deps/v8/include -I../node_modules/nan  -fPIC -pthread -Wall -Wextra -Wno-unused-parameter -fPIC -m64 -O3 -fno-omit-frame-pointer -fno-rtti -fno-exceptions -std=gnu++17 -MMD -MF ./Release/.deps/Release/obj.target/rdtsc/rdtsc.o.d.raw   -c
Release/obj.target/rdtsc/rdtsc.o: ../rdtsc.cpp ../node_modules/nan/nan.h \
 /usr/include/nodejs/src/node_version.h \
 /usr/include/nodejs/deps/uv/include/uv.h \
 /usr/include/nodejs/deps/uv/include/uv/errno.h \
 /usr/include/nodejs/deps/uv/include/uv/version.h \
 /usr/include/nodejs/deps/uv/include/uv/unix.h \
 /usr/include/nodejs/deps/uv/include/uv/threadpool.h \
 /usr/include/nodejs/deps/uv/include/uv/linux.h \
 /usr/include/nodejs/src/node.h /usr/include/nodejs/deps/v8/include/v8.h \
 /usr/include/nodejs/deps/v8/include/cppgc/common.h \
 /usr/include/nodejs/deps/v8/include/v8config.h \
 /usr/include/nodejs/deps/v8/include/v8-array-buffer.h \
 /usr/include/nodejs/deps/v8/include/v8-local-handle.h \
 /usr/include/nodejs/deps/v8/include/v8-internal.h \
 /usr/include/nodejs/deps/v8/include/v8-version.h \
 /usr/include/nodejs/deps/v8/include/v8config.h \
 /usr/include/nodejs/deps/v8/include/v8-object.h \
 /usr/include/nodejs/deps/v8/include/v8-maybe.h \
 /usr/include/nodejs/deps/v8/include/v8-persistent-handle.h \
 /usr/include/nodejs/deps/v8/include/v8-weak-callback-info.h \
 /usr/include/nodejs/deps/v8/include/v8-primitive.h \
 /usr/include/nodejs/deps/v8/include/v8-data.h \
 /usr/include/nodejs/deps/v8/include/v8-value.h \
 /usr/include/nodejs/deps/v8/include/v8-traced-handle.h \
 /usr/include/nodejs/deps/v8/include/v8-container.h \
 /usr/include/nodejs/deps/v8/include/v8-context.h \
 /usr/include/nodejs/deps/v8/include/v8-snapshot.h \
 /usr/include/nodejs/deps/v8/include/v8-date.h \
 /usr/include/nodejs/deps/v8/include/v8-debug.h \
 /usr/include/nodejs/deps/v8/include/v8-script.h \
 /usr/include/nodejs/deps/v8/include/v8-message.h \
 /usr/include/nodejs/deps/v8/include/v8-exception.h \
 /usr/include/nodejs/deps/v8/include/v8-extension.h \
 /usr/include/nodejs/deps/v8/include/v8-external.h \
 /usr/include/nodejs/deps/v8/include/v8-function.h \
 /usr/include/nodejs/deps/v8/include/v8-function-callback.h \
 /usr/include/nodejs/deps/v8/include/v8-template.h \
 /usr/include/nodejs/deps/v8/include/v8-memory-span.h \
 /usr/include/nodejs/deps/v8/include/v8-initialization.h \
 /usr/include/nodejs/deps/v8/include/v8-callbacks.h \
 /usr/include/nodejs/deps/v8/include/v8-isolate.h \
 /usr/include/nodejs/deps/v8/include/v8-embedder-heap.h \
 /usr/include/nodejs/deps/v8/include/v8-microtask.h \
 /usr/include/nodejs/deps/v8/include/v8-statistics.h \
 /usr/include/nodejs/deps/v8/include/v8-promise.h \
 /usr/include/nodejs/deps/v8/include/v8-unwinder.h \
 /usr/include/nodejs/deps/v8/include/v8-embedder-state-scope.h \
 /usr/include/nodejs/deps/v8/include/v8-platform.h \
 /usr/include/nodejs/deps/v8/include/v8-json.h \
 /usr/include/nodejs/deps/v8/include/v8-locker.h \
 /usr/include/nodejs/deps/v8/include/v8-microtask-queue.h \
 /usr/include/nodejs/deps/v8/include/v8-primitive-object.h \
 /usr/include/nodejs/deps/v8/include/v8-proxy.h \
 /usr/include/nodejs/deps/v8/include/v8-regexp.h \
 /usr/include/nodejs/deps/v8/include/v8-typed-array.h \
 /usr/include/nodejs/deps/v8/include/v8-value-serializer.h \
 /usr/include/nodejs/deps/v8/include/v8-wasm.h \
 /usr/include/nodejs/deps/v8/include/v8-platform.h \
 /usr/include/nodejs/src/node_version.h \
 /usr/include/nodejs/src/node_api.h \
 /usr/include/nodejs/src/js_native_api.h \
 /usr/include/nodejs/src/js_native_api_types.h \
 /usr/include/nodejs/src/node_api_types.h \
 /usr/include/nodejs/src/node_buffer.h /usr/include/nodejs/src/node.h \
 /usr/include/nodejs/src/node_object_wrap.h \
 ../node_modules/nan/nan_callbacks.h \
 ../node_modules/nan/nan_callbacks_12_inl.h \
 ../node_modules/nan/nan_maybe_43_inl.h \
 ../node_modules/nan/nan_converters.h \
 ../node_modules/nan/nan_converters_43_inl.h \
 ../node_modules/nan/nan_new.h \
 ../node_modules/nan/nan_implementation_12_inl.h \
 ../node_modules/nan/nan_persistent_12_inl.h \
 ../node_modules/nan/nan_weak.h ../node_modules/nan/nan_object_wrap.h \
 ../node_modules/nan/nan_private.h \
 ../node_modules/nan/nan_typedarray_contents.h \
 ../node_modules/nan/nan_json.h ../node_modules/nan/nan_scriptorigin.h
../rdtsc.cpp:
../node_modules/nan/nan.h:
/usr/include/nodejs/src/node_version.h:
/usr/include/nodejs/deps/uv/include/uv.h:
/usr/include/nodejs/deps/uv/include/uv/errno.h:
/usr/include/nodejs/deps/uv/include/uv/version.h:
/usr/include/nodejs/deps/uv/include/uv/unix.h:
/usr/include/nodejs/deps/uv/include/uv/threadpool.h:
/usr/include/nodejs/deps/uv/include/uv/linux.h:
/usr/include/nodejs/src/node.h:
/usr/include/nodejs/deps/v8/include/v8.h:
/usr/include/nodejs/deps/v8/include/cppgc/common.h:
/usr/include/nodejs/deps/v8/include/v8config.h:
/usr/include/nodejs/deps/v8/include/v8-array-buffer.h:
/usr/include/nodejs/deps/v8/include/v8-local-handle.h:
/usr/include/nodejs/deps/v8/include/v8-internal.h:
/usr/include/nodejs/deps/v8/include/v8-version.h:
/usr/include/nodejs/deps/v8/include/v8config.h:
/usr/include/nodejs/deps/v8/include/v8-object.h:
/usr/include/nodejs/deps/v8/include/v8-maybe.h:
/usr/include/nodejs/deps/v8/include/v8-persistent-handle.h:
/usr/include/nodejs/deps/v8/include/v8-weak-callback-info.h:
/usr/include/nodejs/deps/v8/include/v8-primitive.h:
/usr/include/nodejs/deps/v8/include/v8-data.h:
/usr/include/nodejs/deps/v8/include/v8-value.h:
/usr/include/nodejs/deps/v8/include/v8-traced-handle.h:
/usr/include/nodejs/deps/v8/include/v8-container.h:
/usr/include/nodejs/deps/v8/include/v8-context.h:
/usr/include/nodejs/deps/v8/include/v8-snapshot.h:
/usr/include/nodejs/deps/v8/include/v8-date.h:
/usr/include/nodejs/deps/v8/include/v8-debug.h:
/usr/include/nodejs/deps/v8/include/v8-script.h:
/usr/include/nodejs/deps/v8/include/v8-message.h:
/usr/include/nodejs/deps/v8/include/v8-exception.h:
/usr/include/nodejs/deps/v8/include/v8-extension.h:
/usr/include/nodejs/deps/v8/include/v8-external.h:
/usr/include/nodejs/deps/v8/include/v8-function.h:
/usr/include/nodejs/deps/v8/include/v8-function-callback.h:
/usr/include/nodejs/deps/v8/include/v8-template.h:
/usr/include/nodejs/deps/v8/include/v8-memory-span.h:
/usr/include/nodejs/deps/v8/include/v8-initialization.h:
/usr/include/nodejs/deps/v8/include/v8-callbacks.h:
/usr/include/nodejs/deps/v8/include/v8-isolate.h:
/usr/include/nodejs/deps/v8/include/v8-embedder-heap.h:
/usr/include/nodejs/deps/v8/include/v8-microtask.h:
/usr/include/nodejs/deps/v8/include/v8-statistics.h:
/usr/include/nodejs/deps/v8/include/v8-promise.h:
/usr/include/nodejs/deps/v8/include/v8-unwinder.h:
/usr/include/nodejs/deps/v8/include/v8-embedder-state-scope.h:
/usr/include/nodejs/deps/v8/include/v8-platform.h:
/usr/include/nodejs/deps/v8/include/v8-json.h:
/usr/include/nodejs/deps/v8/include/v8-locker.h:
/usr/include/nodejs/deps/v8/include/v8-microtask-queue.h:
/usr/include/nodejs/deps/v8/include/v8-primitive-object.h:
/usr/include/nodejs/deps/v8/include/v8-proxy.h:
/usr/include/nodejs/deps/v8/include/v8-regexp.h:
/usr/include/nodejs/deps/v8/include/v8-typed-array.h:
/usr/include/nodejs/deps/v8/include/v8-value-serializer.h:
/usr/include/nodejs/deps/v8/include/v8-wasm.h:
/usr/include/nodejs/deps/v8/include/v8-platform.h:
/usr/include/nodejs/src/node_version.h:
/usr/include/nodejs/src/node_api.h:
/usr/include/nodejs/src/js_native_api.h:
/usr/include/nodejs/src/js_native_api_types.h:
/usr/include/nodejs/src/node_api_types.h:
/usr/include/nodejs/src/node_buffer.h:
/usr/include/nodejs/src/node.h:
/usr/include/nodejs/src/node_object_wrap.h:
../node_modules/nan/nan_callbacks.h:
../node_modules/nan/nan_callbacks_12_inl.h:
../node_modules/nan/nan_maybe_43_inl.h:
../node_modules/nan/nan_converters.h:
../node_modules/nan/nan_converters_43_inl.h:
../node_modules/nan/nan_new.h:
../node_modules/nan/nan_implementation_12_inl.h:
../node_modules/nan/nan_persistent_12_inl.h:
../node_modules/nan/nan_weak.h:
../node_modules/nan/nan_object_wrap.h:
../node_modules/nan/nan_private.h:
../node_modules/nan/nan_typedarray_contents.h:
../node_modules/nan/nan_json.h:
../node_modules/nan/nan_scriptorigin.h:
