from sqlite3 import connect
from typing import Optional
from uuid import uuid4

from structures import PeerDetails


class Database:
    def __init__(self, db_name: str):
        self._db_name = db_name
        self._connection = connect(db_name)
        self._cursor = self._connection.cursor()

    def handle_peer(self, peer: PeerDetails):
        peer_id = self._peer_exists(peer.ip, peer.port)
        if peer_id is None:
            peer_id = self._insert_peer(peer.ip, peer.port)

        if not self._torrent_exists(peer.torrent_details.torrent_hash):
            self._insert_torrent(peer.torrent_details.torrent_hash, peer.torrent_details.torrent_name)

        self._manage_peer_transfers(peer_id, peer.torrent_details.torrent_hash, peer.uploaded, peer.downloaded)

    def create_tables(self):
        with open("up.sql", "r") as f:
            query = f.read()
            for table in query.split(";"):
                self.execute(table)
            self.commit()

    def _insert_torrent(self, torrent_hash: str, name: str):
        query = f"INSERT INTO torrents (hash, name) VALUES ('{torrent_hash}', '{name}')"
        self.execute(query)
        self.commit()

    def _insert_peer(self, ip: str, port: int) -> str:
        peer_id = str(uuid4())
        query = f"INSERT INTO peers (peer_id, ip, port) VALUES ('{peer_id}', '{ip}', {port})"
        self.execute(query)
        self.commit()
        return peer_id

    def _manage_peer_transfers(self, peer_id: str, torrent_hash: str, uploaded: int, downloaded: int):
        if self._peer_transfer_exists(peer_id, torrent_hash):
            self._update_peer_transfer(peer_id, torrent_hash, uploaded, downloaded)
        else:
            self._insert_peer_transfer(peer_id, torrent_hash, uploaded, downloaded)

    def _update_peer_transfer(self, peer_id: str, torrent_hash: str, uploaded: int, downloaded: int):
        query = f"UPDATE transfers SET peer_uploaded = {uploaded}, peer_downloaded = {downloaded} WHERE peer_id = '{peer_id}' AND torrent_hash = '{torrent_hash}'"
        self.execute(query)
        self.commit()

    def _insert_peer_transfer(self, peer_id: str, torrent_hash: str, uploaded: int, downloaded: int):
        query = f"INSERT INTO transfers (peer_id, torrent_hash, peer_uploaded, peer_downloaded) VALUES ('{peer_id}', '{torrent_hash}', {uploaded}, {downloaded})"
        self.execute(query)
        self.commit()

    def _peer_transfer_exists(self, peer_id: str, torrent_hash: str) -> bool:
        query = f"SELECT * FROM transfers WHERE peer_id = '{peer_id}' AND torrent_hash = '{torrent_hash}'"
        self.execute(query)
        return bool(self.fetchall())

    def _peer_exists(self, ip: str, port: int) -> Optional[str]:
        query = f"SELECT peer_id FROM peers WHERE ip = '{ip}' AND port = {port}"
        self.execute(query)
        result = self.fetchall()
        if result:
            return result[0][0]

    def _torrent_exists(self, torrent_hash: str) -> bool:
        query = f"SELECT * FROM torrents WHERE hash = '{torrent_hash}'"
        self.execute(query)
        return bool(self.fetchall())

    def execute(self, query: str):
        return self._cursor.execute(query)

    def fetchall(self):
        return self._cursor.fetchall()

    def commit(self):
        self._connection.commit()

    def close(self):
        self._connection.close()
