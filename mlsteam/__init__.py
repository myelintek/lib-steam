import base64
import os
import json
from mlsteam.api import MyelindlApi
from mlsteam import envs
from mlsteam.exceptions import (
    MLSteamMissingApiTokenException,
    MLSteamInvalidApiTokenException,
    MLSteamMissingProjectNameException,
)

session = None
project = None


def init(project_name=None, api_token=None):
    project_name = get_project_name(project_name)
    api_token = get_api_token(api_token)
    global session, project
    session = MyelindlApi(api_token.api_address, api_token.username)
    project = session.get_project(project_name)
    return project


def get_project_name(name=None):
    if not name:
        name = os.getenv(envs.PROJECT_ENV)
    if not name:
        raise MLSteamMissingProjectNameException()
    return name


def get_api_token(token=None):
    if token is None:
        token = os.getenv(envs.API_TOKEN_ENV)
    if token is None:
        raise MLSteamMissingApiTokenException()

    token_dict = api_token_to_dict(token)
    if "api_address" not in token_dict:
        raise MLSteamInvalidApiTokenException()
    token_address = token_dict["api_address"]
    return token_address, token


def api_token_to_dict(api_token):
    try:
        tokend = {}
        tokens = api_token.split('.')
        if len(tokens) != 3:
            raise MLSteamInvalidApiTokenException()
        tokend = token_decode(tokens[0])
        tokend.update(token_decode(tokens[1]))
        return tokend
    except Exception:
        raise MLSteamInvalidApiTokenException()


def token_decode(token):
    try:
        tokenb = token.encode() + b'=' * (-len(token) % 4)
        return json.loads(base64.b64decode(tokenb).decode('utf-8'))
    except Exception:
        raise MLSteamInvalidApiTokenException()
