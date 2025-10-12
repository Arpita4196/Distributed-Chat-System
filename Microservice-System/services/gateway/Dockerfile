FROM python:3.11-slim
WORKDIR /app
COPY proto /app/proto
RUN python -m pip install --no-cache-dir grpcio-tools==1.66.1
RUN python -m grpc_tools.protoc -Iproto --python_out=. --grpc_python_out=. proto/gateway.proto proto/auth.proto proto/room.proto proto/presence.proto proto/message.proto
COPY services/gateway/requirements.txt requirements.txt
RUN pip install --no-cache-dir -r requirements.txt
COPY common /app/common
COPY services/gateway /app/services/gateway
ENV PYTHONPATH=/app
CMD ["python","services/gateway/main.py"]