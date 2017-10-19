"""
Tests for `fusion_util.defer`.
"""
from twisted.internet.defer import CancelledError, Deferred
from twisted.internet.task import Clock
from twisted.trial.unittest import SynchronousTestCase

from fusion_util.defer import TimedOutError, timeout_deferred



class DummyException(Exception):
    """
    Fake exception.
    """



class TimeoutDeferredTests(SynchronousTestCase):
    """
    Tests for ``fusion_util.defer.timeout_deferred``
    """
    def setUp(self):
        """
        Create a clock and a deferred to be cancelled
        """
        self.clock = Clock()
        self.deferred = Deferred()

    def test_propagates_result_if_success_before_timeout(self):
        """
        The deferred callbacks with the result if it succeeds before the
        timeout (e.g. timing out the deferred does not obscure the callback
        value).
        """
        clock = Clock()
        d = Deferred()
        timeout_deferred(d, 10, clock)
        d.callback("Result")
        self.assertEqual(self.successResultOf(d), "Result")

        # the timeout never happens - no errback occurs
        clock.advance(15)
        self.assertIsNone(self.successResultOf(d))

    def test_propagates_failure_if_failed_before_timeout(self):
        """
        The deferred errbacks with the failure if it fails before the
        timeout (e.g. timing out the deferred does not obscure the errback
        failure).
        """
        clock = Clock()
        d = Deferred()
        timeout_deferred(d, 10, clock)
        d.errback(DummyException("fail"))
        self.failureResultOf(d, DummyException)

        # the timeout never happens - no further errback occurs
        clock.advance(15)
        self.assertIsNone(self.successResultOf(d))

    def test_times_out_if_past_timeout(self):
        """
        The deferred errbacks with a TimedOutError if the timeout occurs
        before it either callbacks or errbacks.
        """
        clock = Clock()
        d = Deferred()
        timeout_deferred(d, 10, clock)
        self.assertNoResult(d)

        clock.advance(15)

        self.failureResultOf(d, TimedOutError)

    def test_preserves_cancellation_function_callback(self):
        """
        If a cancellation function that callbacks is provided to the deferred
        being cancelled, its effects will not be overriden with a TimedOutError.
        """
        d = Deferred(lambda c: c.callback('I was cancelled!'))
        timeout_deferred(d, 10, self.clock)
        self.assertNoResult(d)

        self.clock.advance(15)

        self.assertEqual(self.successResultOf(d), 'I was cancelled!')

    def test_preserves_cancellation_function_errback(self):
        """
        If a cancellation function that errbacks (with a non-CancelledError) is
        provided to the deferred being cancelled, this other error will not be
        converted to a TimedOutError.
        """
        d = Deferred(lambda c: c.errback(DummyException('what!')))
        timeout_deferred(d, 10, self.clock)
        self.assertNoResult(d)

        self.clock.advance(15)

        self.failureResultOf(d, DummyException)

    def test_preserves_early_cancellation_error(self):
        """
        If the Deferred is manually cancelled before the timeout, it is not
        re-cancelled (no AlreadyCancelledError), and the CancelledError is not
        obscured
        """
        timeout_deferred(self.deferred, 10, self.clock)
        self.assertNoResult(self.deferred)

        self.deferred.cancel()
        self.failureResultOf(self.deferred, CancelledError)

        self.clock.advance(15)
        # no AlreadyCancelledError raised?  Good.

    def test_deferred_description_passed_to_TimedOutError(self):
        """
        If a deferred_description is passed, the TimedOutError will have that
        string as part of it's string representation.
        """
        timeout_deferred(self.deferred, 5.3, self.clock,
                         deferred_description="It'sa ME!")
        self.clock.advance(6)

        f = self.failureResultOf(self.deferred, TimedOutError)
        self.assertIn("It'sa ME! timed out after 5.3 seconds", str(f))
