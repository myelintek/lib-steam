import pexpect
import re
from os import system

def test_login():
    child = pexpect.spawn('mlsteam login --address 140.96.29.151 --username superuser')
    child.expect ('password:')
    child.sendline ('superuser')
    child.expect(pexpect.EOF)
    out=child.before
    exp=re.findall(b"Login success", out)
    assert exp==[b'Login success']

def test_data_mb():
    ret=system("mlsteam data mb test")
    assert ret==0

def test_data_cp():
    ret=system("mlsteam data cp fake_dataset/file1 bk/test")
    assert ret==0

def test_data_ls():
    ret=system("mlsteam data ls bk/")
    assert ret==0

def test_data_rm():
    ret=system("mlsteam data rm bk/test/file1")
    assert ret==0

def test_data_rb():
    ret=system("mlsteam data rb test")
    assert ret==0

