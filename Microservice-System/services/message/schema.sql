PRAGMA journal_mode=WAL;
CREATE TABLE IF NOT EXISTS messages (
    room_id TEXT NOT NULL,
    offset INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id TEXT NOT NULL,
    text TEXT NOT NULL,
    ts_ms INTEGER NOT NULL,
    idempotency_key TEXT NOT NULL,
    UNIQUE(room_id, idempotency_key)
);
CREATE INDEX IF NOT EXISTS idx_room_offset ON messages(room_id, offset);