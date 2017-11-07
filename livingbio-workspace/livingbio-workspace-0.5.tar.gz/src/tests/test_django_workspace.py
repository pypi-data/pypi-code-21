from os.path import dirname, exists, join

import pytest

from django_workspace import local, remote, store
from .models import Test

test_file = join(dirname(__file__), "test_data/testfile.txt")


@pytest.mark.django_db
def test_store():
    test = Test()
    store(test.field, test_file)

    assert open(test.field.path).read() == open(test_file).read()
    return test.field


@pytest.mark.django_db
def test_local():
    field = test_store()

    filepath = local(field)
    assert exists(filepath)


def test_remote():
    with pytest.raises(AssertionError):
        remote(test_file)
