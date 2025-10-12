import os
JWT_SECRET = os.getenv("JWT_SECRET", "devsecret")
TOKEN_TTL_SECS = int(os.getenv("TOKEN_TTL_SECS", "3600"))
REVOCATION_TTL_SECS = int(os.getenv("REVOCATION_TTL_SECS", "3600"))
PRESENCE_TTL_SECS = int(os.getenv("PRESENCE_TTL_SECS", "20"))


# addresses
AUTH_ADDR = os.getenv("AUTH_ADDR", "auth:50051")
ROOM_ADDR = os.getenv("ROOM_ADDR", "room:50052")
PRESENCE_ADDR = os.getenv("PRESENCE_ADDR", "presence:50053")
MESSAGE_ADDR = os.getenv("MESSAGE_ADDR", "message:50054")
GATEWAY_BIND = os.getenv("GATEWAY_BIND", ":50055")


# sqlite paths (mounted volumes)
AUTH_DB = os.getenv("AUTH_DB", "/data/auth.db")
ROOM_DB = os.getenv("ROOM_DB", "/data/rooms.db")
MESSAGE_DB = os.getenv("MESSAGE_DB", "/data/messages.db")
PRESENCE_DB = os.getenv("PRESENCE_DB", "/data/presence.db")