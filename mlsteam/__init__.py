import base64
import click
import os
import json
import threading
import mlsteam.keras
import mlsteam.stparams
from mlsteam.api import MyelindlApi
from mlsteam.consumer import ApiClient
from mlsteam import envs
from mlsteam.version import __version__
from mlsteam.track import Track
from mlsteam.exceptions import (
    MLSteamMissingApiTokenException,
    MLSteamInvalidApiTokenException,
    MLSteamMissingProjectNameException,
)


def init(project_name=None, api_token=None, debug=False):
    click.echo("mlsteam-client v{}".format(__version__))
    apiclient = ApiClient(api_token=api_token)
    project_uuid = project_name_lookup(apiclient, project_name)
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
        background_jobs,
        debug=debug
    )
    _track.start()
    return _track


def project_name_lookup(apiclient, name=None):
    if not name:
        name = os.getenv(envs.PROJECT_ENV)
        if name:
            click.echo("project name({}): {}".format(envs.PROJECT_ENV, name))
    if not name:
        raise MLSteamMissingProjectNameException()
    return apiclient.get_project(name)
