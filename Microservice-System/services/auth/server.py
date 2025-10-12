from concurrent import futures
import grpc, uuid, sqlite3, os
from common.jwt_utils import issue, verify, revoke
from common.config import AUTH_ADDR
#import proto.auth.v1.auth_pb2 as ap
#import proto.auth.v1.auth_pb2_grpc as apg
import auth_pb2 as ap
import auth_pb2_grpc as apg

AUTH_DB = os.getenv("AUTH_DB", "/data/auth.db")


class Auth(apg.AuthServiceServicer):
	def __init__(self):
		self.db = sqlite3.connect(AUTH_DB, check_same_thread=False)
		self.db.execute("""
			CREATE TABLE IF NOT EXISTS users (
				email TEXT PRIMARY KEY,
				user_id TEXT NOT NULL,
				password TEXT NOT NULL,
				display_name TEXT
			)
		""")
		self.db.commit()

	def Register(self, req, ctx):
		# Check if user already exists
		cursor = self.db.execute("SELECT user_id FROM users WHERE email = ?", (req.email,))
		existing = cursor.fetchone()
		
		if existing:
			# User exists, return token for existing user
			user_id = existing[0]
			tok = issue(user_id, req.email)
			return ap.AuthResponse(access_token=tok)
		
		# Create new user
		uid = str(uuid.uuid4())
		self.db.execute("INSERT INTO users (email, user_id, password, display_name) VALUES (?, ?, ?, ?)", 
		               (req.email, uid, req.password, req.display_name))
		self.db.commit()
		return ap.AuthResponse(access_token=issue(uid, req.email))

	def Login(self, req, ctx):
		cursor = self.db.execute("SELECT user_id, password FROM users WHERE email = ?", (req.email,))
		rec = cursor.fetchone()
		
		if not rec or rec[1] != req.password:
			ctx.abort(grpc.StatusCode.UNAUTHENTICATED, "bad creds")
		
		user_id = rec[0]
		return ap.AuthResponse(access_token=issue(user_id, req.email))


	def Verify(self, tok, ctx):
		try:
			data = verify(tok.access_token)
			return ap.User(user_id=data['sub'], email=data['email'])
		except Exception:
			ctx.abort(grpc.StatusCode.UNAUTHENTICATED, "invalid token")


	def Logout(self, tok, ctx):
		if not revoke(tok.access_token):
			ctx.abort(grpc.StatusCode.INVALID_ARGUMENT, "bad token")
		return ap.Ack(success=True)

	def GetUser(self, req, ctx):
		cursor = self.db.execute("SELECT user_id, display_name FROM users WHERE user_id = ?", (req.user_id,))
		rec = cursor.fetchone()
		if not rec:
			ctx.abort(grpc.StatusCode.NOT_FOUND, "user not found")
		return ap.User(user_id=rec[0], email="", display_name=rec[1] or rec[0])




def serve():
	srv = grpc.server(futures.ThreadPoolExecutor(max_workers=8))
	apg.add_AuthServiceServicer_to_server(Auth(), srv)
	srv.add_insecure_port("[::]:50051")
	srv.start(); print("auth-svc on :50051"); srv.wait_for_termination()