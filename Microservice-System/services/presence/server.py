import time, threading, os, sqlite3
from concurrent import futures
import grpc
from common.config import PRESENCE_TTL_SECS, PRESENCE_DB
#import proto.presence.v1.presence_pb2 as pp
#import proto.presence.v1.presence_pb2_grpc as ppg
import presence_pb2 as pp
import presence_pb2_grpc as ppg

STATE = {}

PRESENCE_TTL_MS = int(os.getenv("PRESENCE_TTL_SECS", "20")) * 1000

# In-memory with optional snapshot of last_seen
class Presence(ppg.PresenceServiceServicer):
	def __init__(self):
		self.lock = threading.Lock()
		self.last = {} # room -> {user -> ts_ms}
		self.subs = {} # room -> [queues]
		# optional snapshot DB
		self.db = sqlite3.connect(PRESENCE_DB, check_same_thread=False)
		self.db.execute("CREATE TABLE IF NOT EXISTS last_seen(room_id TEXT,user_id TEXT,ts_ms INTEGER,PRIMARY KEY(room_id,user_id))")
		threading.Thread(target=self._reaper, daemon=True).start()


	'''def Heartbeat(self, hb, ctx):
		now = int(time.time()*1000)
		with self.lock:
			room = self.last.setdefault(hb.room_id, {})
			is_new = hb.user_id not in room
			room[hb.user_id] = now
			self.db.execute("INSERT OR REPLACE INTO last_seen(room_id,user_id,ts_ms) VALUES(?,?,?)", (hb.room_id, hb.user_id, now))
			self.db.commit()
			if is_new:
				self._broadcast(hb.room_id, pp.PresenceEvent(user_id=hb.user_id, type="JOIN", ts_ms=now))
		return pp.Ack(success=True)'''

	def Heartbeat(self, req, ctx):
		now = int(time.time() * 1000)
		room = STATE.setdefault(req.room_id, {})
		rec = room.setdefault(req.user_id, {"last_seen_ms": now, "display_name": req.display_name or req.user_id})
		rec["last_seen_ms"] = now
		if req.display_name:
			rec["display_name"] = req.display_name

		# emit JOIN if this is first time / was expired
		# (left as simple: always emit JOIN on heartbeat for demo)
		ev = pp.PresenceEvent(
			type=pp.JOIN, room_id=req.room_id,
			user_id=req.user_id, display_name=rec["display_name"], ts_ms=now
		)
		# (if you already had a stream fan-out, push ev there)
		return pp.Ack(ok=True)


	def Subscribe(self, rid, ctx):
		q = []
		with self.lock:
			self.subs.setdefault(rid.room_id, []).append(q)
		try:
			while True:
				time.sleep(0.25)
				while q:
					yield q.pop(0)
		finally:
			with self.lock:
				if q in self.subs.get(rid.room_id, []):
					self.subs[rid.room_id].remove(q)


	'''def Roster(self, rid, ctx):
		with self.lock:
			users = list(self.last.get(rid.room_id, {}).keys())
		return pp.RosterReply(user_ids=sorted(users))'''
	
	def Roster(self, req, ctx):
		now = int(time.time()*1000)
		room = STATE.get(req.room_id, {})
		users = []
		expired = []
		for uid, rec in room.items():
			if now - rec["last_seen_ms"] > PRESENCE_TTL_MS:
				expired.append(uid)
				continue
			users.append(pp.PresenceUser(
				user_id=uid,
				display_name=rec.get("display_name") or uid,
				last_seen_ms=rec["last_seen_ms"]
			))
		# cleanup expired
		for uid in expired:
			room.pop(uid, None)
		return pp.RosterReply(users=users)


	def _broadcast(self, room_id, ev):
		for q in self.subs.get(room_id, []):
			q.append(ev)


	def _reaper(self):
		while True:
			time.sleep(1)
			now = int(time.time()*1000)
			with self.lock:
				for room_id, users in list(self.last.items()):
					for uid, ts in list(users.items()):
						if now - ts > PRESENCE_TTL_SECS*1000:
							del users[uid]
							self._broadcast(room_id, pp.PresenceEvent(user_id=uid, type="LEAVE", ts_ms=now))


def serve():
	srv = grpc.server(futures.ThreadPoolExecutor(max_workers=8))
	ppg.add_PresenceServiceServicer_to_server(Presence(), srv)
	srv.add_insecure_port("[::]:50053")
	srv.start(); print("presence-svc on :50053"); srv.wait_for_termination()