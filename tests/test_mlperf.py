import pexpect
import re
import os
import time
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
    ret=system("mlsteam data cp /workspace/tests/fake_dataset/file1 bk/test")
    assert ret==0

def test_data_ls():
    ret=system("mlsteam data ls bk/test")
    assert ret==0

def test_data_rm():
    ret=system("mlsteam data rm bk/test/file1")
    assert ret==0

def test_data_rb():
    ret=system("mlsteam data rb test")
    assert ret==0

def test_generate_cifar10():
    system("python3 /workspace/example/cifar10_estimator/generate_cifar10_tfrecords.py --data-dir=/workspace/cifar10")
    system("mlsteam data mb bk/cifar10")
    system("mlsteam data cp -r /workspace/cifar10/* bk/cifar10")
    system("mlsteam data ls bk/cifar10")

def test_project_create():
    system("mlsteam project create test_project cifar10")

def test_job_submit():
    ret=system("PROJECT=test_project mlsteam job submit training --job-name job1 --package-path /workspace/example/cifar10_estimator -- python2 cifar10_main.py --data-dir /dataset --job-dir /jobs --train-steps=100")
    assert ret==0

def test_job_list():
    ret=system("mlsteam job list")
    assert ret==0

def test_project_list():
    ret=system("mlsteam project list")
    assert ret==0

def test_job_status():
    job_status=os.popen("mlsteam job list | awk '/job1/ {print $8}'").read()
    job_status=job_status.rstrip()
    while job_status != "Done":
        job_status=os.popen("mlsteam job list | awk '/job1/ {print $8}'").read()
        job_status=job_status.rstrip()
        print(job_status)
        if job_status == "Running" or job_status == "Waiting" or job_status == "Initializing":
            time.sleep(60)
        elif job_status == "Error" or job_status == "Stopped":
            raise Exception('Job status: '+job_status)
        elif job_status != "Done":
            raise Exception('Unexpected job status: '+job_status)


def test_job_delete():
    job_ids=os.popen("mlsteam job list | awk '/job1/ {print $2}'").read()
    print(job_ids)
    print(job_ids.split('\n'))
    for job_id in job_ids.split('\n'):
        if job_id=='': continue
        ret=system("mlsteam job delete --job-id "+job_id)
        assert ret==0

def test_project_delete():
    proj_id=os.popen("mlsteam project list | awk '/test_project/ {print $2}'").read()
    print(proj_id)
    ret=system("mlsteam project delete --id "+proj_id)
    assert ret==0
