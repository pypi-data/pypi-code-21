import pytest
from inukshuk import Engine, Template


def _foonator(val):
    return 'FOO' + val + 'FOO'


def test_foonator_filter_on_query():
    engine = Engine()
    engine.filters['foo'] = _foonator
    tpl = Template('How about some {{bar|foo}}')
    tpl._engine = engine
    out = tpl.render({'bar': 'woah'})
    assert out == 'How about some FOOwoahFOO'


def test_foonator_filter_on_string():
    engine = Engine()
    engine.filters['foo'] = _foonator
    tpl = Template('How about some {{"woah too"|foo}}')
    tpl._engine = engine
    out = tpl.render({'bar': 'woah'})
    assert out == 'How about some FOOwoah tooFOO'


@pytest.mark.parametrize("filter_name, value, args, expected_result", [
    ('abs', 3, None, '3'),
    ('abs', -3, None, '3'),
    ('capitalize', 'foo bar', None, 'Foo bar'),
    ('center', '1234567890', None, (' ' * 35) + '1234567890' + (' ' * 35)),
    ('center', '1234567890', [14], '  1234567890  '),
    ('center', '1234567890', [15], '  1234567890   '),
])
def test_builtin_filters(filter_name, value, args, expected_result):
    engine = Engine()

    filter_text = filter_name
    if args:
        filter_text += '(%s)' % (', '.join(map(lambda i: str(i), args)))
    tpl = Template('{{foo|%s}}' % filter_text)
    tpl._engine = engine

    out = tpl.render({'foo': value})
    assert out == expected_result
