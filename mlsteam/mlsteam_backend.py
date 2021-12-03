import platform
from bravado.requests_client import RequestsClient
from bravado.requests_client import Authenticator
from bravado.client import SwaggerClient
from mlsteam.api_clients.credential import Credential
from mlsteam.version import __version__


from pathlib import Path
from time import time
import threading
# import json


class RunBackend():
    def __init__(
        self,
        run_id: str,
        apiclient: "ApiClient",
        cache: "DiskCache",
        lock: threading.RLock,
        background_jobs: list,
        sleep_time: int,
    ):
        self._run_id = run_id
        self._apiclient = apiclient
        self._cache = cache
        self._consumer = ConsumerThread(self, sleep_time, batch_size=1000)
        self._waiting_cond = threading.Condition(lock=lock)
        self._background_jobs = background_jobs

    @property
    def cache(self):
        return self._cache

    def start(self):
        self._consumer.start()

    def stop(self):
        if self._consumer._is_running:
            self._consumer.disable_sleep()
            self._consumer.wake_up()
            self._consumer.interrupt()
        self._consumer.join()


class ConsumerThread(threading.Thread):
    def __init__(self,
        backend: RunBackend,
        sleep_time: int,
        batch_size: int
    ):
        super().__init__(daemon=True)
        self._sleep_time = sleep_time
        self._interrupted = False
        self._event = threading.Event()
        self._is_running = False
        self._backend = backend
        self._batch_size = batch_size

    def disable_sleep(self):
        self._sleep_time = 0

    def interrupt(self):
        self._interrupted = True
        self.wake_up()

    def wake_up(self):
        self._event.set()

    def run(self):
        self._is_running = True
        try:
            while not self._interrupted:
                print("consumer start")
                self.work()
                print("consumer stop")
                if self._sleep_time > 0 and not self._interrupted:
                    self._event.wait(timeout=self._sleep_time)
                    self._event.clear()
                    # sleep for self._sleep_time
        finally:
            self._is_running = False

    def work(self):
        while True:
            batch = self._backend._cache.get_batch(self._batch_size)
            if not batch:
                return
            # process_batch


class DiskCache(object):
    def __init__(self, root_path=".mlsteam"):
        self._root_path = Path(root_path)
        if not self._root_path.exists():
            self._root_path.mkdir(parents=True)

    def text_log(self, key, value):
        key_path = self._root_path.joinpath(key)
        if not key_path.parent.exists():
            key_path.parent.mkdir(parents=True)
        with key_path.open('a') as f:
            f.write_text(value.rstrip()+"\n")

    def get_batch(self, size):
        return None


class ApiClient(object):

    def __init__(self, api_token=None):
        self.credential = Credential(api_token)
        self.http_client = create_http_client()
        self.http_client.set_api_key(
            # host="http://192.168.0.17:3000",
            host=self.credential.api_address,
            api_key=f"Bearer {self.credential.api_token}",
            param_name="Authorization",
            param_in="header",
        )
        self.swagger_client = SwaggerClient.from_url(
            f"{self.credential.api_address}/api/v2/swagger.json",
            config=dict(
                validate_swagger_spec=False,
                validate_requests=False,
                validate_response=False
            ),
            http_client=self.http_client,
        )
        for _api in dir(self.swagger_client.api):
            print('\t' + _api)


    def get_project(self, name):
        result = self.swagger_client.api.listProjects(name=name).result()
        # TBD
        print(result)
        return "uuid"

    def create_run(self, project_uuid):
        # TODO client API
        return '1'


def create_http_client():
    http_client = RequestsClient()
    user_agent = (
        "mlsteam-client/{lib_version} ({system}, python {python_version})".format(
            lib_version=__version__,
            system=platform.platform(),
            python_version=platform.python_version(),
        )
    )
    http_client.session.headers.update({"User-Agent": user_agent})
    return http_client

