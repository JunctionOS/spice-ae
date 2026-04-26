FROM python:3.12.3-alpine

ARG DATA_PATH=/

RUN pip3 install --user protobuf grpcio pillow minio

RUN mkdir -p /image_rotate_s3
COPY functions/python/image_rotate_s3/image_rotate_s3.py /image_rotate_s3/image_rotate_s3.py
COPY functions/python/grpc/* .
COPY functions/python/grpc/server.py .
COPY functions/python/util /util/

CMD ["python", "server.py", "image_rotate_s3"]
