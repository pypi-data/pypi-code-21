from django.contrib.auth.models import AnonymousUser

from rf_django_misc.test import get_test_request


def test_get_test_request():
    request = get_test_request()
    assert request.user.is_anonymous()
    assert request.session == {}
    assert not request.GET
    assert not request.POST


def test_get_test_request_with_data():
    request = get_test_request(data={'hello': '24'})
    assert request.user.is_anonymous()
    assert request.session == {}
    assert request.GET == {'hello': ['24', ]}
    assert not request.POST


def test_get_test_request_with_session_data():
    request = get_test_request(session_data={'hello': '24'})
    assert request.user.is_anonymous()
    assert request.session == {'hello': '24'}
    assert not request.GET
    assert not request.POST


def test_get_test_request_with_user():
    user = 'JustAString'
    request = get_test_request(user=user)
    assert request.user is user
    assert request.session == {}
    assert not request.GET
    assert not request.POST
