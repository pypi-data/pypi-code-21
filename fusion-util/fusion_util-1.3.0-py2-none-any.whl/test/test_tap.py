from testtools import TestCase

from twisted.internet.defer import succeed

from fusion_util import tap



class TapTests(TestCase):
    """
    Tests for `fusion_util.tap.tap`.
    """
    def test_tap(self):
        """
        L{fusion_util.tap.tap} calls a function with a result and optional
        positional and keyword arguments and discards its return value, instead
        returning the original result.
        """
        def func(result, a, b):
            self.calledWith = result, a, b
            return 5144

        def _checkResult(result):
            # The return value of func is discarded.
            self.assertEquals(result, 42)
            self.assertEquals(self.calledWith, (42, 1, 2))

        d = succeed(42)
        d.addCallback(tap(func), 1, b=2)
        d.addCallback(_checkResult)
        return d
