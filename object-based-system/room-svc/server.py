import grpc
from concurrent import futures
import room_pb2, room_pb2_grpc
import uuid

rooms = {}

class RoomService(room_pb2_grpc.RoomServiceServicer):
    def CreateRoom(self, request, context):
        room_id = str(uuid.uuid4())
        rooms[room_id] = request.name
        return room_pb2.RoomResponse(id=room_id, name=request.name)

    def ListRooms(self, request, context):
        return room_pb2.RoomList(
            rooms=[room_pb2.RoomResponse(id=id, name=name) for id, name in rooms.items()]
        )

def serve():
    server = grpc.server(futures.ThreadPoolExecutor(max_workers=10))
    room_pb2_grpc.add_RoomServiceServicer_to_server(RoomService(), server)
    server.add_insecure_port("[::]:50051")
    print("[room-svc] running...")
    server.start()
    server.wait_for_termination()

if __name__ == "__main__":
    serve()
