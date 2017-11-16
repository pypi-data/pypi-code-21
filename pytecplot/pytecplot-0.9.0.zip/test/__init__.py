import sys

### move mock under unittest like it is in Python version 3.1+
if sys.version_info < (3,1):
    import mock
    import unittest
    sys.modules['unittest.mock'] = mock
    unittest.mock = mock

    def assertIsNone(self, obj):
        return self.assertTrue(obj is None)
    unittest.TestCase.assertIsNone = assertIsNone

    if sys.version_info < (3,3):
        def assertRegex(self, text, regexp, msg=None):
            return self.assertRegexpMatches(text, regexp, msg)
        unittest.TestCase.assertRegex = assertRegex

import argparse
import functools
import logging
import os
import platform
import random
import re
import time
import unittest
import warnings

from argparse import ArgumentParser, SUPPRESS
from contextlib import contextmanager
from os import path
from tempfile import NamedTemporaryFile
from unittest.mock import patch, Mock

logging.basicConfig()

# useful for testing other platforms
#patch('platform.system', Mock(return_value='Windows')).start()

### Mock out DLL if all we are going to do is list out test cases
parser = ArgumentParser(usage=SUPPRESS, add_help=False)
parser.add_argument('-l', '--list',
    action='store_true',
    default=False,
    help='''just list out the test cases, but do not run them.''')
args,_ = parser.parse_known_args(sys.argv)
if args.list:
    from .mock_tecplot_module import patch_tecplot_module
    patch_tecplot_module()
    sys.modules['numpy'] = Mock()

@contextmanager
def closed_tempfile(suffix=''):
    with NamedTemporaryFile(suffix=suffix, delete=False) as fout:
        try:
            fout.close()
            yield fout.name
        finally:
            os.remove(fout.name)

### convenience methods for patching tecutil
def patch_tecutil(fn_name, **kwargs):
    import tecplot
    return patch.object(tecplot.tecutil._tecutil, fn_name, Mock(**kwargs))

@contextmanager
def patched_tecutil(fn_name, **kwargs):
    with patch_tecutil(fn_name, **kwargs) as p:
        yield p


# This will print out timing information for each TestCase
'''
@classmethod
def setUpClass(cls):
    cls.startTime = time.time()
@classmethod
def tearDownClass(cls):
    print("\n{}.{}: {:.3f}".format(cls.__module__, cls.__name__, time.time() - cls.startTime))
unittest.TestCase.setUpClass = setUpClass
unittest.TestCase.tearDownClass = tearDownClass
'''


LATEST_SDK_VERSION = (2017, 2)


def skip_windows():
    def decorator(test_item):
        @functools.wraps(test_item)
        def skip_wrapper(*args, **kwargs):
            if platform.system() != 'Windows':
                test_item(*args, **kwargs)
        return skip_wrapper
    return decorator


def skip_on(*ex):
    """
    Unconditionally skip a test on specfic exceptions
    """
    def decorator(test_item):
        @functools.wraps(test_item)
        def skip_wrapper(*args, **kwargs):
            if __debug__:
                try:
                    warnings.simplefilter('ignore')
                    test_item(*args, **kwargs)
                except ex:
                    raise unittest.SkipTest(str(ex[0]))
                finally:
                    warnings.simplefilter('default')
            else:
                import tecplot
                if tecplot.sdk_version_info < LATEST_SDK_VERSION:
                    raise unittest.SkipTest(str(ex[0]))
                else:
                    test_item(*args, **kwargs)
        return skip_wrapper
    return decorator


def skip_if_sdk_version_before(*ver, **kwargs):
    msg = kwargs.pop('msg', 'Added to SDK in {}')
    def decorator(test_item):
        @functools.wraps(test_item)
        def skip_wrapper(*args, **kwargs):
            import tecplot
            if tecplot.sdk_version_info < ver:
                raise unittest.SkipTest(msg.format('.'.join(str(x) for x in ver)))
            else:
                test_item(*args, **kwargs)
        return skip_wrapper
    return decorator


def skip_if_connected(test_item):
    @functools.wraps(test_item)
    def skip_wrapper(*args, **kwargs):
        import tecplot
        if tecplot.tecutil._tecutil_connector.connected:
            raise unittest.SkipTest('Batch only')
        else:
            test_item(*args, **kwargs)
    return skip_wrapper


def main():
    parser = ArgumentParser(usage=SUPPRESS)
    parser.add_argument('-r', '--random',
        action='store_true',
        default=False,
        help='''randomize ordering of test cases and further randomize
                test methods within each test case''')
    parser.add_argument('-d', '--debug',
        action='store_true',
        default=False,
        help='''Set logging output to DEBUG''')
    parser.add_argument('-l', '--list',
        action='store_true',
        default=False,
        help='''just list out the test cases, but do not run them.''')
    parser.add_argument('-c', '--connect',
        action='store_true',
        default=False,
        help='''connect to a running instance of Tecplot 360.''')
    parser.add_argument('-p', '--port',
        type=int, default=7600,
        help='''port to use when connecting to the TecUtil Server.''')

    def print_help():
        try:
            unittest.main(argv=[sys.argv[0], '--help'])
        except SystemExit:
            parser._print_help()
            sys.exit(0)
    parser._print_help = parser.print_help
    parser.print_help = print_help
    args,unknown_args = parser.parse_known_args(sys.argv)

    if args.debug:
        logging.root.handlers[0].stream = sys.stdout
        logging.root.setLevel(logging.DEBUG)
    else:
        logging.root.handlers[0].stream = open(os.devnull, 'w')

    if args.list:

        def list_of_tests(tests):
            if unittest.suite._isnotsuite(tests):
                yield tests
            else:
                for test in tests._tests:
                    for t in list_of_tests(test):
                        yield t

        here = os.path.abspath(os.path.realpath(os.path.dirname(__file__)))
        tests = unittest.defaultTestLoader.discover('test',
            top_level_dir=os.path.dirname(here))

        tests = sorted(set([str(t) for t in list_of_tests(tests)]))
        tests = [str(t).replace(' (','-').replace(')','') for t in tests]

        for test in tests:
            fnname, namespace = test.split('-')
            if re.search(r'test\.examples\.', namespace):
                continue
            if platform.system() == 'Windows':
                if re.search(r'captured_output', namespace):
                    continue
            print(test)

    else:
        import tecplot as tp
        if args.connect:
            tp.session.connect(port=args.port)
            tp.new_layout()
        else:
            tp.session._tecutil_connector.start()

        if not path.exists(tp.session.tecplot_examples_directory()):
            def TecplotGetHomeDirectory(*a, **kw):
                latestdir = '/builds/360/trunk/nightly/latest'
                if platform.system() == 'Windows':
                    examples_dir = path.join(r'\\buildstore', latestdir, 'win64-vs2013/Release')
                elif platform.system() == 'Darwin':
                    examples_dir = path.join(latestdir, 'macix64.1010/release')
                elif platform.system() == 'Linux':
                    examples_dir = path.join(latestdir, 'linux64-centos6.5/release')
                else:
                    raise RuntimeError('unknown platform: "{}"'.format(platform.system()))
                examples_dir = path.join(examples_dir, 'image')
                return examples_dir
            del tp.tecutil._tecutil_connector._tecsdkhome
            tp.tecutil._tecutil.TecplotGetHomeDirectory = TecplotGetHomeDirectory

        try:
            if args.random:
                unittest.defaultTestLoader.sortTestMethodsUsing = \
                    lambda *a: random.choice((-1,1))
                def suite_init(self,tests=()):
                    self._tests = []
                    self._removed_tests = 0
                    if isinstance(tests, list):
                        random.shuffle(tests)
                    self.addTests(tests)
                unittest.defaultTestLoader.suiteClass.__init__ = suite_init

            unittest.main(argv=unknown_args)

        finally:
            if args.connect:
                tp.session.disconnect()
            tp.session.stop()
