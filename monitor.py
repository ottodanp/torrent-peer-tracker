import asyncio
from typing import List, Dict, Any

from aiohttp import ClientSession

from db import Database


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


async def data_worker(peer_queue: asyncio.Queue, database: Database):
    while True:
        (infohash, peer) = await peer_queue.get()
        database.handle_peer_update(infohash, peer)
        print(peer)


async def main():
    database = Database("tracker.db")
    database.create_tables()

    async with ClientSession() as session:
        active_torrent_hashes = []
        peer_queue = asyncio.Queue()

        await asyncio.gather(
            torrents_worker(session, database, active_torrent_hashes),
            peers_worker(session, active_torrent_hashes, peer_queue),
            data_worker(peer_queue, database),
        )


if __name__ == '__main__':
    asyncio.run(main())
