import pytest
import testinfra
import time

from paramiko.ssh_exception import NoValidConnectionsError

from .aws import EC2

MAX_RETRIES = 20


def get_fixture_ec2(image, identity_file, termination=True):
    def ec2(request):
        print('Create EC2 instance', end='')
        instance = EC2.create_instance(pattern=image)
        instance.wait_until_running()

        retry = 0
        host = None
        while retry < MAX_RETRIES:
            try:
                host_name = instance.public_dns_name
                host = testinfra.get_host(f"paramiko://ubuntu@{host_name}?ssh_identity_file={identity_file}")
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

    return pytest.fixture(scope="module")(ec2)
