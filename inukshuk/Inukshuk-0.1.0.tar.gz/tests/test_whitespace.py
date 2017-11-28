import pytest
from inukshuk.lexer import (
    _lstrip_spaces_and_first_newline, _rstrip_spaces_until_newline)


@pytest.mark.parametrize("val, expected", [
    ('', ''),
    ('  ', ''),
    ('  foo', 'foo'),
    ('foo  bar', 'foo  bar'),
    ('  \n  foo  ', '  foo  '),
    ('\n', ''),
    ('\n\n', '\n'),
    ('  \n\nfoo', '\nfoo')
])
def test_lstrip(val, expected):
    actual = _lstrip_spaces_and_first_newline(val)
    assert actual == expected


@pytest.mark.parametrize("val, expected", [
    ('', ''),
    ('  ', ''),
    ('foo\n  ', 'foo\n'),
    ('foo\n bar  ', 'foo\n bar  ')
])
def test_rstrip(val, expected):
    actual = _rstrip_spaces_until_newline(val)
    assert actual == expected
