import pytest

from file import MAGIC_MIME_TYPE
from file import MAGIC_NONE
from file import Magic


@pytest.fixture
def magic():
    with Magic(MAGIC_NONE) as magic:
        yield magic


def test_get_version(magic):
    assert isinstance(magic.version, int)


def test_from_buffer(magic):
    mimetype = magic.buffer(b"ehlo")
    assert mimetype == "ASCII text, with no line terminators"


def test_from_file(magic):
    mimetype = magic.file("/etc/passwd")
    assert mimetype == "ASCII text"


def test_with(magic):
    magic.setflags(MAGIC_MIME_TYPE)
    mimetype = magic.file("/etc/passwd")
    assert mimetype == "text/plain"


def test_setflags(magic):
    mimetype = magic.file("/etc/passwd")
    assert mimetype == "ASCII text"
    magic.setflags(MAGIC_MIME_TYPE)
    mimetype = magic.file("/etc/passwd")
    assert mimetype == "text/plain"
