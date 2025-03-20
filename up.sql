CREATE TABLE IF NOT EXISTS torrents (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    infohash_v1 TEXT UNIQUE NOT NULL,
    name TEXT,
    num_seeds INTEGER,
    num_leechs INTEGER
);

CREATE TABLE IF NOT EXISTS peers (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    torrent_id INTEGER,
    ip TEXT NOT NULL,
    port INTEGER,
    connection_type TEXT,
    uploaded INTEGER,
    downloaded INTEGER,
    FOREIGN KEY (torrent_id) REFERENCES torrents (id) ON DELETE CASCADE
);