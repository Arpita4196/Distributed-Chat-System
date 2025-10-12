import sqlite3, os, time, threading
from concurrent import futures
import grpc


#import proto.message.v1.message_pb2 as mp
#import proto.message.v1.message_pb2_grpc as mpg

import message_pb2 as mp
import message_pb2_grpc as mpg


DB_PATH = os.getenv("MESSAGE_DB", "/data/messages.db")


class Message(mpg.MessageServiceServicer):
	def __init__(self):
		self.db = sqlite3.connect(DB_PATH, check_same_thread=False)
		with open(os.path.join(os.path.dirname(__file__), "schema.sql")) as f:
			self.db.executescript(f.read())
		self.db.commit()
		self.lock = threading.Lock()
		self.subs = {} # room -> [queues]


	def Append(self, req, ctx):
		now = int(time.time()*1000)
		try:
			cur = self.db.execute(
				"INSERT INTO messages(room_id,user_id,text,ts_ms,idempotency_key) VALUES(?,?,?,?,?)",
				(req.room_id, req.user_id, req.text, now, req.idempotency_key)
			)
			self.db.commit()
		except sqlite3.IntegrityError:
			# dedup: fetch existing offset
			row = self.db.execute(
				"SELECT offset, ts_ms FROM messages WHERE room_id=? AND idempotency_key=?",
				(req.room_id, req.idempotency_key)
			).fetchone()
			off = row[0] if row else None
			return mp.AppendResp(success=True, offset=off or 0)
		off = self.db.execute("SELECT last_insert_rowid()").fetchone()[0]
		msg = mp.Msg(room_id=req.room_id, user_id=req.user_id, text=req.text, offset=off, ts_ms=now)
		self._broadcast(req.room_id, msg)
		return mp.AppendResp(success=True, offset=off)


	def List(self, req, ctx):
		lim = req.limit if req.limit > 0 else 100
		for row in self.db.execute(
			"SELECT room_id,user_id,text,offset,ts_ms FROM messages WHERE room_id=? AND offset>=? ORDER BY offset ASC LIMIT ?",
			(req.room_id, req.from_offset, lim)):
			yield mp.Msg(room_id=row[0], user_id=row[1], text=row[2], offset=row[3], ts_ms=row[4])


	def Subscribe(self, rid, ctx):
		q = []
		with self.lock:
			self.subs.setdefault(rid.room_id, []).append(q)
		try:
			while True:
				time.sleep(0.1)
				while q:
					yield q.pop(0)
		finally:
			with self.lock:
				if q in self.subs.get(rid.room_id, []):
					self.subs[rid.room_id].remove(q)


	def NextOffset(self, rid, ctx):
		row = self.db.execute("SELECT COALESCE(MAX(offset),0) FROM messages WHERE room_id=?", (rid.room_id,)).fetchone()
		val = row[0] or 0
		return mp.Offset(value=val+1)


	def _broadcast(self, room_id, msg):
		with self.lock:
			for q in self.subs.get(room_id, []):
				q.append(msg)

def serve():
	srv = grpc.server(futures.ThreadPoolExecutor(max_workers=16))
	mpg.add_MessageServiceServicer_to_server(Message(), srv)
	srv.add_insecure_port("[::]:50054")
	srv.start(); print("message-svc on :50054"); srv.wait_for_termination()