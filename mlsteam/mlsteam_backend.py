import platform
from bravado.requests_client import RequestsClient
from bravado.requests_client import Authenticator
from bravado.client import SwaggerClient
from mlsteam.api_clients.credential import Credential
from mlsteam.version import __version__
from mlsteam.exceptions import MLSteamInvalidProjectNameException
import json
from pathlib import Path
from time import time
import threading
import queue
ROOT_PATH = ".mlsteam"
# import json


class TrackBackend():
    def __init__(
        self,
        track_id: str,
        project_uuid: str,
        apiclient: "ApiClient",
        # cache: "DiskCache",
        lock: threading.RLock,
        background_jobs: list,
        sleep_time: int,
    ):
        self._track_id = track_id
        self._apiclient = apiclient
        self._cache = DiskCache(f"{project_uuid}/{track_id}")
        self._consumer = ConsumerThread(self, project_uuid, track_id, sleep_time)
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
        backend: TrackBackend,
        project_uuid: str,
        track_id: str,
        sleep_time: int
    ):
        super().__init__(daemon=True)
        self._sleep_time = sleep_time
        self._interrupted = False
        self._event = threading.Event()
        self._is_running = False
        self._backend = backend
        self._puuid = project_uuid
        self._trackid = track_id
        print(f"Thread, puuid: {project_uuid}, track_id: {track_id}")

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
                    self._event.wait(timeout=self._sleep_time)
                    self._event.clear()
                    # sleep for self._sleep_time
        finally:
            self._is_running = False

    def work(self):
        # while True:
        try:
            config_data, log_data = self._backend._cache.process()
            # process_batch
            if config_data:
                print(f"process batch, config: {config_data}")
                self._backend._apiclient.post_track_config(
                    self._puuid,
                    self._trackid,
                    json.dumps(config_data)
                )
            if log_data:
                print(f"process batch, log: {log_data}")
                self._backend._apiclient.post_track_log(
                    self._puuid,
                    self._trackid,
                    json.dumps(log_data)
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
        op = QueueOp('config', {key: value})
        self._queue.put(op)
        print("Put queue (assign), len: {}".format(self._queue.qsize()))

    def log(self, key, value):
        tm = time()
        op = QueueOp('log', {key: f"{tm}, {value}\n"})
        self._queue.put(op)
        print("Put queue (log), len: {}".format(self._queue.qsize()))

    def process(self):
        i = 100
        config_content = {}
        log_content = {}
        while (not self._queue.empty()) and (i > 0):
            i = i - 1
            op = self._queue.get()
            if op.type == "config":
                config_content.update(op.content)
            elif op.type == "log":
                for (key, value) in op.content.items():
                    if key in log_content:
                        log_content[key] = log_content[key] + value
                    else:
                        log_content[key] = value
        return config_content, log_content

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
        # for _api in dir(self.swagger_client.api):
        #     print('\t' + _api)


    def get_project(self, name):
        result = self.swagger_client.api.listProjects(
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
        result = self.swagger_client.api.createTrack(
            _request_options=self._request_options,
            puuid=project_uuid).result()
        print(result)
        # TODO client API
        return result['id']

    def post_track_config(self, project_uuid, track_id, config):
        result = self.swagger_client.api.postTrackConfig(
            _request_options=self._request_options,
            puuid=project_uuid,
            tid=track_id,
            data=config).result()
        print(result)
        return result

    def post_track_log(self, project_uuid, track_id, log):
        result = self.swagger_client.api.postTrackLog(
            _request_options=self._request_options,
            puuid=project_uuid,
            tid=track_id,
            data=log).result()
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

