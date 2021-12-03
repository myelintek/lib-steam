import base64
import os
import json
import threading
from mlsteam.api import MyelindlApi
from mlsteam.mlsteam_backend import ApiClient
from mlsteam import envs
from mlsteam.run import Run
from mlsteam.mlsteam_backend import (
    RunBackend,
    DiskCache,
)
from mlsteam.exceptions import (
    MLSteamMissingApiTokenException,
    MLSteamInvalidApiTokenException,
    MLSteamMissingProjectNameException,
)


def init(project_name=None, api_token=None):
    apiclient = ApiClient(api_token=api_token)
    project_uuid = project_name_lookup(apiclient, project_name)
    # Run
    run_id = apiclient.create_run(project_uuid)

    run_lock = threading.RLock()

    stdout_path = "monitoring/stdout"
    stderr_path = "monitoring/stderr"
    traceback_path = "monitoring/traceback"
    background_jobs = []

    run_backend = RunBackend(
        run_id=run_id,
        apiclient=apiclient,
        cache=DiskCache(),
        lock=run_lock,
        background_jobs=background_jobs,
        sleep_time=5
    )

    _run = Run(
        run_id,
        run_backend,
        run_lock,
        project_uuid
    )
    _run.start()
    return _run


def project_name_lookup(apiclient, name=None):
    if not name:
        name = os.getenv(envs.PROJECT_ENV)
    if not name:
        raise MLSteamMissingProjectNameException()
    return apiclient.get_project(name)
