from concurrent import futures
import grpc
from common.config import AUTH_ADDR, ROOM_ADDR, PRESENCE_ADDR, MESSAGE_ADDR, GATEWAY_BIND


#import proto.gateway.v1.gateway_pb2 as gp
#import proto.gateway.v1.gateway_pb2_grpc as gpg


#import proto.auth.v1.auth_pb2 as ap
#import proto.auth.v1.auth_pb2_grpc as apg
#import proto.room.v1.room_pb2 as rp
#import proto.room.v1.room_pb2_grpc as rpg
#import proto.presence.v1.presence_pb2 as pp
#import proto.presence.v1.presence_pb2_grpc as ppg
#import proto.message.v1.message_pb2 as mp
#import proto.message.v1.message_pb2_grpc as mpg

import gateway_pb2 as gp
import gateway_pb2_grpc as gpg

import auth_pb2 as ap
import auth_pb2_grpc as apg
import room_pb2 as rp
import room_pb2_grpc as rpg
import presence_pb2 as pp
import presence_pb2_grpc as ppg
import message_pb2 as mp
import message_pb2_grpc as mpg

class Gateway(gpg.GatewayServiceServicer):
	def __init__(self):
		self.auth = apg.AuthServiceStub(grpc.insecure_channel(AUTH_ADDR))
		self.room = rpg.RoomServiceStub(grpc.insecure_channel(ROOM_ADDR))
		self.pres = ppg.PresenceServiceStub(grpc.insecure_channel(PRESENCE_ADDR))
		self.msg = mpg.MessageServiceStub(grpc.insecure_channel(MESSAGE_ADDR))


	# ---- Auth proxies ----
	def Register(self, req, ctx): return self.auth.Register(req)
	def Login(self, req, ctx): return self.auth.Login(req)
	def Logout(self, tok, ctx): return self.auth.Logout(tok)
	def GetUser(self, req, ctx): return self.auth.GetUser(req)


	# ---- Rooms ----
	def CreateRoom(self, req, ctx): return self.room.CreateRoom(req)
	def JoinRoom(self, req, ctx): return self.room.JoinRoom(req)
	def LeaveRoom(self, req, ctx): return self.room.LeaveRoom(req)
	def ListRooms(self, _req, ctx):
		for r in self.room.ListRooms(rp.Empty()): yield r
	def ListMembers(self, rid, ctx):
		for m in self.room.ListMembers(rid): yield m


	# ---- Presence ----
	def Heartbeat(self, hb, ctx): return self.pres.Heartbeat(hb)
	def SubscribePresence(self, rid, ctx):
		for ev in self.pres.Subscribe(rid): yield ev
	def Roster(self, rid, ctx): return self.pres.Roster(rid)


	# ---- Messaging ----
	def Append(self, req, ctx): return self.msg.Append(req)
	def List(self, req, ctx):
		for m in self.msg.List(req): yield m


	def ReplayAndSubscribe(self, req, ctx):
		# 1) stream history from last_seen+1
		start = req.last_seen_offset + 1 if req.last_seen_offset > 0 else 0
		for m in self.msg.List(mp.ListReq(room_id=req.room_id, from_offset=start, limit=0)):
			yield m
		# 2) then subscribe live
		for m in self.msg.Subscribe(mp.RoomId(room_id=req.room_id)):
			yield m

def serve():
	srv = grpc.server(futures.ThreadPoolExecutor(max_workers=16))
	gpg.add_GatewayServiceServicer_to_server(Gateway(), srv)
	srv.add_insecure_port(GATEWAY_BIND)
	srv.start(); print(f"gateway-svc on {GATEWAY_BIND}"); srv.wait_for_termination()