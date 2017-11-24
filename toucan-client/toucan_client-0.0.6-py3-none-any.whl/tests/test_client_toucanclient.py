import pytest

from toucan_client.client import ToucanClient

SMALL_APP_NAME = 'my-small-app'

BASE_ROUTE = 'fake.route/my-small-app'
BASE_ROUTE_2 = 'fake.route/my-small-app/'


@pytest.fixture(name='small_app', scope='function')
def gen_small_app():
    return ToucanClient(BASE_ROUTE)


def test_simple_get(small_app):
    """It should build the right URL"""
    _ = small_app.config.etl.get
    assert small_app.method == 'get'
    assert small_app.route == '{}/config/etl'.format(BASE_ROUTE)


def test_simple_get_with_baseroute_2():
    small_app = ToucanClient(BASE_ROUTE_2)
    _ = small_app.config.etl.get
    assert small_app.method == 'get'
    assert small_app.route == '{}/config/etl'.format(BASE_ROUTE)


def test_simple_get_with_stage(small_app):
    """It should build the right URL (with staging stage)"""
    small_app.stage = 'staging'
    _ = small_app.config.etl.get
    assert small_app.method == 'get'
    assert small_app.route == '{}/config/etl?stage=staging'.format(BASE_ROUTE)


def test_call(small_app, mocker):
    mock_getattr = mocker.patch('requests.get')
    mock_getattr.return_value = 1
    mock_getattr.return_value = 1
    res = small_app.config.etl.get()
    assert res == 1


def test_kwargs(small_app):
    """It should add kwargs"""
    small_app.best_character = 'Ryu'
    _ = small_app.config.etl.get
    assert small_app.kwargs == {'best_character': 'Ryu'}
