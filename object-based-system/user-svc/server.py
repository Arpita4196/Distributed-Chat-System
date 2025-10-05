import time
import grpc
from concurrent import futures
from sqlalchemy import create_engine, Column, Integer, String
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from sqlalchemy.exc import OperationalError

import user_pb2, user_pb2_grpc

# === Database Setup ===
DATABASE_URL = "postgresql+psycopg2://chatuser:chatpass@db-svc:5432/chatdb"

# Retry loop for DB connection
for i in range(10):
    try:
        engine = create_engine(DATABASE_URL)
        conn = engine.connect()
        conn.close()
        print(f"[user-svc] ✅ Connected to DB")
        break
    except OperationalError:
        print(f"[user-svc] ⏳ DB not ready, retrying ({i+1}/10)...")
        time.sleep(5)
else:
    raise RuntimeError("[user-svc] ❌ Could not connect to DB after 10 retries")

SessionLocal = sessionmaker(bind=engine)
Base = declarative_base()

class User(Base):
    __tablename__ = "users"
    id = Column(Integer, primary_key=True, index=True)
    username = Column(String, unique=True, index=True, nullable=False)
    password = Column(String, nullable=False)

Base.metadata.create_all(bind=engine)

# === gRPC Service Implementation ===
class UserService(user_pb2_grpc.UserServiceServicer):
    def Register(self, request, context):
        db = SessionLocal()
        user = User(username=request.username, password=request.password)
        db.add(user)
        db.commit()
        return user_pb2.RegisterResponse(success=True, message="User registered successfully")

    def Login(self, request, context):
        db = SessionLocal()
        user = db.query(User).filter_by(username=request.username, password=request.password).first()
        if user:
            return user_pb2.LoginResponse(success=True, message="Login successful")
        return user_pb2.LoginResponse(success=False, message="Invalid username or password")

# === Start gRPC Server ===
def serve():
    server = grpc.server(futures.ThreadPoolExecutor(max_workers=10))
    user_pb2_grpc.add_UserServiceServicer_to_server(UserService(), server)
    server.add_insecure_port("[::]:50051")
    print("[user-svc] gRPC server listening on port 50051")
    server.start()
    server.wait_for_termination()

if __name__ == "__main__":
    serve()
