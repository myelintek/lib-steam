import base64
import os
import json
import threading
from mlsteam.api import MyelindlApi
from mlsteam.consumer import ApiClient
from mlsteam import envs
from mlsteam.track import Track
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
    track_obj = apiclient.create_track(project_uuid)

    # stdout_path = "monitoring/stdout"
    # stderr_path = "monitoring/stderr"
    # traceback_path = "monitoring/traceback"
    background_jobs = []

    _track = Track(
        track_obj,
        project_uuid,
        apiclient,
        background_jobs
    )
    _track.start()
    return _track


def project_name_lookup(apiclient, name=None):
    if not name:
        name = os.getenv(envs.PROJECT_ENV)
    if not name:
        raise MLSteamMissingProjectNameException()
    return apiclient.get_project(name)
