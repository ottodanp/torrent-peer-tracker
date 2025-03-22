CREATE TABLE IF NOT EXISTS torrents (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    infohash_v1 TEXT UNIQUE NOT NULL,
    name TEXT,
    num_seeds INTEGER,
    num_leeches INTEGER
);

CREATE TABLE IF NOT EXISTS peers (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    torrent_id INTEGER,
    ip TEXT NOT NULL,
    port INTEGER,
    connection_type TEXT,
    uploaded INTEGER,
    downloaded INTEGER,
    asn_number INTEGER,
    asn_name TEXT,
    country TEXT,
    FOREIGN KEY (torrent_id) REFERENCES torrents (id) ON DELETE CASCADE
);

CREATE TABLE IF NOT EXISTS trackers (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    torrent_id INTEGER,
    url TEXT NOT NULL,
    FOREIGN KEY (torrent_id) REFERENCES torrents (id) ON DELETE CASCADE
);
