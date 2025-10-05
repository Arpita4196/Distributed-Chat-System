-- USERS TABLE
CREATE TABLE IF NOT EXISTS users (
    id SERIAL PRIMARY KEY,
    username VARCHAR(255) UNIQUE NOT NULL,
    password VARCHAR(255) NOT NULL
);

-- ROOMS TABLE
CREATE TABLE IF NOT EXISTS rooms (
    id SERIAL PRIMARY KEY,
    name VARCHAR(255) UNIQUE NOT NULL
);

-- MESSAGES TABLE  (no timestamp column)
CREATE TABLE IF NOT EXISTS messages (
    id SERIAL PRIMARY KEY,
    room_id VARCHAR(255) NOT NULL,   -- e.g. 'general'
    username VARCHAR(255) NOT NULL,  -- sender username
    text TEXT NOT NULL
);

-- PRESENCE TABLE
CREATE TABLE IF NOT EXISTS presence (
    id SERIAL PRIMARY KEY,
    username VARCHAR(255) NOT NULL,
    status VARCHAR(50) NOT NULL      -- 'online', 'offline', etc.
);
