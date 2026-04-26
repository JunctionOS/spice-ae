FROM python:3.12.3-slim

ARG DATA_PATH=/

RUN apt update && apt install -y libgl1 libgl1-mesa-dri libglib2.0-0
RUN pip install --upgrade pip && \
    pip3 install --user protobuf grpcio opencv-python minio

RUN mkdir -p /video_processing_s3
COPY functions/python/video_processing_s3/video_processing_s3.py /video_processing_s3/video_processing_s3.py
COPY functions/python/grpc/* .
COPY functions/python/grpc/server.py .

EXPOSE 50051

CMD ["python", "server.py", "video_processing_s3"]
