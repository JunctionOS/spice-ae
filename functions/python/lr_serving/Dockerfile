FROM python:3.12.3-slim

ARG DATA_PATH=/

RUN pip3 install --user protobuf grpcio pandas scikit-learn grpcio minio psutil

RUN mkdir -p /lr_serving
COPY functions/python/lr_serving/lr_serving.py /lr_serving/lr_serving.py
COPY functions/python/grpc/* .
COPY functions/python/grpc/server.py .
COPY functions/python/util /util/

RUN mkdir -p ${DATA_PATH}/ml
COPY functions/data/ml/dataset.csv ${DATA_PATH}/ml
COPY functions/data/ml/lr_model.pk ${DATA_PATH}/ml

CMD ["python", "server.py", "lr_serving"]
