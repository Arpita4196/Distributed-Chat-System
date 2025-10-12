import sqlite3, os, time
from concurrent import futures
import grpc


#import proto.room.v1.room_pb2 as rp
#import proto.room.v1.room_pb2_grpc as rpg

import room_pb2 as rp
import room_pb2_grpc as rpg

DB_PATH = os.getenv("ROOM_DB", "/data/rooms.db")


def get_conn():
	conn = sqlite3.connect(DB_PATH, check_same_thread=False)
	conn.execute("PRAGMA foreign_keys=ON")
	return conn


class Room(rpg.RoomServiceServicer):
	def __init__(self):
		self.conn = get_conn()
		with open(os.path.join(os.path.dirname(__file__), "schema.sql")) as f:
			self.conn.executescript(f.read())


	def CreateRoom(self, req, ctx):
		try:
			self.conn.execute("INSERT OR IGNORE INTO rooms(room_id,name) VALUES(?,?)", (req.room_id, req.name))
			self.conn.commit()
			return rp.Ack(success=True)
		except Exception as e:
			return rp.Ack(success=False, error=str(e))


	def JoinRoom(self, req, ctx):
		try:
			self.conn.execute("INSERT OR IGNORE INTO members(room_id,user_id) VALUES(?,?)", (req.room_id, req.user_id))
			self.conn.commit(); return rp.Ack(success=True)
		except Exception as e:
			return rp.Ack(success=False, error=str(e))


	def LeaveRoom(self, req, ctx):
		self.conn.execute("DELETE FROM members WHERE room_id=? AND user_id=?", (req.room_id, req.user_id))
		self.conn.commit(); return rp.Ack(success=True)


	def ListRooms(self, _req, ctx):
		for rid, name in self.conn.execute("SELECT room_id,name FROM rooms ORDER BY room_id"):
			yield rp.Room(room_id=rid, name=name)


	def ListMembers(self, rid, ctx):
		for uid, in self.conn.execute("SELECT user_id FROM members WHERE room_id=? ORDER BY user_id", (rid.room_id,)):
			yield rp.Member(user_id=uid, room_id=rid.room_id)


	def RoomExists(self, rid, ctx):
		cur = self.conn.execute("SELECT 1 FROM rooms WHERE room_id=?", (rid.room_id,))
		return rp.Ack(success=cur.fetchone() is not None)


def serve():
	srv = grpc.server(futures.ThreadPoolExecutor(max_workers=8))
	rpg.add_RoomServiceServicer_to_server(Room(), srv)
	srv.add_insecure_port("[::]:50052"); srv.start(); print("room-svc on :50052"); srv.wait_for_termination()