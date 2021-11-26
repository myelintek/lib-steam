from .api import MyelindlApi

session = None
project = None


def init(project_name=None, api_token=None):
    project_name = get_project_name(project_name)
    api_token = get_api_token(api_token)
    global session, project
    session = MyelindlApi(api_token.api_address, api_token.username)
    project = session.get_project(project_name)
    return project


def get_project_name(projectname=None):
    # TBD
    return projectname


def get_api_token(token=None):
    # TBD
    return token
