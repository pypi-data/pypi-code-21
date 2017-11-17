import pytest
from ..cache import lrucache
from ..models import Cache


@lrucache('{0}+{1}')
def sum(a, b):
    return a + b


@pytest.mark.django_db
def test_cache():
    a = 1
    b = 2
    c = sum(a, b)

    assert c == 3

    try:
        Cache.objects.get(key="1+2")
    except:
        pytest.fail("Cache not created")
