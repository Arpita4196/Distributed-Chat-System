PRAGMA journal_mode=WAL;
CREATE TABLE IF NOT EXISTS rooms (
	room_id TEXT PRIMARY KEY,
	name TEXT NOT NULL
);
CREATE TABLE IF NOT EXISTS members (
	room_id TEXT NOT NULL,
	user_id TEXT NOT NULL,
	PRIMARY KEY(room_id, user_id)
);