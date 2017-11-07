
# I wonder if this wouldn't be easier if I specified commands and results as text and
# dynamically built the tests.

import unittest, logging
from collections import namedtuple

from runtasks import task
from runtasks.tasks import get_task_names
from runtasks.parser import parse_task

logger = logging.getLogger()


@task
def basic(arg1, arg2=False, arg3=True, arg4=None):
    pass


@task
def other(arg1=None, flag=False, forward=False, verbose=False):
    pass


@task(flags={'x': 'flag'})
def flagtest(arg1=None, flag=False, forward=False, verbose=False):
    pass


@task()
def sometask(flag1=False, flag2=True):
    # A test from the readme
    pass


@task
def counter(verbosity=0):
    # A test from the readme
    pass


basicresults    = namedtuple('basicresults', 'arg1 arg2 arg3 arg4')
otherresults    = namedtuple('otherresults', 'arg1 flag forward verbose')
flagtestresults = namedtuple('flagtestresults', 'arg1 flag forward verbose')


class TestParser(unittest.TestCase):

    def test_positional(self):
        "Ensure position parameters work with no dashes"

        # The value "test" should be assigned to arg1 since it has no default.

        cmdline  = 'basic test'
        expected = basicresults(arg1='test', arg2=False, arg3=True, arg4=None)
        args, remaining = parse_task(basic._task, cmdline.split(), other_names=get_task_names())
        self.assertEqual(args.args, expected)
        self.assertFalse(remaining)

    def test_required(self):
        "Fail if not enough values are provided"

        # If we don't provide a value for arg1 it should fail.

        with self.assertRaises(SystemExit):
            cmdline = 'basic'
            parse_task(basic._task, cmdline.split(), other_names=get_task_names())

    def test_reject_bool_vals(self):
        "Fail if a value is provided for a Boolean parameter"

        # arg2 and arg3 both are Booleans, so you can provide "--arg2" or "--no-arg3" but not
        # "--arg2=xyz".

        with self.assertRaises(SystemExit):
            cmdline = 'basic arg2=test'
            parse_task(basic._task, cmdline.split(), other_names=get_task_names())

        with self.assertRaises(SystemExit):
            cmdline = 'basic arg3=test'
            parse_task(basic._task, cmdline.split(), other_names=get_task_names())

    def test_equals(self):
        _check(basic, 'test1 arg4=test4', basicresults(arg1='test1', arg2=False, arg3=True, arg4='test4'))

    def test_dashes_equals(self):
        _check(basic, 'test1 --arg4=test4', basicresults(arg1='test1', arg2=False, arg3=True, arg4='test4'))

    def test_bool(self):
        "test --arg"
        # A parameter with "=False" is a Boolean parameter that can be enabled using the
        # parameter name as a flag: --arg2

        cmdline  = 'basic test1 --arg2'
        expected = basicresults(arg1='test1', arg2=True, arg3=True, arg4=None)
        args, remaining = parse_task(basic._task, cmdline.split(), other_names=get_task_names())
        self.assertEqual(args.args, expected)
        self.assertFalse(remaining)

    def test_bool_no(self):
        "Test --no-arg"
        # A parameter with "=True" is a Boolean parameter that can be disabled by prepending
        # "no-"to the parameter name as a flag: --no-arg3
        cmdline  = 'basic test1 --no-arg3'
        expected = basicresults(arg1='test1', arg2=False, arg3=False, arg4=None)
        args, remaining = parse_task(basic._task, cmdline.split(), other_names=get_task_names())
        self.assertEqual(args.args, expected)
        self.assertFalse(remaining)

    def test_bool_true_flag(self):
        "Test --arg for a default=True"
        # A parameter with "=True" is a Boolean parameter that can be disabled by prepending
        # "no-"to the parameter name as a flag: --no-arg3
        cmdline  = 'basic test1 --arg3'
        expected = basicresults(arg1='test1', arg2=False, arg3=True, arg4=None)
        args, remaining = parse_task(basic._task, cmdline.split(), other_names=get_task_names())
        self.assertEqual(args.args, expected)
        self.assertFalse(remaining)

    def test_bool_false_no(self):
        "Test --no-arg for a default=False"

        # The parameter defaults to False already, but we'll accept --no-arg for readability.
        cmdline  = 'basic test1 --no-arg2'
        expected = basicresults(arg1='test1', arg2=False, arg3=True, arg4=None)
        args, remaining = parse_task(basic._task, cmdline.split(), other_names=get_task_names())
        self.assertEqual(args.args, expected)
        self.assertFalse(remaining)

    def test_remaining(self):
        "Ensure the parser returns the remaining, unrecognized values."
        cmdline = 'basic test1 other'
        expected = basicresults(arg1='test1', arg2=False, arg3=True, arg4=None)
        args, remaining = parse_task(basic._task, cmdline.split(), other_names=get_task_names())
        self.assertEqual(args.args, expected)
        self.assertEqual(remaining, ['other'])

    def test_dont_guess(self):
        "Fail if a token is ambiguous"

        # In this case "other" can either be the value for basic.arg1 or the name of the next
        # task.  Resist the urge to guess.

        with self.assertRaises(SystemExit):
            cmdline = 'basic other'
            parse_task(basic._task, cmdline.split(), other_names=get_task_names())

        # Here's what you'd need to use if you wanted the value "other"
        cmdline  = 'basic arg1=other'
        expected = basicresults(arg1='other', arg2=False, arg3=True, arg4=None)
        args, remaining = parse_task(basic._task, cmdline.split(), other_names=get_task_names())
        self.assertEqual(args.args, expected)
        self.assertFalse(remaining)

    def test_numval(self):
        # Not surprising, but make sure nothing chokes on the value being just numbers.  Note
        # that the result is still a string.
        _check(basic, '123', basicresults(arg1='123', arg2=False, arg3=True, arg4=None))

    # Make sure the readme examples work :)

    def test_sometask_defaults(self):
        _check(sometask, '', (False, True))

    def test_sometask_flag1(self):
        _check(sometask, '--flag1', (True, True))

    def test_sometask_noflag2(self):
        _check(sometask, '--no-flag2', (False, False))

    def test_sometask_noflag2(self):
        _check(sometask, '--no-flag1', (False, True))

    def test_sometask_noval(self):
        # The first parameter is a Boolean named flag1.  You cannot pass just the name of a
        # flag (though I guess we could change it), so it will be assumed to be the next
        # command.
        _check(sometask, 'flag1', (False, True), remaining='flag1')

    def test_sometask_flag1_val(self):
        _check(sometask, '--flag1 1', (True, True))

    def test_sometask_flag2_val(self):
        _check(sometask, '--flag2 0', (False, False))

    def test_sometask_flag1_int(self):
        _check(sometask, '1', (True, True))

    def test_inttask(self):
        @task
        def inttask(n=123):
            pass
        _check(inttask, '33', 33)

    def test_counter_long(self):
        _check(counter, '--verbosity', 1)

    def test_counter_short(self):
        _check(counter, '-vvv', 3)


class TestShortFlags(unittest.TestCase):
    def test_one_value(self):
        cmdline = 'other -a value1'
        expected = otherresults(arg1='value1', flag=False, forward=False, verbose=False)
        args, remaining = parse_task(other._task, cmdline.split(), other_names=get_task_names())
        self.assertEqual(args.args, expected)
        self.assertFalse(remaining)

    def test_multiple_flags(self):
        cmdline = 'other -va value1'
        expected = otherresults(arg1='value1', flag=False, forward=False, verbose=True)
        args, remaining = parse_task(other._task, cmdline.split(), other_names=get_task_names())
        self.assertEqual(args.args, expected)
        self.assertFalse(remaining)

    def test_flag(self):
        cmdline = 'other -v'
        expected = otherresults(arg1=None, flag=False, forward=False, verbose=True)
        args, remaining = parse_task(other._task, cmdline.split(), other_names=get_task_names())
        self.assertEqual(args.args, expected)
        self.assertFalse(remaining)

    def test_multiple_matches(self):
        "There can only be one parameter per letter"

        # The "other" task has two parameters that start with 'f', so 'f' is not a valid flag.

        with self.assertRaises(SystemExit):
            cmdline = 'other -f'
            parse_task(other._task, cmdline.split(), other_names=get_task_names())

    def test_manual_flags(self):
        # The flagtest task has a flag set specifically by the user.
        cmdline = 'flagtest -vx'
        expected = flagtestresults(arg1=None, flag=True, forward=False, verbose=True)
        args, remaining = parse_task(flagtest._task, cmdline.split(), other_names=get_task_names())
        self.assertEqual(args.args, expected)
        self.assertFalse(remaining)

    def test_manual_flags_multiple(self):
        # The flagtest task has two arguments that start with "f", but we've assigned "x" to
        # one of them.  That means "f" should work for the other.
        cmdline = 'flagtest -f'
        expected = flagtestresults(arg1=None, flag=False, forward=True, verbose=False)
        args, remaining = parse_task(flagtest._task, cmdline.split(), other_names=get_task_names())
        self.assertEqual(args.args, expected)
        self.assertFalse(remaining)

    def test_counter(self):
        @task(register=False)
        def f(v=0):
            pass
        cmdline = 'f -vv'
        expected = (2,)
        args, remaining = parse_task(f._task, cmdline.split(), other_names=[])
        self.assertEqual(args.args, expected)
        self.assertFalse(remaining)

    def test_bool_val(self):
        @task(register=False)
        def f(v=False):
            pass
        cmdline = 'f -v 1'
        expected = (1,)
        args, remaining = parse_task(f._task, cmdline.split(), other_names=[])
        self.assertEqual(args.args, expected)
        self.assertFalse(remaining)

    def test_bool_ignore_int(self):
        @task(register=False)
        def f(v=False):
            pass
        cmdline = 'f -v 123'
        expected = (1,)
        args, remaining = parse_task(f._task, cmdline.split(), other_names=[])
        self.assertEqual(args.args, expected)
        self.assertEqual(remaining, ['123'])

    def test_int(self):
        @task(register=False)
        def f(v=123):
            pass
        cmdline = 'f -v 234'
        expected = (234,)
        args, remaining = parse_task(f._task, cmdline.split(), other_names=[])
        self.assertEqual(args.args, expected)
        self.assertFalse(remaining)

    def test_int_counter(self):
        @task(register=False)
        def f(v=123):
            pass
        cmdline = 'f -v test'
        expected = (124,)
        args, remaining = parse_task(f._task, cmdline.split(), other_names=[])
        self.assertEqual(args.args, expected)
        self.assertEqual(remaining, ['test'])

    def test_equals(self):
        @task(register=False)
        def f(who='World'):
            pass
        _check(f, '-w=Bob', 'Bob')

    def test_equals_multi(self):
        @task(register=False)
        def f(x=False, y=False, who='World'):
            pass
        _check(f, '-xyw=Bob', (True, True, 'Bob'))


def _check(func, cmdline, expected, remaining=None):
    # A helper function to consolidate the common testing code.
    cmdline = cmdline.split()
    cmdline.insert(0, func._task.name)

    if not isinstance(expected, tuple):
        expected = (expected,)

    if remaining is None:
        remaining = []
    else:
        remaining = remaining.split()

    args, rem = parse_task(func._task, cmdline, other_names=[])
    assert args.args == expected
    assert rem == remaining
