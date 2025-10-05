import time
import grpc
from concurrent import futures
from sqlalchemy import Column, Integer, String, create_engine
from sqlalchemy.orm import declarative_base, sessionmaker
from sqlalchemy.exc import OperationalError

import message_pb2, message_pb2_grpc

# === Database Setup ===
DATABASE_URL = "postgresql+psycopg2://chatuser:chatpass@db-svc:5432/chatdb"

Base = declarative_base()

class Message(Base):
    __tablename__ = "messages"
    id = Column(Integer, primary_key=True, autoincrement=True)
    room_id = Column(String, nullable=False)
    username = Column(String, nullable=False)
    text = Column(String, nullable=False)

# Retry loop for DB connection
for i in range(10):
    try:
        engine = create_engine(DATABASE_URL)
        conn = engine.connect()
        conn.close()
        print(f"[message-svc] ✅ Connected to DB")
        break
    except OperationalError:
        print(f"[message-svc] ⏳ DB not ready, retrying ({i+1}/10).")
        time.sleep(5)
else:
    raise RuntimeError("[message-svc] ❌ Could not connect to DB after 10 retries")

Base.metadata.create_all(engine)
SessionLocal = sessionmaker(bind=engine)

# === gRPC Service Implementation ===
class MessageService(message_pb2_grpc.MessageServiceServicer):
    def SendMessage(self, request, context):
        db = SessionLocal()
        msg = Message(room_id=request.room_id, username=request.sender, text=request.content)
        db.add(msg)
        db.commit()
        return message_pb2.SendResponse(success=True, message="Message sent")

    def GetMessages(self, request, context):
        db = SessionLocal()
        messages = db.query(Message).filter_by(room_id=request.room_id).all()

        proto_messages = [
            message_pb2.Message(
                room_id=msg.room_id,
                sender=msg.username,
                content=msg.text
            )
            for msg in messages
        ]

        return message_pb2.HistoryResponse(messages=proto_messages)

# === Start gRPC Server ===
def serve():
    server = grpc.server(futures.ThreadPoolExecutor(max_workers=10))
    message_pb2_grpc.add_MessageServiceServicer_to_server(MessageService(), server)
    server.add_insecure_port("[::]:50051")
    print("[message-svc] gRPC server listening on port 50051")
    server.start()
    server.wait_for_termination()

if __name__ == "__main__":
    serve()
