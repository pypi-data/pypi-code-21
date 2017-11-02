"""
This test suite wants to cover a massive file validator scenario.

The `check_text()` will be called for fast results and simple test cases
"""

from tests import parametrize_with_names
from wscheck.checker import WhitespaceChecker


CHECK_COUNT = 1000
LINES_PER_TEXT = 100
DEFAULT_LINE = 'lorem \tipsum' * 5  # 60 chars
DEFAULT_EOL = '\n'


def _line(prefix='', suffix='', eol=DEFAULT_EOL):
    return '{prefix}{line}{suffix}{eol}'.format(
        prefix=prefix,
        line=DEFAULT_LINE,
        suffix=suffix,
        eol=eol,
    )


def _text(standard_line=None, head='', center='', foot=''):
    if standard_line is None:
        standard_line = _line()

    part1_lines = int(LINES_PER_TEXT / 2)
    part2_lines = LINES_PER_TEXT - part1_lines

    return '{head}{part1}{center}{part2}{foot}'.format(
        head=head,
        part1=''.join([standard_line] * part1_lines),
        center=center,
        part2=''.join([standard_line] * part2_lines),
        foot=foot,
    )


def _measure(benchmark, text, expected_rules, expected_issue_count):
    def measured_call():
        checker = WhitespaceChecker()

        for _ in range(CHECK_COUNT):
            checker.check_text(text)

        assert expected_issue_count == len(checker.issues)
        assert set(expected_rules) == {issue['rule'] for issue in checker.issues}

    benchmark(measured_call)


@parametrize_with_names('text,expected_rules,expected_issue_count', {
    '':  [_text(_line()),    [], 0],     # noqa: E241,E501
})
def test_valid(benchmark, text, expected_rules, expected_issue_count):
    _measure(benchmark, text, expected_rules, expected_issue_count)


@parametrize_with_names('text,expected_rules,expected_issue_count', {
    'head_cr':      [_text(head=_line(eol='\r')),       ['WSC001'], CHECK_COUNT],                   # noqa: E241,E501
    'head_cr+lf':   [_text(head=_line(eol='\r\n')),     ['WSC001'], CHECK_COUNT],                   # noqa: E241,E501
    'center_cr':    [_text(center=_line(eol='\r')),     ['WSC001'], CHECK_COUNT],                   # noqa: E241,E501
    'center_cr+lf': [_text(center=_line(eol='\r\n')),   ['WSC001'], CHECK_COUNT],                   # noqa: E241,E501
    'foot_cr':      [_text(foot=_line(eol='\r')),       ['WSC001'], CHECK_COUNT],                   # noqa: E241,E501
    'foot_cr+lf':   [_text(foot=_line(eol='\r\n')),     ['WSC001'], CHECK_COUNT],                   # noqa: E241,E501
    'all_cr':       [_text(_line(eol='\r')),            ['WSC001'], CHECK_COUNT * LINES_PER_TEXT],  # noqa: E241,E501
    'all_cr+lf':    [_text(_line(eol='\r\n')),          ['WSC001'], CHECK_COUNT * LINES_PER_TEXT],  # noqa: E241,E501
})
def test_wsc001(benchmark, text, expected_rules, expected_issue_count):
    """
    Bad line ending
    """
    _measure(benchmark, text, expected_rules, expected_issue_count)


@parametrize_with_names('text,expected_rules,expected_issue_count', {
    'head_tab-1x1':         [_text(head=_line(suffix='\t')),        ['WSC002'], CHECK_COUNT],                   # noqa: E241,E501
    'head_tab-1x15':        [_text(head=_line(suffix='\t' * 15)),   ['WSC002'], CHECK_COUNT],                   # noqa: E241,E501
    'head_space+tab-1x1':   [_text(head=_line(suffix=' \t')),       ['WSC002'], CHECK_COUNT],                   # noqa: E241,E501
    'head_space+tab-1x15':  [_text(head=_line(suffix=' \t' * 15)),  ['WSC002'], CHECK_COUNT],                   # noqa: E241,E501
    'head_space-1x1':       [_text(head=_line(suffix=' ')),         ['WSC002'], CHECK_COUNT],                   # noqa: E241,E501
    'head_space-1x15':      [_text(head=_line(suffix=' ' * 15)),    ['WSC002'], CHECK_COUNT],                   # noqa: E241,E501
    'head_space-21x1':      [_text(head=_line(suffix=' ') * 21),    ['WSC002'], CHECK_COUNT * 21],              # noqa: E241,E501
    'center_space-1x1':     [_text(center=_line(suffix=' ')),       ['WSC002'], CHECK_COUNT],                   # noqa: E241,E501
    'center_space-1x15':    [_text(center=_line(suffix=' ' * 15)),  ['WSC002'], CHECK_COUNT],                   # noqa: E241,E501
    'center_space-21x1':    [_text(center=_line(suffix=' ') * 21),  ['WSC002'], CHECK_COUNT * 21],              # noqa: E241,E501
    'foot_space-1x1':       [_text(foot=_line(suffix=' ')),         ['WSC002'], CHECK_COUNT],                   # noqa: E241,E501
    'foot_space-1x15':      [_text(foot=_line(suffix=' ' * 15)),    ['WSC002'], CHECK_COUNT],                   # noqa: E241,E501
    'foot_space-21x1':      [_text(foot=_line(suffix=' ') * 21),    ['WSC002'], CHECK_COUNT * 21],              # noqa: E241,E501
    'all_space-1x1':        [_text(_line(suffix=' ')),              ['WSC002'], CHECK_COUNT * LINES_PER_TEXT],  # noqa: E241,E501
})
def test_wsc002(benchmark, text, expected_rules, expected_issue_count):
    """
    Tailing whitespace
    """
    _measure(benchmark, text, expected_rules, expected_issue_count)


@parametrize_with_names('text,expected_rules,expected_issue_count', {
    'head_space-1x1':       [_text(head=_line(prefix=' ')),         ['WSC003'], CHECK_COUNT],                   # noqa: E241,E501
    'head_space-1x15':      [_text(head=_line(prefix=' ' * 15)),    ['WSC003'], CHECK_COUNT],                   # noqa: E241,E501
    'head_space-21x1':      [_text(head=_line(prefix=' ') * 21),    ['WSC003'], CHECK_COUNT * 21],              # noqa: E241,E501
    'center_space-1x1':     [_text(center=_line(prefix=' ')),       ['WSC003'], CHECK_COUNT],                   # noqa: E241,E501
    'center_space-1x15':    [_text(center=_line(prefix=' ' * 15)),  ['WSC003'], CHECK_COUNT],                   # noqa: E241,E501
    'center_space-21x1':    [_text(center=_line(prefix=' ') * 21),  ['WSC003'], CHECK_COUNT * 21],              # noqa: E241,E501
    'foot_space-1x1':       [_text(foot=_line(prefix=' ')),         ['WSC003'], CHECK_COUNT],                   # noqa: E241,E501
    'foot_space-1x15':      [_text(foot=_line(prefix=' ' * 15)),    ['WSC003'], CHECK_COUNT],                   # noqa: E241,E501
    'foot_space-21x1':      [_text(foot=_line(prefix=' ') * 21),    ['WSC003'], CHECK_COUNT * 21],              # noqa: E241,E501
    'all_space-1x1':        [_text(_line(prefix=' ')),              ['WSC003'], CHECK_COUNT * LINES_PER_TEXT],  # noqa: E241,E501
})
def test_wsc003(benchmark, text, expected_rules, expected_issue_count):
    """
    Indentation is not multiple of 2
    """
    _measure(benchmark, text, expected_rules, expected_issue_count)


@parametrize_with_names('text,expected_rules,expected_issue_count', {
    'head_tab-1x1':       [_text(head=_line(prefix='\t')),         ['WSC004'], CHECK_COUNT],                    # noqa: E241,E501
    'head_tab-1x15':      [_text(head=_line(prefix='\t' * 15)),    ['WSC004'], CHECK_COUNT],                    # noqa: E241,E501
    'head_tab-21x1':      [_text(head=_line(prefix='\t') * 21),    ['WSC004'], CHECK_COUNT * 21],               # noqa: E241,E501
    'center_tab-1x1':     [_text(center=_line(prefix='\t')),       ['WSC004'], CHECK_COUNT],                    # noqa: E241,E501
    'center_tab-1x15':    [_text(center=_line(prefix='\t' * 15)),  ['WSC004'], CHECK_COUNT],                    # noqa: E241,E501
    'center_tab-21x1':    [_text(center=_line(prefix='\t') * 21),  ['WSC004'], CHECK_COUNT * 21],               # noqa: E241,E501
    'foot_tab-1x1':       [_text(foot=_line(prefix='\t')),         ['WSC004'], CHECK_COUNT],                    # noqa: E241,E501
    'foot_tab-1x15':      [_text(foot=_line(prefix='\t' * 15)),    ['WSC004'], CHECK_COUNT],                    # noqa: E241,E501
    'foot_tab-21x1':      [_text(foot=_line(prefix='\t') * 21),    ['WSC004'], CHECK_COUNT * 21],               # noqa: E241,E501
    'all_tab-1x1':        [_text(_line(prefix='\t')),              ['WSC004'], CHECK_COUNT * LINES_PER_TEXT],   # noqa: E241,E501
})
def test_wsc004(benchmark, text, expected_rules, expected_issue_count):
    """
    Indentation with non-space character
    """
    _measure(benchmark, text, expected_rules, expected_issue_count)


@parametrize_with_names('text,expected_rules,expected_issue_count', {
    '':    [_text(foot=_line(eol='')), ['WSC005'], CHECK_COUNT],  # noqa: E241,E501
})
def test_wsc005(benchmark, text, expected_rules, expected_issue_count):
    """
    No newline at end of file
    """
    _measure(benchmark, text, expected_rules, expected_issue_count)


@parametrize_with_names('text,expected_rules,expected_issue_count', {
    '1-lf':     [_text(_line(), foot=DEFAULT_EOL),      ['WSC006'], CHECK_COUNT],  # noqa: E241,E501
    '15-lf':    [_text(_line(), foot=DEFAULT_EOL * 15), ['WSC006'], CHECK_COUNT],  # noqa: E241,E501
})
def test_wsc006(benchmark, text, expected_rules, expected_issue_count):
    """
    Too many newline at end of file
    """
    _measure(benchmark, text, expected_rules, expected_issue_count)


@parametrize_with_names('text,expected_rules,expected_issue_count', {
    '':    [_text(head=_line(eol='')),  ['WSC007'], CHECK_COUNT],  # noqa: E241,E501
})
def test_wsc007(benchmark, text, expected_rules, expected_issue_count):
    """
    File begins with newline
    """
    _measure(benchmark, text, expected_rules, expected_issue_count)
