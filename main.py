import asyncio
from typing import List

from aiohttp import ClientSession

from db import Database
from structures import PeerDetails, TorrentDetails


async def get_torrents(session: ClientSession):
    async with session.get("http://127.0.0.1:8080/api/v2/sync/maindata") as response:
        body = await response.json()

        return body["torrents"]


async def get_peers(session: ClientSession, torrent_details: TorrentDetails):
    torrent_hash = torrent_details.torrent_hash

    async with session.get(f"http://127.0.0.1:8080/api/v2/sync/torrentPeers?hash={torrent_hash}") as response:
        body = await response.json()

        return body["peers"]


async def peers_worker(session: ClientSession, active_torrent_hashes: List[TorrentDetails], peer_queue: asyncio.Queue):
    while True:
        for torrent_details in active_torrent_hashes:
            peers = await get_peers(session, torrent_details)
            for peer, details in peers.items():
                peer_details = PeerDetails(torrent_details, details["ip"], details["port"], details["uploaded"], details["downloaded"])
                await peer_queue.put(peer_details)

        await asyncio.sleep(2)


async def torrents_worker(session: ClientSession, active_torrent_hashes: List[TorrentDetails]):
    while True:
        torrents = await get_torrents(session)
        for t_hash, details in torrents.items():
            if (
                    details["num_seeds"] == 0 and details["num_leechs"] == 0
            ) or t_hash in active_torrent_hashes:
                continue

            active_torrent_hashes.append(TorrentDetails(t_hash, details["name"]))

        await asyncio.sleep(5)


async def data_worker(peer_queue: asyncio.Queue, database: Database):
    while True:
        peer = await peer_queue.get()
        database.handle_peer(peer)
        print(f"Handled peer {peer.ip}:{peer.port} for torrent {peer.torrent_details.torrent_name}")


async def main():
    database = Database("tracker.db")
    database.create_tables()

    async with ClientSession() as session:
        active_torrent_hashes = []
        peer_queue = asyncio.Queue()

        await asyncio.gather(
            torrents_worker(session, active_torrent_hashes),
            peers_worker(session, active_torrent_hashes, peer_queue),
            data_worker(peer_queue, database),
        )


if __name__ == '__main__':
    asyncio.run(main())
