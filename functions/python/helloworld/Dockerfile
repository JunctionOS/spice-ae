FROM python:3.12.8-alpine3.21

RUN pip3 install --user protobuf grpcio

RUN mkdir -p /helloworld
COPY functions/python/helloworld/helloworld.py /helloworld/
COPY functions/python/util /util/
COPY functions/python/grpc/* .
COPY scripts/reap_test.py .
COPY scripts/test.py .
COPY scripts/args.py .
COPY scripts/dirs.py .
COPY functions/func_args.py .
COPY functions/python/grpc/server.py .

CMD ["python", "server.py", "helloworld"]
