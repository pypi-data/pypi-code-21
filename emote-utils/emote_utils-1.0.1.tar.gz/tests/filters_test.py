from emote_utils import SocialsFactory

f = SocialsFactory()
value = 'hello world'


def test_normal():
    assert f.normal('this is a test.') == 'This is a test.'


def test_title():
    assert f.title(value) == value.title()


def test_upper():
    assert f.upper(value) == value.upper()


def test_lower():
    assert f.lower(value) == value.lower()
