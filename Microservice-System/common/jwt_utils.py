import time, uuid, jwt
from .config import JWT_SECRET, TOKEN_TTL_SECS, REVOCATION_TTL_SECS


# Simple in-memory revocation: jti -> exp
_REVOKED = {}


def issue(user_id: str, email: str, ttl: int = TOKEN_TTL_SECS) -> str:
	now = int(time.time())
	jti = str(uuid.uuid4())
	return jwt.encode({"jti": jti, "sub": user_id, "email": email, "iat": now, "exp": now+ttl}, JWT_SECRET, algorithm="HS256")


def verify(token: str):
	data = jwt.decode(token, JWT_SECRET, algorithms=["HS256"])
	# purge old
	now = int(time.time())
	for k, v in list(_REVOKED.items()):
		if v < now: del _REVOKED[k]
	if data.get("jti") in _REVOKED:
		raise jwt.InvalidTokenError("revoked")
	return data


def revoke(token: str) -> bool:
	try:
		data = jwt.decode(token, JWT_SECRET, algorithms=["HS256"], options={"verify_exp": True})
		_REVOKED[data["jti"]] = int(time.time()) + REVOCATION_TTL_SECS
		return True
	except Exception:
		return False