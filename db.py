from sqlite3 import connect
from typing import Optional, Dict, Any


class Database:
    def __init__(self, db_name: str):
        self._db_name = db_name
        self._connection = connect(db_name)
        self._cursor = self._connection.cursor()

    def handle_peer_update(self, info_hash: str, peer: Dict[str, Any]):
        ip = peer["ip"]

        peer_id = self.get_peer_id(ip, info_hash)
        if not peer_id:
            torrent_id = self.get_torrent_id(info_hash)
            if not torrent_id:
                return

            self.execute(
                f"INSERT INTO peers (torrent_id, ip, port, connection_type, uploaded, downloaded) VALUES ('{torrent_id}', '{ip}', {peer['port']}, '', {peer['uploaded']}, {peer['downloaded']})")
        else:
            self.execute(
                f"UPDATE peers SET uploaded = {peer['uploaded']}, downloaded = {peer['downloaded']} WHERE id = '{peer_id}'")

        self.commit()

    def handle_torrent_update(self, torrent: Dict[str, Any]):
        info_hash = torrent["infohash_v1"]
        torrent_id = self.get_torrent_id(info_hash)
        if torrent_id:
            self.execute(
                f"UPDATE torrents SET num_seeds = {torrent['num_seeds']}, num_leechs = {torrent['num_leechs']} WHERE id = '{torrent_id}'")

        else:
            self.execute(
                f"INSERT INTO torrents (infohash_v1, name, num_seeds, num_leechs) VALUES ('{info_hash}', '{torrent['name']}', {torrent['num_seeds']}, {torrent['num_leechs']})")
        self.commit()

    def get_peer_id(self, ip: str, infohash: str) -> Optional[str]:
        torrent_id = self.get_torrent_id(infohash)
        if not torrent_id:
            return

        self.execute(f"SELECT * FROM peers WHERE ip = '{ip}' AND torrent_id = '{torrent_id}'")
        data = self.fetchall()

        if data:
            return data[0][0]

    def get_torrent_id(self, infohash: str) -> Optional[str]:
        self.execute(f"SELECT id FROM torrents WHERE infohash_v1 = '{infohash}'")
        data = self.fetchall()

        if data:
            return data[0][0]

    def create_tables(self):
        with open("up.sql", "r") as f:
            query = f.read()
            for table in query.split(";"):
                self.execute(table)
            self.commit()

    def execute(self, query: str):
        return self._cursor.execute(query)

    def fetchall(self):
        return self._cursor.fetchall()

    def commit(self):
        self._connection.commit()

    def close(self):
        self._connection.close()
