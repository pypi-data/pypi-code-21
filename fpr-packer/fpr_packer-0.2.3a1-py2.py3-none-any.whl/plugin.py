import pytest
import testinfra
import time

from paramiko.ssh_exception import NoValidConnectionsError

from .aws import EC2

MAX_RETRIES = 20


@pytest.fixture
def termination():
    return True


@pytest.fixture
def host_instance_getter(request):
    def ec2(aws_image, aws_identity_file, termination=True):
        print('Create EC2 instance', end='')
        instance = EC2.create_instance(pattern=aws_image)
        instance.wait_until_running()

        retry = 0
        host = None
        while retry < MAX_RETRIES:
            try:
                host_name = instance.public_dns_name
                host = testinfra.get_host(f"paramiko://ubuntu@{host_name}?ssh_identity_file={aws_identity_file}")
                host.exists("pwd")
                break
            except NoValidConnectionsError:
                time.sleep(5)
                retry += 1
                print('.', end='')

        print('.. running')
        yield host

        def fin():
            if termination:
                instance.terminate()

        request.addfinalizer(fin)
        return instance

    return ec2
