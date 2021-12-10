import platform
from bravado.requests_client import RequestsClient
from bravado.requests_client import Authenticator
from bravado.client import SwaggerClient
from mlsteam.api_clients.credential import Credential
from mlsteam.version import __version__
from mlsteam.exceptions import MLSteamInvalidProjectNameException
from pathlib import Path
from time import time
from time import sleep
import threading
import queue
ROOT_PATH = ".mlsteam"


class ConsumerThread(threading.Thread):
    def __init__(self,
        lock: threading.RLock,
        cache: "DiskCache",
        apiclient: "ApiClient",
        project_uuid: str,
        track_bucket_name: str,
        sleep_time: int
    ):
        super().__init__(daemon=True)
        self._lock = lock
        self._sleep_time = sleep_time
        self._interrupted = False
        self._event = threading.Event()
        self._is_running = False
        self._cache = cache
        self._apiclient = apiclient
        self._puuid = project_uuid
        self._track_bucket_name = track_bucket_name
        print(f"Thread, puuid: {project_uuid}, bucket_name: {track_bucket_name}")

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
                # print("consumer start")
                self.work()
                # print("consumer stop")
                if self._sleep_time > 0 and not self._interrupted:
                    print("sleep")
                    self._event.wait(timeout=self._sleep_time)
                    print("wake")
                    self._event.clear()
                    # sleep for self._sleep_time
        finally:
            self._is_running = False

    def work(self):
        # while True:
        try:
            with self._lock:
                self._cache.process(
                    self._apiclient,
                    self._track_bucket_name
                )
        except Exception as e:
            print("error in api thread: {}".format(e))


class DiskCache(object):
    def __init__(self, track_path):
        self._queue = queue.Queue()
        self.track_path = Path(ROOT_PATH, track_path)
        if not self.track_path.exists():
            self.track_path.mkdir(parents=True)

    def assign(self, key, value):
        op = QueueOp('config', {key: f"{value}"})
        self._queue.put(op)
        print("Put queue (assign), len: {}".format(self._queue.qsize()))

    def log(self, key, value):
        tm = time()
        op = QueueOp('log', {key: f"{tm}, {value}\n"})
        self._queue.put(op)
        print("Put queue (log), len: {}".format(self._queue.qsize()))

    def process(self, apiclient: "ApiClient", bucket_name: str):
        i = 100
        log_aggregate = {}
        while (not self._queue.empty()) and (i > 0):
            i = i - 1
            op = self._queue.get()
            if op.type == "config":
                self._write_config(op.content)
                for (keypath, value) in op.content.items():
                    if isinstance(value, str):
                        value = value.encode('utf-8')
                    apiclient.put_file(
                        bucket_name=bucket_name,
                        obj_path=keypath,
                        obj=value
                    )
            elif op.type == "log":
                self._write_log(op.content)
                for (key, value) in op.content.items():
                    if isinstance(value, str):
                        value = value.encode('utf-8')
                    if key in log_aggregate:
                        log_aggregate[key] = log_aggregate[key] + value
                    else:
                        log_aggregate[key] = value
        if log_aggregate:
            for (keypath, value) in log_aggregate.items():
                apiclient.put_file(
                    bucket_name=bucket_name,
                    obj_path=keypath,
                    obj=value,
                    part_offset='-1'
                )

    def _write_config(self, content):
        for (key, value) in content.items():
            key_path = self.track_path.joinpath(key)
            if not key_path.parent.exists():
                key_path.parent.mkdir(parents=True)
            with key_path.open('w') as f:
                if isinstance(value, str):
                    f.write(value.rstrip()+"\n")
                else:
                    f.write(f"{value}\n")

    def _write_log(self, content):
        for (key, value) in content.items():
            key_path = self.track_path.joinpath(f"{key}.log")
            if not key_path.parent.exists():
                key_path.parent.mkdir(parents=True)
            tm = time()
            with key_path.open('a') as f:
                f.write(f"{tm}, {value}\n")


class QueueOp(object):
    def __init__(self, optype, content):
        self._optype = optype
        self._content = content

    @property
    def type(self):
        return self._optype

    @property
    def content(self):
        return self._content


class ApiClient(object):
    def __init__(self, api_token=None):
        self.credential = Credential(api_token)
        self.http_client = create_http_client()
        self.http_client.set_api_key(
            "http://192.168.0.17:3000",
            f"Bearer {self.credential.api_token}",
            param_name="api_key",
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
            # request_headers={
            #     'Authorization': f'Bearer {self.credential.api_token}'
            # }
        )
        self._request_options = {
            'headers': {
                'Authorization': f'Bearer {self.credential.api_token}'
            }
        }
        for tag in dir(self.swagger_client):
            for _api in dir(getattr(self.swagger_client, tag)):
                print('\t{}.{}'.format(tag, _api))


    def get_project(self, name):
        result = self.swagger_client.project.listProject(
            _request_options=self._request_options,
            name=name).result()
        # TBD
        print(result)
        if result:
            project = result[0]
            if project:
                return project['uuid']
        raise MLSteamInvalidProjectNameException()

    def create_track(self, project_uuid):
        result = self.swagger_client.track.createTrack(
            _request_options=self._request_options,
            puuid=project_uuid).result()
        print(result)
        return result

    def put_file(self, bucket_name: str, obj_path: str, obj: bytes, part_offset: int = None):
        result = self.swagger_client.object.putObject(
            _request_options=self._request_options,
            bucket_name=bucket_name,
            obj_path=obj_path,
            obj=obj,
            part_offset=part_offset,
            part_size=len(obj)).result()
        print(result)
        return result


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

