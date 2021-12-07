import threading

from mlsteam.mlsteam_backend import TrackBackend, DiskCache
from mlsteam.mlsteam_backend import ApiClient


class Track(object):
    def __init__(self,
        track_id: str,
        track_backend: TrackBackend,
        track_lock: threading.RLock,
        project_uuid: str
    ):
        self._track_id = track_id
        self._backend = track_backend
        self._lock = track_lock
        self._project_uuid = project_uuid

    def __getitem__(self, key):
        print("getitem, {}".format(key))
        return Config(self, self._backend.cache, key)

    def __setitem__(self, key, value):
        self.__getitem__(key).assign(value)

    def lock(self):
        return self._lock

    def start(self):
        self._backend.start()
        # TODO start background jobs

    def stop(self):
        self._backend.stop()

class Config(object):
    def __init__(self, track: Track, cache: DiskCache, key: str):
        self._track = track
        self._cache = cache
        self._key = key

    def __setitem__(self, key, value):
        print("Config setitem, {}: {}".format(key, value))
        self[key].assign(value)

    def assign(self, value):
        print("Config assign, {}: {}".format(self._key, value))
        with self._track.lock():
            self._cache.assign(self._key, value)

    def log(self, value):
        print("Config log, {}: {}".format(self._key, value))
        with self._track.lock():
            self._cache.log(self._key, value)
