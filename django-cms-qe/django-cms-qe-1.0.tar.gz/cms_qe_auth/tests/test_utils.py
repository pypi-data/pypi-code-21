import pytest
from pytest_data import use_data

from ..utils import get_user_by_uidb64, pk_to_uidb64, uidb64_to_pk

UIDB64_TEST_DATA = (
    'pk, uid',
    [
        ('1', 'MQ'),
        ('99', 'OTk'),
        ('100', 'MTAw'),
        ('123456', 'MTIzNDU2')
    ]
)


@pytest.mark.parametrize(*UIDB64_TEST_DATA)
def test_uidb64_to_pk(pk, uid):
    assert uidb64_to_pk(uid) == pk


@pytest.mark.parametrize(*UIDB64_TEST_DATA)
def test_pk_to_uidb64(pk, uid):
    assert pk_to_uidb64(pk) == uid.encode()


@use_data(user_data={'id': 1})
def test_get_user_by_uidb64(user):
    assert user.pk == 1
    assert user == get_user_by_uidb64("MQ")


@use_data(user_data={'id': 1})
def test_get_user_by_uidb64_user_not_exits(user):
    user = get_user_by_uidb64("Mg")
    assert not user
