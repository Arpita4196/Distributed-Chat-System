import grpc
from concurrent import futures

import gateway_pb2, gateway_pb2_grpc
import message_pb2, message_pb2_grpc
import user_pb2, user_pb2_grpc
import room_pb2, room_pb2_grpc
import presence_pb2, presence_pb2_grpc

# Connect to other services
user_channel = grpc.insecure_channel("user-svc:50051")
user_stub = user_pb2_grpc.UserServiceStub(user_channel)

message_channel = grpc.insecure_channel("message-svc:50051")
message_stub = message_pb2_grpc.MessageServiceStub(message_channel)

room_channel = grpc.insecure_channel("room-svc:50051")
room_stub = room_pb2_grpc.RoomServiceStub(room_channel)

presence_channel = grpc.insecure_channel("presence-svc:50051")
presence_stub = presence_pb2_grpc.PresenceServiceStub(presence_channel)


class GatewayService(gateway_pb2_grpc.GatewayServiceServicer):
    # --------------------
    # User
    # --------------------
    def RegisterUser(self, request, context):
        print(f"[gateway-svc] Forwarding RegisterUser for {request.username}")
        return user_stub.Register(request)

    def LoginUser(self, request, context):
        print(f"[gateway-svc] Forwarding LoginUser for {request.username}")
        return user_stub.Login(request)

    # --------------------
    # Messaging
    # --------------------
   # --------------------
# Messaging
# --------------------
    def SendMessage(self, request, context):
        print(f"[gateway-svc] Forwarding SendMessage from {request.sender}")
        return message_stub.SendMessage(
            message_pb2.Message(
                room_id=request.room_id,
                sender=request.sender,
                content=request.content,
                timestamp=request.timestamp  # optional but proto defines it
            )
        )


    def GetMessages(self, request, context):
        print(f"[gateway-svc] Forwarding GetMessages for room {request.room_id}")
        return message_stub.GetMessages(
            message_pb2.HistoryRequest(room_id=request.room_id)
        )


    # --------------------
    # Rooms
    # --------------------
    def CreateRoom(self, request, context):
        return room_stub.CreateRoom(request)

    def ListRooms(self, request, context):
        return room_stub.ListRooms(request)

    # --------------------
    # Presence
    # --------------------
    def UpdatePresence(self, request, context):
        return presence_stub.UpdatePresence(request)


def serve():
    server = grpc.server(futures.ThreadPoolExecutor(max_workers=10))
    gateway_pb2_grpc.add_GatewayServiceServicer_to_server(GatewayService(), server)
    server.add_insecure_port("[::]:50051")
    print("[gateway-svc] gRPC server listening on port 50051")
    server.start()
    server.wait_for_termination()


if __name__ == "__main__":
    serve()
