CREATE TABLE IF NOT EXISTS torrents (
    hash TEXT PRIMARY KEY,
    name TEXT NOT NULL
);

CREATE TABLE IF NOT EXISTS peers (
    peer_id TEXT PRIMARY KEY,
    ip TEXT NOT NULL,
    port INTEGER NOT NULL
);

CREATE TABLE IF NOT EXISTS transfers (
    transfer_id INTEGER PRIMARY KEY AUTOINCREMENT,
    peer_id TEXT NOT NULL,
    torrent_hash TEXT NOT NULL,
    peer_downloaded INTEGER NOT NULL,
    peer_uploaded INTEGER NOT NULL,
    FOREIGN KEY (peer_id) REFERENCES peers(peer_id),
    FOREIGN KEY (torrent_hash) REFERENCES torrents(hash)
);
