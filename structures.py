class Stats:
    _total_peers_found = 0
    _total_torrents_found = 0

    @classmethod
    def total_peers_found(cls):
        return cls._total_peers_found

    @classmethod
    def total_torrents_found(cls):
        return cls._total_torrents_found

    @classmethod
    def increment_peers(cls):
        cls._total_peers_found += 1

    @classmethod
    def increment_torrents(cls):
        cls._total_torrents_found += 1
