try:
    import mock
except ImportError:
    from unittest import mock

# using StringIO to capture IO is easy, but we need to handle Py2 vs. Py3
# StringIO sources by capturing an ImportError
try:
    from StringIO import StringIO
except ImportError:
    from io import StringIO

from tests.framework.patched_testcase import PatchedTestCase


class CapturedIOTestCase(PatchedTestCase):
    """
    A class of TestCases which capture all data written to stderr and stdout.
    """
    def __init__(self, desc):
        PatchedTestCase.__init__(self, desc)

        # create the capturing StringIOs so that we can inspect stderr and
        # stdout during a test run
        # during tests, looking at stderr is as simple as calling
        # `self.stderr.getvalue()`
        self.stderr = StringIO()
        self.stdout = StringIO()
        self._patches.add(mock.patch('sys.stderr', self.stderr))
        self._patches.add(mock.patch('sys.stdout', self.stdout))
