class TorrentDetails:
    _torrent_hash: str
    _torrent_name: str

    def __init__(self, torrent_hash: str, torrent_name: str):
        self._torrent_hash = torrent_hash
        self._torrent_name = torrent_name

    @property
    def torrent_hash(self) -> str:
        return self._torrent_hash

    @property
    def torrent_name(self) -> str:
        return self._torrent_name


class PeerDetails:
    _torrent_details: TorrentDetails
    _ip: str
    _port: int
    _uploaded: int
    _downloaded: int

    def __init__(self, torrent_details: TorrentDetails, ip: str, port: int, uploaded: int, downloaded: int):
        self._torrent_details = torrent_details
        self._ip = ip
        self._port = port
        self._uploaded = uploaded
        self._downloaded = downloaded

    @property
    def torrent_details(self) -> TorrentDetails:
        return self._torrent_details

    @property
    def ip(self) -> str:
        return self._ip

    @property
    def port(self) -> int:
        return self._port

    @property
    def uploaded(self) -> int:
        return self._uploaded

    @property
    def downloaded(self) -> int:
        return self._downloaded
