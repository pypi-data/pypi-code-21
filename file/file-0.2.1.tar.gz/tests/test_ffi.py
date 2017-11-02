import pytest

from file import MAGIC_MIME
from file import MAGIC_MIME_TYPE
from file import MAGIC_NONE
from file import magic_buffer
from file import magic_close
from file import magic_file
from file import magic_load
from file import magic_open
from file import magic_setflags
from file import magic_version


def test_version():
    version = magic_version()
    assert isinstance(version, int)


def test_open():
    cookie = magic_open(MAGIC_NONE)
    assert cookie is not None


def test_close():
    cookie = magic_open(MAGIC_NONE)
    assert cookie is not None
    magic_close(cookie)


def test_load():
    cookie = magic_open(MAGIC_NONE)
    assert cookie is not None
    with pytest.raises(ValueError):
        magic_load(cookie, b"/etc/magic_database")
    magic_load(cookie)


def test_file():
    cookie = magic_open(MAGIC_NONE)
    assert cookie is not None

    magic_load(cookie)
    mimetype = magic_file(cookie, b"/etc/passwd")
    assert mimetype == "ASCII text"


def test_buffer():
    cookie = magic_open(MAGIC_NONE)
    assert cookie is not None
    magic_load(cookie)

    mimetype = magic_buffer(cookie, b"")
    assert mimetype == "empty"

    mimetype = magic_buffer(cookie, b"kittens")
    assert mimetype == "ASCII text, with no line terminators"

    mimetype = magic_buffer(cookie, b"\x89\x50\x4E\x47\x0D\x0A\x1A\x0A")
    assert mimetype == "PNG image data"


def test_setflags():
    cookie = magic_open(MAGIC_NONE)
    assert cookie is not None

    magic_load(cookie)

    mimetype = magic_buffer(cookie, b"\x89\x50\x4E\x47\x0D\x0A\x1A\x0A")
    assert mimetype == "PNG image data"

    magic_setflags(cookie, MAGIC_MIME_TYPE)
    mimetype = magic_buffer(cookie, b"\x89\x50\x4E\x47\x0D\x0A\x1A\x0A")
    assert mimetype == "image/png"

    magic_setflags(cookie, MAGIC_MIME)
    mimetype = magic_buffer(cookie, b"\x89\x50\x4E\x47\x0D\x0A\x1A\x0A")
    assert mimetype == "image/png; charset=binary"
