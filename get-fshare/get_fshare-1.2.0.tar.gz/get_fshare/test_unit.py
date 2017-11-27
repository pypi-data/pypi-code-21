import pytest
from .get_fshare import FS


EMAIL = 'fsharevip.taimienphi.vn@gmail.com'
PASSWORD = 'taimienphi2711'


bot = FS(EMAIL, PASSWORD)
bot.login()

URL = 'https://www.fshare.vn/file/F564TIS7CV3I'


def test_login():
    assert bot.is_alive(URL) is True


def test_get_link():
    assert bot.is_exist(URL) is True
