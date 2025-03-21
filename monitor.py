import asyncio
from typing import List, Dict, Any

from aiohttp import ClientSession

from db import Database
from structures import Stats


async def get_torrents(session: ClientSession):
    async with session.get("http://127.0.0.1:8080/api/v2/sync/maindata") as response:
        body = await response.json()

        return body["torrents"]


async def get_peers(session: ClientSession, torrent_details: Dict[str, Any]):
    torrent_hash = torrent_details["infohash_v1"]

    async with session.get(f"http://127.0.0.1:8080/api/v2/sync/torrentPeers?hash={torrent_hash}") as response:
        body = await response.json()

        return body["peers"]


async def peers_worker(session: ClientSession, active_torrent_hashes: List[Dict[str, Any]], peer_queue: asyncio.Queue):
    while True:
        for torrent_details in active_torrent_hashes:
            peers = await get_peers(session, torrent_details)
            for peer, details in peers.items():
                await peer_queue.put((torrent_details["infohash_v1"], details))

        await asyncio.sleep(2)


async def torrents_worker(session: ClientSession, database: Database, active_torrents: List[Dict[str, Any]]):
    hashes = set()
    while True:
        torrents = await get_torrents(session)
        for t_hash, details in torrents.items():
            if t_hash not in hashes:
                hashes.add(t_hash)
                database.handle_torrent_update(details)
            active_torrents.append(details)

        await asyncio.sleep(5)


async def data_worker(peer_queue: asyncio.Queue, database: Database, stats: Stats):
    hashes = set()

    while True:
        (infohash, peer) = await peer_queue.get()
        if infohash not in hashes:
            hashes.add(infohash)
            stats.increment_torrents()

        if database.handle_peer_update(infohash, peer):
            stats.increment_peers()


async def display_worker(stats: Stats):
    while True:
        print(f"Total Peers: {stats.total_peers_found()}")
        print(f"Total Torrents: {stats.total_torrents_found()}")
        await asyncio.sleep(5)


async def main():
    database = Database("tracker.db")
    database.create_tables()

    stats = Stats()

    async with ClientSession() as session:
        active_torrent_hashes = []
        peer_queue = asyncio.Queue()

        await asyncio.gather(
            torrents_worker(session, database, active_torrent_hashes),
            peers_worker(session, active_torrent_hashes, peer_queue),
            data_worker(peer_queue, database, stats),
            display_worker(stats)
        )


if __name__ == '__main__':
    asyncio.run(main())
