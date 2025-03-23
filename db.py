import socket
import struct
from sqlite3 import connect, IntegrityError
from typing import Optional, Dict, Any, List, Tuple


def ip_to_uint32(ip_address: str) -> int:
    try:
        return struct.unpack("!I", socket.inet_aton(ip_address))[0]
    except OSError:
        return -1


def uint32_to_ip(ip_int: int) -> str:
    return socket.inet_ntoa(struct.pack("!I", ip_int))


class Database:
    def __init__(self, db_name: str, asn_db_name: str):
        self._db_name = db_name
        self._asn_db_name = asn_db_name
        self._connection = connect(db_name)
        self._cursor = self._connection.cursor()
        self._asn_db_connection = connect(asn_db_name)
        self._asn_db_cursor = self._asn_db_connection.cursor()

    def handle_peer_update(self, info_hash: str, peer: Dict[str, Any]) -> bool:
        ip = peer["ip"]

        peer_id = self.get_peer_id(ip, info_hash)
        if not peer_id:
            torrent_id = self.get_torrent_id(info_hash)
            if not torrent_id:
                return False

            asn_info = self.find_asn(ip)
            asn_number = asn_info["asn_number"]
            asn_name = asn_info["registered_to"]
            country = asn_info["country_code"]

            command = f"INSERT INTO peers (torrent_id, ip, port, connection_type, uploaded, downloaded, asn_number, asn_name, country) VALUES ('{torrent_id}', '{ip}', {peer['port']}, '{peer['connection']}', {peer['uploaded']}, {peer['downloaded']}, '{asn_number}', '{asn_name}', '{country}')"

            self.execute(command)
            self.commit()
            return True
        else:
            self.execute(
                f"UPDATE peers SET uploaded = {peer['uploaded']}, downloaded = {peer['downloaded']} WHERE id = '{peer_id}'")

        self.commit()
        return False

    def handle_torrent_update(self, torrent: Dict[str, Any]) -> Optional[str]:
        info_hash = torrent["infohash_v1"]
        torrent_id = self.get_torrent_id(info_hash)
        if torrent_id:
            self.execute(
                f"UPDATE torrents SET num_seeds = {torrent['num_seeds']}, num_leeches = {torrent['num_leechs']} WHERE id = '{torrent_id}'")

        else:
            self.execute(
                f"INSERT INTO torrents (infohash_v1, name, num_seeds, num_leeches) VALUES ('{info_hash}', '{torrent['name']}', {torrent['num_seeds']}, {torrent['num_leechs']})")

        self.commit()
        return torrent_id

    def insert_trackers(self, torrent_id: str, trackers: List[str]):
        for tracker in trackers:
            if self.tracker_exists(tracker, torrent_id):
                continue

            self.execute(f"INSERT INTO trackers (torrent_id, url) VALUES ('{torrent_id}', '{tracker}')")
        self.commit()

    def tracker_exists(self, tracker: str, torrent_id: str) -> bool:
        self.execute(f"SELECT * FROM trackers WHERE torrent_id = '{torrent_id}' AND url = '{tracker}'")
        return bool(self.fetchall())

    def get_peer_id(self, ip: str, infohash: str) -> Optional[str]:
        torrent_id = self.get_torrent_id(infohash)
        if not torrent_id:
            return

        self.execute(f"SELECT * FROM peers WHERE ip = '{ip}' AND torrent_id = '{torrent_id}'")
        data = self.fetchall()

        if data:
            return data[0][0]

    def get_all_peers(self) -> List[Dict[str, Any]]:
        self.execute("SELECT * FROM peers")
        data = self.fetchall()
        return [self._format_peer_data(row) for row in data]

    def get_peer_count(self) -> int:
        self.execute("SELECT COUNT(*) FROM peers")
        data = self.fetchall()
        return data[0][0]

    def get_host_count(self) -> int:
        self.execute("SELECT COUNT(DISTINCT ip) FROM peers")
        data = self.fetchall()
        return data[0][0]

    def get_all_torrents(self) -> List[Dict[str, Any]]:
        self.execute("SELECT * FROM torrents")
        data = self.fetchall()
        return [
            {
                "id": torrent[0],
                "infohash_v1": torrent[1],
                "name": torrent[2],
                "num_seeds": torrent[3],
                "num_leeches": torrent[4]
            } for torrent in data
        ]

    def get_torrent_id(self, infohash: str) -> Optional[str]:
        self.execute(f"SELECT id FROM torrents WHERE infohash_v1 = '{infohash}'")
        data = self.fetchall()

        if data:
            return data[0][0]

    def insert_asn_record(self, asn_number: int, start_ip: str, end_ip: str, country_code: str, registered_to: str):
        try:
            self.execute(
                f"INSERT INTO asn_info (asn_number, start_ip, end_ip, country_code, registered_to) VALUES ({asn_number}, '{start_ip}', '{end_ip}', '{country_code}', '{registered_to}')")
            self.commit()
        except IntegrityError:
            pass

    def find_asn(self, ip: str) -> Dict[str, Any]:
        ip_int = ip_to_uint32(ip)
        self.asn_execute(f"SELECT * FROM asn_info WHERE start_ip <= {ip_int} AND end_ip >= {ip_int}")
        data = self.asn_fetchall()

        if data:
            return self._format_asn_data(*data[0], success=True)

        return self._format_asn_data(success=False)

    def find_ips(self, asn: int) -> List[Dict[str, Any]]:
        self.execute(f"SELECT * FROM peers WHERE asn_number = {asn}")
        data = self.fetchall()
        return [self._format_peer_data(row) for row in data]

    @staticmethod
    def _format_asn_data(asn_number: int = -1, start_ip: str = "", end_ip: str = "", country_code: str = "",
                         registered_to: str = "", success: bool = False) -> Dict[str, Any]:
        return {
            "asn_number": asn_number,
            "start_ip": start_ip,
            "end_ip": end_ip,
            "country_code": country_code,
            "registered_to": registered_to,
            "success": success
        }

    def _format_peer_data(self, row: Tuple) -> Dict[str, Any]:
        return self._clean_payload({
            "id": row[0],
            "torrent_id": row[1],
            "ip": row[2],
            "port": row[3],
            "connection_type": row[4],
            "uploaded": row[5],
            "downloaded": row[6],
            "asn_number": row[7],
            "asn_name": row[8],
            "country": row[9]
        })

    @staticmethod
    def _clean_payload(data: Dict[str, Any]) -> Dict[str, Any]:
        return {k: v for k, v in data.items() if (v is not "" and v != -1)}

    def create_tables(self, target_file: str = "scripts/torrent_up.sql"):
        with open(target_file, "r") as f:
            query = f.read()
            for table in query.split(";"):
                self.execute(table)
            self.commit()

    def execute(self, query: str):
        return self._cursor.execute(query)

    def asn_execute(self, query: str):
        return self._asn_db_cursor.execute(query)

    def fetchall(self):
        return self._cursor.fetchall()

    def asn_fetchall(self):
        return self._asn_db_cursor.fetchall()

    def commit(self):
        self._connection.commit()

    def asn_commit(self):
        self._asn_db_connection.commit()

    def close(self):
        self._connection.close()
