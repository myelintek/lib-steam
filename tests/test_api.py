import requests
import pexpect
import pytest
import json
import os
import re

headers={}
base_url='http://140.96.29.151/api'
tout=100


def setup_module(module):
    """ setup any state specific to the execution of the given module."""
    child = pexpect.spawn('mlsteam login --address 140.96.29.151 --username superuser')
    child.expect ('password:')
    child.sendline ('superuser')
    child.expect(pexpect.EOF)
    out=child.before
    exp=re.findall(b"Login success", out)
    assert exp==[b'Login success']
    config_path = os.path.join(os.getenv('HOME'), '.mlsteam', 'cred')
    with open(config_path, 'r') as cred:
        data = json.load(cred)
    headers.update({'Authorization': 'Bearer {}'.format(data['access_token'])})


def teardown_module(module):
    """ teardown any state that was previously setup with a setup_module
    method.
    """
    pytest.skip()


"""
 user account related test cases
"""
def test_user_list():
    pytest.skip()

def test_user_add():
    pytest.skip()

def test_user_inactive():
    pytest.skip()

def test_user_remove():
    pytest.skip()


"""
 project related test cases
"""
def test_project_list():
    url = '{}/{}'.format(base_url, 'projects')
    data = None
    response = requests.get(url, timeout=tout, headers=headers)
    assert response.status_code == 200


def test_project_create_private():
    pytest.skip()


def test_project_member_list():
    pytest.skip()


def test_project_member_add():
    pytest.skip()


def test_project_member_remove():
    pytest.skip()


def test_project_create_public():
    pytest.skip()


def test_project_info():
    pytest.skip()


def test_project_delete():
    pytest.skip()


"""
 work related test cases
"""
def test_work_create():
    pytest.skip()


def test_work_list():
    pytest.skip()


def test_work_info():
    pytest.skip()


def test_work_delete():
    pytest.skip()
