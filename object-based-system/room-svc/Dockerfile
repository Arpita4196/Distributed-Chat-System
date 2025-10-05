FROM python:3.12-slim
WORKDIR /app

COPY room-svc/requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY room-svc /app
COPY protos /protos

RUN python -m grpc_tools.protoc \
    -I=/protos \
    --python_out=/app \
    --grpc_python_out=/app \
    /protos/user.proto \
    /protos/message.proto \
    /protos/room.proto \
    /protos/presence.proto \
    /protos/gateway.proto

CMD ["python", "server.py"]
