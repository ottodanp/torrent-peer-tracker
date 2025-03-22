from asyncio import run

from aiohttp import ClientSession


async def fetch_asn_info(session: ClientSession, asn_number: int):
    async with session.get(f"https://ipinfo.io/AS{asn_number}") as response:
        body = await response.text()

    print(body)


async def main():
    async with ClientSession() as session:
        await fetch_asn_info(session, 15169)


if __name__ == "__main__":
    run(main())
