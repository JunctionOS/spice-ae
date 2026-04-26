FROM python:3.12.8-alpine3.21

RUN pip3 install --user protobuf grpcio chameleon six minio

RUN mkdir -p /json_serdes_s3
COPY functions/python/json_serdes_s3/json_serdes_s3.py /json_serdes_s3/json_serdes_s3.py
COPY functions/python/grpc/* .
COPY functions/python/grpc/server.py .
COPY functions/python/util /util/

CMD ["python", "server.py", "json_serdes_s3"]
