FROM python:3.11-slim
WORKDIR /app
COPY proto /app/proto
RUN python -m pip install --no-cache-dir grpcio-tools==1.66.1
RUN python -m grpc_tools.protoc -Iproto --python_out=. --grpc_python_out=. proto/message.proto
COPY services/message/requirements.txt requirements.txt
RUN pip install --no-cache-dir -r requirements.txt
COPY services/message /app/services/message
ENV PYTHONPATH=/app
VOLUME ["/data"]
CMD ["python","services/message/main.py"]