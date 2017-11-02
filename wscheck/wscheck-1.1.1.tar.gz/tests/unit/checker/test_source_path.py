import pytest

from wscheck.checker import WhitespaceChecker


class AlwaysFailChecker(WhitespaceChecker):
    def __init__(self):
        super(AlwaysFailChecker, self).__init__()
        self._checkers = [self._check_for_fail]

    def _check_for_fail(self, source_path, lines):
        self._add_issue(rule='WSC000', path=source_path, line=1, col=1, context='')


class TestSourcePath(object):
    def test_without_specified_source(self):
        fail_checker = AlwaysFailChecker()
        fail_checker.check_text('')

        assert [
            {'rule': 'WSC000', 'path': '<string>', 'line': 1, 'col': 1, 'context': '', 'message_suffix': None},
        ] == fail_checker.issues

    @pytest.mark.parametrize('source_path', [
        ('/empty/file', ''),
        ('/contains/anything', ' foo\t\r\nbar '),
    ])
    def test_with_source(self, source_path):
        fail_checker = AlwaysFailChecker()
        fail_checker.check_text('', source_path)

        assert [
            {'rule': 'WSC000', 'path': source_path, 'line': 1, 'col': 1, 'context': '', 'message_suffix': None},
        ] == fail_checker.issues
