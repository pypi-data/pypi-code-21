#!/usr/bin/env python
# -*- coding: utf-8 -*-

__author__ = "knarfeh@outlook.com"


_RESULT_MAX_LENGTH = 80


def safe_repr(obj, short=False):
    try:
        result = repr(obj)
    except Exception:
        result = object.__repr__(obj)
    if not short or len(result) < _RESULT_MAX_LENGTH:
        return result
    return result[:_RESULT_MAX_LENGTH] + ' [truncated]...'


def _sentinel(*args, **kwargs):
    raise AssertionError('Should never be called')


class _AssertRaisesContext(object):
    """
    context manager used to implement TestCase.assertRaises methods.
    """

    def __init__(self, expected, test_case, expected_regexp=None):
        self.expected = expected
        self.failureException = test_case.failureException
        self.expected_regexp = expected_regexp

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_value, tb):
        if exc_type is None:
            try:
                exc_name = self.expected.__name__
            except AttributeError:
                exc_name = str(self.expected)
            raise self.failureException(
                "{0} not raised".format(exc_name))
        if not issubclass(exc_type, self.expected):
            # let unexpected exceptions pass through
            return False
        # store for later retrieval
        self.exception = exc_value
        if self.expected_regexp is None:
            return True

        expected_regexp = self.expected_regexp
        if not expected_regexp.search(str(exc_value)):
            raise self.failureException('"%s" does not match "%s"' %
                                        (expected_regexp.pattern, str(exc_value)))
        return True


class Assertion(object):
    longMessage = False
    failureException = AssertionError
    maxDiff = 80 * 8
    # If a string is longer than _diffThreshold, use normal comparison instead
    # of difflib.  See #11763.
    _diffThreshold = 2 ** 16
    # Attribute used by TestSuite for classSetUp

    _classSetupFailed = False

    def __init__(self, method_name='runTest'):
        """
        Create an instance of the class that will use the named test
        method when executed. Raises a ValueError if the instance does
        not have a method with the specified name.
        """
        self._testMethodName = method_name
        self._resultForDoCleanups = None

        # Map types to custom assertEqual functions that will compare
        # instances of said type in more detail to generate a more useful
        # error message.
        self._type_equality_funcs = {}
        self.add_type_equality_func(dict, 'assertDictEqual')
        self.add_type_equality_func(list, 'assertListEqual')
        self.add_type_equality_func(tuple, 'assertTupleEqual')
        self.add_type_equality_func(set, 'assertSetEqual')
        self.add_type_equality_func(frozenset, 'assertSetEqual')
        try:
            self.add_type_equality_func(unicode, 'assertMultiLineEqual')
        except NameError:
            # No unicode support in this build
            pass

    def add_type_equality_func(self, typeobj, function):
        """Add a type specific assertEqual style function to compare a type.

        This method is for use by TestCase subclasses that need to register
        their own type equality functions to provide nicer error messages.

        Args:
            typeobj: The data type to call this function on when both values
                    are of the same type in assertEqual().
            function: The callable taking two arguments and an optional
                    msg= argument that raises self.failureException with a
                    useful error message when the two arguments are not equal.
        """
        self._type_equality_funcs[typeobj] = function

    def assert_false(self, expr, msg=None):
        """
        Check that the expression is false.
        """
        if expr:
            msg = self._format_message(msg, "%s is not false" % safe_repr(expr))
            raise self.failureException(msg)

    def assert_true(self, expr, msg=None):
        """
        Check that the expression is true.
        :param expr
        :param msg
        """
        if not expr:
            msg = self._format_message(msg, "%s is not true" % safe_repr(expr))
            raise self.failureException(msg)

    def _format_message(self, msg, standard_msg):
        """
        Honour the longMessage attribute when generating failure messages.
        If longMessage is False this means:
        * Use only an explicit message if it is provided
        * Otherwise use the standard message for the assert

        If longMessage is True:
        * Use the standard message
        * If an explicit message is provided, plus ' : ' and the explicit message
        """
        if not self.longMessage:
            return msg or standard_msg
        if msg is None:
            return standard_msg
        try:
            # don't switch to '{}' formatting in Python 2.X
            # it changes the way unicode input is handled
            return '%s : %s' % (standard_msg, msg)
        except UnicodeDecodeError:
            return '%s : %s' % (safe_repr(standard_msg), safe_repr(msg))

    def assert_raises(self, exc_class, callable_obj=_sentinel, *args, **kwargs):
        """
        Fail unless an exception of class excClass is raised
        by callableObj when invoked with arguments args and keyword
        arguments kwargs. If a different type of exception is
        raised, it will not be caught, and the test case will be
        deemed to have suffered an error, exactly as for an
        unexpected exception.

        If called with callableObj omitted, will return a
        context object used like this::

        with self.assertRaises(SomeException):
            do_something()

        The context manager keeps a reference to the exception as
        the 'exception' attribute. This allows you to inspect the
        exception after the assertion::

        with self.assertRaises(SomeException) as cm:
            do_something()
            the_exception = cm.exception
            self.assertEqual(the_exception.error_code, 3)
        """
        context = _AssertRaisesContext(exc_class, self)
        if callable_obj is _sentinel:
            return context
        with context:
            callable_obj(*args, **kwargs)

    def _get_assert_equality_func(self, first, second):
        """
        Get a detailed comparison function for the types of the two args.

        Returns: A callable accepting (first, second, msg=None) that will
        raise a failure exception if first != second with a useful human
        readable error message for those types.
        :param first
        :param second
        :return
        """
        #
        # NOTE(gregory.p.smith): I considered isinstance(first, type(second))
        # and vice versa.  I opted for the conservative approach in case
        # subclasses are not intended to be compared in detail to their super
        # class instances using a type equality func.  This means testing
        # subtypes won't automagically use the detailed comparison.  Callers
        # should use their type specific assertSpamEqual method to compare
        # subclasses if the detailed comparison is desired and appropriate.
        # See the discussion in http://bugs.python.org/issue2578.
        #
        if type(first) is type(second):
            asserter = self._type_equality_funcs.get(type(first))
            if asserter is not None:
                if isinstance(asserter, basestring):  # noqa
                    asserter = getattr(self, asserter)
                return asserter

        return self._base_assert_equal

    def _base_assert_equal(self, first, second, msg=None):
        """
        The default assertEqual implementation, not type specific.
        :param first
        :param second
        :param msg
        """
        if not first == second:
            standard_msg = '%s != %s' % (safe_repr(first), safe_repr(second))
            msg = self._format_message(msg, standard_msg)
            raise self.failureException(msg)

    def assert_equal(self, first, second, msg=None):
        """
        Fail if the two objects are unequal as determined by the '==' operator.
        :param first
        :param second
        :param msg
        """
        assertion_func = self._get_assert_equality_func(first, second)
        assertion_func(first, second, msg=msg)

    def assert_not_equal(self, first, second, msg=None):
        """
        Fail if the two objects are equal as determined by the '!=' operator.
        :param first
        :param second
        :param msg
        """
        if not first != second:
            msg = self._format_message(msg, '%s == %s' % (safe_repr(first),
                                                          safe_repr(second)))
            raise self.failureException(msg)

    def assert_almost_equal(self, first, second, places=None, msg=None, delta=None):
        """
        Fail if the two objects are unequal as determined by their
        difference rounded to the given number of decimal places
        (default 7) and comparing to zero, or by comparing that the
        between the two objects is more than the given delta.

        Note that decimal places (from zero) are usually not the same
        as significant digits (measured from the most significant digit).

        If the two objects compare equal then they will automatically
        compare almost equal.

        :param first
        :param second
        :param places
        :param msg
        :param delta
        :return None
        """
        if first == second:
            # shortcut
            return
        if delta is not None and places is not None:
            raise TypeError("specify delta or places not both")

        if delta is not None:
            if abs(first - second) <= delta:
                return

            standard_msg = '%s != %s within %s delta' % (safe_repr(first),
                                                         safe_repr(second),
                                                         safe_repr(delta))
        else:
            if places is None:
                places = 7

            if round(abs(second - first), places) == 0:
                return

            standard_msg = '%s != %s within %r places' % (safe_repr(first),
                                                          safe_repr(second),
                                                          places)
        msg = self._format_message(msg, standard_msg)
        raise self.failureException(msg)

    def assert_not_almost_equal(self, first, second, places=None, msg=None, delta=None):
        """
        Fail if the two objects are equal as determined by their
        difference rounded to the given number of decimal places
        (default 7) and comparing to zero, or by comparing that the
        between the two objects is less than the given delta.

        Note that decimal places (from zero) are usually not the same
        as significant digits (measured from the most significant digit).

        Objects that are equal automatically fail.

        :param first:
        :param second:
        :param places:
        :param msg:
        :param delta:
        :return:
        """
        if delta is not None and places is not None:
            raise TypeError("specify delta or places not both")
        if delta is not None:
            if not (first == second) and abs(first - second) > delta:
                return
            standard_msg = '%s == %s within %s delta' % (safe_repr(first),
                                                         safe_repr(second),
                                                         safe_repr(delta))
        else:
            if places is None:
                places = 7
            if not (first == second) and round(abs(second - first), places) != 0:
                return
            standard_msg = '%s == %s within %r places' % (safe_repr(first),
                                                          safe_repr(second),
                                                          places)

        msg = self._format_message(msg, standard_msg)
        raise self.failureException(msg)
