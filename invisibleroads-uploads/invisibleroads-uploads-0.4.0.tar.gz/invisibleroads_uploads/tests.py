from cgi import FieldStorage
from pytest import fixture

from .models import prepare_file


@fixture
def uploads_request(posts_request, uploads_config):
    yield posts_request


@fixture
def uploads_config(config):
    config.include('invisibleroads_uploads')
    yield config


def prepare_field_storage(name, x):
    field_storage = FieldStorage()
    field_storage.filename = name
    field_storage.file = prepare_file(x)
    return field_storage
