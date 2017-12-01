"""Tests for feed module."""

from accern import Stream, http_client, error
from mock import Mock
import pytest

api_base = "http://http://feed-staging.accern.com/v4/stream"


class MockClient(Stream):
    """Mock client for feed."""

    def __init__(self):
        self.http_client = Mock(http_client.HTTPClient)
        self.http_client.name = 'mockclient'
        self.requestor = Stream(client=self.http_client)
        self.api_base = api_base

    def mock_response(self, return_body, return_code, requestor=None):
        """Mock http response. Take return body and code."""
        if not requestor:
            requestor = self.requestor

        self.requestor.request = Mock(
            return_value=(return_body, return_code, {}))

client = MockClient()


@pytest.fixture(scope="module")
def client():
    return MockClient()


def test_success_with_api_key(client):
    client = Stream()
    client.token = '495b1526f016824b037b4e1f0aefdbb3'
    rbody, rcode, rheader = client.request('get')
    assert rcode == 200


def test_fails_without_api_key(client):
    """An authentication error will be raised."""
    client.token = None
    pytest.raises(error.AuthenticationError, client.request)


def test_fails_with_invalid_method(client):
    """An conection failed error will be raised."""
    client.token = 'some key'
    with pytest.raises(error.APIConnectionError, match=r"Unrecognized HTTP method .*"):
        client.request(method='wrong')
