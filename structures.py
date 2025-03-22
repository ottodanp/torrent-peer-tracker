class Stats:
    _total_peers_found = 0
    _total_torrents_found = 0
    _trackers = 0

    @classmethod
    def total_peers_found(cls):
        return cls._total_peers_found

    @classmethod
    def total_torrents_found(cls):
        return cls._total_torrents_found

    @classmethod
    def total_trackers_found(cls):
        return cls._trackers

    @classmethod
    def increment_peers(cls, val: int = 1):
        cls._total_peers_found += val

    @classmethod
    def increment_torrents(cls, val: int = 1):
        cls._total_torrents_found += val

    @classmethod
    def increment_trackers(cls, val: int = 1):
        cls._trackers += val
