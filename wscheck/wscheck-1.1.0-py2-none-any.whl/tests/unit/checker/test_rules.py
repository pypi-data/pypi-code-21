import pytest

from wscheck.checker import WhitespaceChecker


@pytest.fixture
def checker():
    return WhitespaceChecker()


class TestEof(object):
    """
    WSC005: No newline at end of file
    WSC006: Too many newline at end of file
    """

    def test_one_empty_line_is_good(self, checker):
        checker.check_text('')
        assert [] == checker.issues

    def test_two_empty_lines_is_bad(self, checker):
        checker.check_text('\n')
        assert [
            {
                'rule': 'WSC006', 'path': '<string>', 'line': 1, 'col': 1,
                'context': '', 'message_suffix': '(+1)'
            },
        ] == checker.issues

    def test_three_empty_lines_is_bad(self, checker):
        checker.check_text('\n\n')
        assert [
            {
                'rule': 'WSC006', 'path': '<string>', 'line': 1, 'col': 1,
                'context': '', 'message_suffix': '(+2)'
            },
        ] == checker.issues

    def test_one_non_empty_line_wo_lf_is_bad(self, checker):
        checker.check_text('apple')
        assert [
            {
                'rule': 'WSC005', 'path': '<string>', 'line': 1, 'col': 6,
                'context': 'apple', 'message_suffix': None
            },
        ] == checker.issues

    def test_one_empty_lines_at_end_is_good(self, checker):
        checker.check_text('apple\n')
        assert [] == checker.issues

    def test_two_empty_lines_at_end_is_bad(self, checker):
        checker.check_text('apple\n\n')
        assert [
            {
                'rule': 'WSC006', 'path': '<string>', 'line': 1, 'col': 6,
                'context': 'apple', 'message_suffix': '(+1)'
            },
        ] == checker.issues

    def test_three_empty_lines_at_end_is_bad(self, checker):
        checker.check_text('apple\n\n\n')
        assert [
            {
                'rule': 'WSC006', 'path': '<string>', 'line': 1, 'col': 6,
                'context': 'apple', 'message_suffix': '(+2)'
            },
        ] == checker.issues

    def test_two_non_empty_lines_but_missing_lf_after_last_is_bad(self, checker):
        checker.check_text('apple\norange')
        assert [
            {
                'rule': 'WSC005', 'path': '<string>', 'line': 2, 'col': 7,
                'context': 'orange', 'message_suffix': None
            },
        ] == checker.issues


class TestBof(object):
    """
    WSC007: File begins with newline
    """

    def test_one_empty_line_before_non_empty_lines_is_bad(self, checker):
        checker.check_text('\napple\n')
        assert [
            {
                'rule': 'WSC007', 'path': '<string>', 'line': 2, 'col': 1,
                'context': 'apple', 'message_suffix': None
            },
        ] == checker.issues

    def test_two_empty_line_before_non_empty_lines_is_bad(self, checker):
        checker.check_text('\n\napple\n')
        assert [
            {
                'rule': 'WSC007', 'path': '<string>', 'line': 3, 'col': 1,
                'context': 'apple', 'message_suffix': None
            },
        ] == checker.issues

    def test_three_empty_line_before_non_empty_lines_is_bad(self, checker):
        checker.check_text('\n\n\napple\n')
        assert [
            {
                'rule': 'WSC007', 'path': '<string>', 'line': 4, 'col': 1,
                'context': 'apple', 'message_suffix': None
            },
        ] == checker.issues


class TestLines(object):
    """
    WSC001: Bad line ending
    WSC002: Tailing whitespace
    WSC003: Indentation is not multiple of 2
    WSC004: Indentation with non-space character
    """

    def test_lf_is_good_eol(self, checker):
        checker.check_text('orange\nbanana\n')
        assert [] == checker.issues

    def test_cr_is_bad_eol(self, checker):
        checker.check_text('apple\rorange\r')
        assert [
            {
                'rule': 'WSC001', 'path': '<string>', 'line': 1, 'col': 6,
                'context': 'apple', 'message_suffix': '\'\\r\''
            },
            {
                'rule': 'WSC001', 'path': '<string>', 'line': 2, 'col': 7,
                'context': 'orange', 'message_suffix': '\'\\r\''
            },
        ] == checker.issues

    def test_crlf_is_bad_eol(self, checker):
        checker.check_text('apple\r\norange\r\n')
        assert [
            {
                'rule': 'WSC001', 'path': '<string>', 'line': 1, 'col': 6,
                'context': 'apple', 'message_suffix': '\'\\r\\n\''
            },
            {
                'rule': 'WSC001', 'path': '<string>', 'line': 2, 'col': 7,
                'context': 'orange', 'message_suffix': '\'\\r\\n\''
            },
        ] == checker.issues

    @pytest.mark.parametrize('content', [
        'apple banana',
        'apple  banana',
        'apple\tbanana',
        'apple\t\tbanana',
        'apple \t banana',
    ])
    def test_infix_whitespace_is_ok(self, checker, content):
        checker.check_text('{}\n'.format(content))
        assert [] == checker.issues

    @pytest.mark.parametrize('content', [
        'kiwi ',
        'kiwi  ',
        'kiwi\t',
        'kiwi\t\t',
        'kiwi \t ',
    ])
    def test_suffix_space_is_bad(self, checker, content):
        checker.check_text('{}\n'.format(content))
        assert [
            {
                'rule': 'WSC002', 'path': '<string>', 'line': 1, 'col': 5,
                'context': content, 'message_suffix': None
            },
        ] == checker.issues

    @pytest.mark.parametrize('content', [
        'berry',
        '  berry',
        '    berry',
        '      berry',
    ])
    def test_even_indentation_is_good(self, checker, content):
        checker.check_text('{}\n'.format(content))
        assert [] == checker.issues

    @pytest.mark.parametrize('content,col', [
        (' berry',          2),  # noqa: E241
        ('   berry',        4),  # noqa: E241
        ('     berry',      6),  # noqa: E241
        ('       berry',    8),  # noqa: E241
    ])
    def test_odd_indentation_is_bad(self, checker, content, col):
        checker.check_text('{}\n'.format(content))
        assert [
            {
                'rule': 'WSC003', 'path': '<string>', 'line': 1, 'col': col,
                'context': content, 'message_suffix': None
            },
        ] == checker.issues

    @pytest.mark.parametrize('content,col', [
        ('\tpeach',         1),  # noqa: E241
        ('  \tpeach',       3),  # noqa: E241
        (' \t peach',       2),  # noqa: E241
        (' \t\t peach',     2),  # noqa: E241
    ])
    def test_non_spaces_in_indentation_is_bad(self, checker, content, col):
        checker.check_text('{}\n'.format(content))
        assert [
            {
                'rule': 'WSC004', 'path': '<string>', 'line': 1, 'col': col,
                'context': content, 'message_suffix': None
            },
        ] == checker.issues


class TestComplexCases(object):
    def test_multiple_issues(self, checker):
        checker.check_text('\n\n \tpineapple \rbanana')
        assert [
            {
                'rule': 'WSC001', 'path': '<string>', 'line': 3, 'col': 13,
                'context': ' \tpineapple ', 'message_suffix': '\'\\r\''
            },
            {
                'rule': 'WSC002', 'path': '<string>', 'line': 3, 'col': 12,
                'context': ' \tpineapple ', 'message_suffix': None
            },
            {
                'rule': 'WSC003', 'path': '<string>', 'line': 3, 'col': 3,
                'context': ' \tpineapple ', 'message_suffix': None
            },
            {
                'rule': 'WSC004', 'path': '<string>', 'line': 3, 'col': 2,
                'context': ' \tpineapple ', 'message_suffix': None
            },
            {
                'rule': 'WSC005', 'path': '<string>', 'line': 4, 'col': 7,
                'context': 'banana', 'message_suffix': None
            },
            {
                'rule': 'WSC007', 'path': '<string>', 'line': 3, 'col': 1,
                'context': ' \tpineapple ', 'message_suffix': None
            },
        ] == checker.issues
