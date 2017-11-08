from os.path import dirname, exists, join

import pytest
from django.db import models

from djworkspace.store import local, remote, store
from fake.models import Fake

test_file = join(dirname(__file__), "test_data/350x150.jpg")



@pytest.mark.django_db
def test_store():
    test = Fake()
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
