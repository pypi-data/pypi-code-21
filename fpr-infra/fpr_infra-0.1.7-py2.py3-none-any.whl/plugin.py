# coding: utf-8

"""
    Implements some pytest fixtures.

    testinfra_host_getter : function to create host instance fixture
        @pytest.fixture(scope="module")
        def testinfra_host(testinfra_host_getter):
            aws_image = "python3.6.3_uwsgi"
            aws_identity_file = "/home/studiogdo/.ssh/fpr.pem"
            kwargs = {other aws instance parameters}
            return testinfra_host_getter(aws_image, aws_identity_file, **kwargs)

"""

import pytest
import testinfra
import time

from paramiko.ssh_exception import NoValidConnectionsError

from .aws import EC2

MAX_RETRIES = 20


@pytest.fixture(scope="session")
def testinfra_host_getter(request):
    def testinfra_host(aws_image, aws_identity_file, termination=True, **kwargs):
        sleep = kwargs.pop("sleep", None)

        print(f'Create EC2 instance on {aws_image}', end='')
        instance = EC2.create_instance(pattern=aws_image, **kwargs)
        instance.wait_until_running()

        retry = 0
        host = None
        while retry < MAX_RETRIES:
            try:
                host_name = instance.public_dns_name
                host = testinfra.get_host(f"paramiko://ubuntu@{host_name}?ssh_identity_file={aws_identity_file}")
                host.ec2_instance = instance
                host.exists("pwd")
                break
            except NoValidConnectionsError:
                time.sleep(5)
                retry += 1
                print('.', end='')

        def fin():
            if termination:
                instance.terminate()

        request.addfinalizer(fin)

        if sleep:
            time.sleep(sleep)

        print('.. running')

        return host

    return testinfra_host
