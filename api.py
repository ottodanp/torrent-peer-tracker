from typing import List, Dict, Any

from quart import Quart

from db import Database


class TrackerAPI:
    _db: Database
    _quart: Quart

    def __init__(self, db: Database):
        self._db = db
        self._quart = Quart(__name__)
        self._quart.route("/peers")(self.all_peers)
        self._quart.route("/torrents")(self.all_torrents)
        self._quart.route("/ip-to-asn/<ip>")(self.ip_to_asn)
        self._quart.route("/asn-to-ips/<asn>")(self.asn_to_ips)
        self._quart.route("/peer-count")(self.peer_count)

    # min upload/download, asn number, asn name, country
    async def all_peers(self) -> List[Dict[str, Any]]:
        return self._db.get_all_peers()

    async def all_torrents(self) -> List[Dict[str, Any]]:
        return self._db.get_all_torrents()

    async def ip_to_asn(self, ip: str) -> Dict[str, Any]:
        return self._db.find_asn(ip)

    async def asn_to_ips(self, asn: int) -> List[Dict[str, Any]]:
        return self._db.find_ips(asn)

    async def peer_count(self) -> Dict[str, Any]:
        return {
            "peers": self._db.get_peer_count(),
            "unique_hosts": self._db.get_host_count()
        }

    def run(self):
        self._quart.run(host="0.0.0.0")


if __name__ == '__main__':
    api = TrackerAPI(Database("torrents.db", "asn.db"))
    api.run()
