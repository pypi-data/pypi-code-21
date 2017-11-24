import pytest
from django.contrib.messages.storage.fallback import FallbackStorage
from django.test import RequestFactory
from pytest_data import get_data


@pytest.fixture
def post_request_empty(request):
    rf = RequestFactory()
    rq = rf.post('', get_data(request, 'post_request_empty_data', {}))
    setattr(rq, 'session', True)
    messages = FallbackStorage(rq)
    setattr(rq, '_messages', messages)
    return rq
