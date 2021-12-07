import base64
import os
import json
import threading
from mlsteam.api import MyelindlApi
from mlsteam.mlsteam_backend import ApiClient
from mlsteam import envs
from mlsteam.track import Track
from mlsteam.mlsteam_backend import (
    TrackBackend,
)
from mlsteam.exceptions import (
    MLSteamMissingApiTokenException,
    MLSteamInvalidApiTokenException,
    MLSteamMissingProjectNameException,
)


def init(project_name=None, api_token=None):
    apiclient = ApiClient(api_token=api_token)
    project_uuid = project_name_lookup(apiclient, project_name)
    print(project_uuid)
    # Track
    track_id = apiclient.create_track(project_uuid)

    track_lock = threading.RLock()

    stdout_path = "monitoring/stdout"
    stderr_path = "monitoring/stderr"
    traceback_path = "monitoring/traceback"
    background_jobs = []

    track_backend = TrackBackend(
        track_id=track_id,
        project_uuid=project_uuid,
        apiclient=apiclient,
        lock=track_lock,
        background_jobs=background_jobs,
        sleep_time=5
    )

    _track = Track(
        track_id,
        track_backend,
        track_lock,
        project_uuid
    )
    _track.start()
    return _track


def project_name_lookup(apiclient, name=None):
    if not name:
        name = os.getenv(envs.PROJECT_ENV)
    if not name:
        raise MLSteamMissingProjectNameException()
    return apiclient.get_project(name)
