FROM python:3.12.8-alpine3.21

RUN pip3 install --user protobuf grpcio pyaes

RUN mkdir -p /pyaes1
COPY functions/python/pyaes1/pyaes1.py /pyaes1/pyaes1.py
COPY functions/python/grpc/* .
COPY functions/python/grpc/server.py .
COPY functions/python/util /util/

CMD ["python", "server.py", "pyaes"]
