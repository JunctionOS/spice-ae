FROM python:3.12.8-alpine3.21

RUN pip3 install --user protobuf grpcio chameleon six

RUN mkdir -p /chameleon1
COPY functions/python/chameleon1/chameleon1.py /chameleon1/chameleon1.py
COPY functions/python/grpc/* .
COPY functions/python/grpc/server.py .
COPY functions/python/util /util/

CMD ["python", "server.py", "chameleon"]
