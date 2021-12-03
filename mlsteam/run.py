import threading

from mlsteam.mlsteam_backend import RunBackend, DiskCache
from mlsteam.mlsteam_backend import ApiClient


class Run(object):
    def __init__(self,
        run_id: str,
        run_backend: RunBackend,
        run_lock: threading.RLock,
        project_uuid: str
    ):
        self._run_id = run_id
        self._backend = run_backend
        self._run_lock = run_lock
        self._project_uuid = project_uuid

    def __getitem__(self, key):
        print("getitem, {}".format(key))
        return Config(self._processor.cache, key)

    def start(self):
        self._backend.start()
        # TODO start background jobs

    def stop(self):
        self._backend.stop()

class Config(object):
    def __init__(self, cache: DiskCache, key: str):
        self._cache = cache
        self._key = key

    def __setitem__(self, key, value):
        print("Config setitem, {}: {}".format(key, value))
        self._cache.text_log(key, value)
