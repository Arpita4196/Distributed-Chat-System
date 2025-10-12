FROM python:3.11-slim
WORKDIR /app
COPY proto /app/proto
RUN python -m pip install --no-cache-dir grpcio-tools==1.66.1
RUN python -m grpc_tools.protoc -Iproto --python_out=. --grpc_python_out=. proto/presence.proto
COPY services/presence/requirements.txt requirements.txt
RUN pip install --no-cache-dir -r requirements.txt
COPY common /app/common
COPY services/presence /app/services/presence
ENV PYTHONPATH=/app
VOLUME ["/data"]
CMD ["python","services/presence/main.py"]