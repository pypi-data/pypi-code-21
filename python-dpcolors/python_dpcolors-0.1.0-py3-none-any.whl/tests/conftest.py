import pytest


@pytest.fixture(scope='module')
def nicknames():
    return [i[:-1] for i in open('tests/nicknames.txt', encoding='utf8').readlines()]
