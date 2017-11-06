import os
import pytest
import uuid

from blackfynn import Blackfynn

def pytest_addoption(parser):
    parser.addoption("--devserver", default=[], help=("Test against dev server (not local)"))

def pytest_generate_tests(metafunc):
    print metafunc.fixturenames
    use_dev = False
    if 'devserver' in metafunc.fixturenames:
        use_dev = metafunc.config.option.devserver
    metafunc.parametrize("use_dev", [use_dev], scope='session')
    

@pytest.fixture(scope='session')
def client(use_dev):
    """
    Login via API, return client. Login information, by default, will be taken from
    environment variables, so ensure those are set properly before testing. Alternatively,
    to force a particular user, adjust input arguments as necessary.
    """
    bf = Blackfynn(
        api_token='43db6624-68ac-4e60-8ee6-d248b0db0445',
        api_secret='c1a421e3-6f2e-4387-8d3b-e0596bd6a711'
    )
    # get organizations
    orgs = bf.organizations()
    print 'organizations =', orgs
    assert len(orgs) > 0

    # explicitly set context to Blackfyn org
    assert bf.context is not None
    return bf

@pytest.fixture(scope='session')
def client2(use_dev):
    bf = Blackfynn(
        api_token='43db6624-68ac-4e60-8ee6-d248b0db0445',
        api_secret='c1a421e3-6f2e-4387-8d3b-e0596bd6a711'
    )
    # get organizations
    orgs = bf.organizations()
    assert len(orgs) > 0

    # explicitly set context to Blackfyn org
    assert bf.context is not None
    return bf


@pytest.fixture(scope='session')
def superuser_client(use_dev):
    """
    Client using super-admin permissions
    """
    bf = Blackfynn(
        api_token='c535152c-0564-4865-8fa0-addebb07e020',
        api_secret='89d1a675-a876-4e16-8dd7-b54f58ff3c8e'
    )
    assert bf.profile.is_super_admin
    return bf


@pytest.fixture(scope='session')
def dataset(use_dev, client, superuser_client):
    """
    Test Dataset to be used by other tests.
    """

    # collection of all datasets
    n_ds = len(client.datasets())

    # create test dataset
    ds = client.create_dataset("test dataset {}".format(uuid.uuid4()))
    assert ds.exists
    assert len(client.datasets()) == n_ds + 1

    # surface test dataset to other functions
    yield ds

    # remove
    superuser_client._api.datasets.delete(ds)

    assert len(client.datasets()) == n_ds
    assert not ds.exists
    assert not hasattr(ds, 'parent')

@pytest.fixture(scope='session')
def test_organization(client):
    return filter(lambda o: o.name == 'Test Organization', client.organizations())[0]

def test_login(client):
    email = os.environ.get('BLACKFYNN_USER')
    profile = client.profile
    print "profile = ", profile
    assert profile['email'] == email

