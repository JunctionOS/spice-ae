FROM python:3.12.3-slim

ARG DATA_PATH=/

RUN pip3 install --user chameleon pillow numpy pandas tensorflow grpcio grpcio-tools minio keras-preprocessing keras-applications

RUN mkdir -p /cnn_serving
COPY functions/python/cnn_serving/cnn_serving.py /cnn_serving/cnn_serving.py
COPY functions/python/grpc/* .
COPY functions/python/grpc/server.py .
COPY functions/python/util /util/

RUN mkdir -p ${DATA_PATH}/images
RUN mkdir -p ${DATA_PATH}/ml

COPY functions/data/images/image.jpg ${DATA_PATH}/images
COPY functions/data/ml/squeezenet_weights_tf_dim_ordering_tf_kernels.h5 ${DATA_PATH}/ml
COPY functions/data/ml/imagenet_class_index.json ${DATA_PATH}/ml

CMD ["python", "server.py", "cnn_serving"]
