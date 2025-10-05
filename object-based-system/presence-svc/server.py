import grpc
from concurrent import futures
import presence_pb2, presence_pb2_grpc

presence = {}

class PresenceService(presence_pb2_grpc.PresenceServiceServicer):
    def SetPresence(self, request, context):
        presence[request.username] = request.online
        return presence_pb2.PresenceResponse(
            message=f"{request.username} is now {'online' if request.online else 'offline'}"
        )

    def GetPresence(self, request, context):
        status = presence.get(request.username, False)
        return presence_pb2.PresenceResponse(
            message=f"{request.username} is {'online' if status else 'offline'}"
        )

def serve():
    server = grpc.server(futures.ThreadPoolExecutor(max_workers=10))
    presence_pb2_grpc.add_PresenceServiceServicer_to_server(PresenceService(), server)
    server.add_insecure_port("[::]:50051")
    print("[presence-svc] running...")
    server.start()
    server.wait_for_termination()

if __name__ == "__main__":
    serve()
