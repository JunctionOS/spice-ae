FROM python:3.12.3-slim

ARG DATA_PATH=/

RUN pip install --upgrade pip; pip3 install --user protobuf grpcio numpy; pip3 install --user torch --index-url https://download.pytorch.org/whl/cpu

RUN mkdir -p /rnn_serving
COPY functions/python/rnn_serving/rnn_serving.py /rnn_serving/rnn_serving.py
COPY functions/python/grpc/* .
COPY functions/python/grpc/server.py .
COPY functions/python/util /util/

RUN mkdir -p ${DATA_PATH}/ml
COPY functions/data/ml/rnn_params.pkl ${DATA_PATH}/ml
COPY functions/data/ml/rnn_model.pth ${DATA_PATH}/ml

CMD ["python", "server.py", "rnn_serving"]
