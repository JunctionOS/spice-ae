FROM python:3.12.3-slim

RUN pip3 install --user protobuf grpcio minio scikit-learn pandas numpy

RUN mkdir -p /lr_training_s3
COPY functions/python/lr_training_s3/lr_training_s3.py /lr_training_s3/lr_training_s3.py
COPY functions/python/grpc/* .
COPY functions/python/grpc/server.py .

CMD ["python", "server.py", "lr_training_s3"]
