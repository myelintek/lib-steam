import atexit
import threading
import traceback
from mlsteam.mlsteam_backend import TrackBackend, DiskCache


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

    def __exit__(self, exc_type, exc_val, exc_tb):
        if exc_tb is not None:
            traceback.print_exception(exc_type, exc_val, exc_tb)
        self.stop()

    def __getitem__(self, key):
        return Config(self, self._backend.cache, key)

    def __setitem__(self, key, value):
        self.__getitem__(key).assign(value)

    def lock(self):
        return self._lock

    def start(self):
        atexit.register(self._shutdown_hook)
        self._backend.start()

    def stop(self):
        self._backend.stop()

    def _shutdown_hook(self):
        self.stop()


class Config(object):
    def __init__(self, track: Track, cache: DiskCache, key: str):
        self._track = track
        self._cache = cache
        self._key = key

    def __setitem__(self, key, value):
        self[key].assign(value)

    def assign(self, value):
        with self._track.lock():
            self._cache.assign(self._key, value)

    def log(self, value):
        with self._track.lock():
            self._cache.log(self._key, value)
