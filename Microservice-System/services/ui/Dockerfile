FROM python:3.11-slim
WORKDIR /app

# bring in protos and generate flat Python stubs
COPY proto /app/proto
RUN python -m pip install --no-cache-dir grpcio-tools==1.66.1
RUN python -m grpc_tools.protoc -Iproto --python_out=. --grpc_python_out=. \
    proto/gateway.proto proto/auth.proto proto/room.proto proto/presence.proto proto/message.proto

# install runtime deps
COPY services/ui/requirements.txt /app/requirements.txt
RUN pip install --no-cache-dir -r /app/requirements.txt

# copy the UI service (FastAPI app, templates, static)
COPY services/ui /app/services/ui

ENV PYTHONPATH=/app
ENV GATEWAY_ADDR=gateway:50055
CMD ["uvicorn", "services.ui.server:app", "--host", "0.0.0.0", "--port", "8080"]
