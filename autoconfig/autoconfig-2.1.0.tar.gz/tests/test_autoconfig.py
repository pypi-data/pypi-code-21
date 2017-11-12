
# The library doesn't yet have a way to "undo", so we are only going to execute once.

import os, sys, logging, os.path
from os.path import dirname, join

import autoconfig
autoconfig.init(searchfrom=__file__, env=['other'], relpath='local')


def test_filename():
    fqn = join(dirname(__file__), '.config')
    assert autoconfig.get_filename() == fqn


def test_vars():
    "Ensure environment variables are set"
    assert os.environ.get('TESTA') == 'a'
    assert os.environ.get('TESTB') == 'b'


def test_othervars():
    "Ensure environment variables are set from [other]"
    assert os.environ.get('TESTOTHER') == 'a'


def test_syspath():
    "Ensure [env] PYTHONPATH entries were added to the system path"
    # The regular env has these: lib:/var/autoconfig
    #
    # Since 'lib' is relative, it will be relative to the .config file which is this file's
    # directory.  The other is absolute, so it should be on the path too.
    relative = join(dirname(__file__), 'lib')
    assert relative in sys.path

    absolute = '/var/autoconfig'
    assert absolute in sys.path


def test_othersyspath():
    "Ensure [other] PYTHONPATH entries were added to the system path"
    # PYTHONPATH=otherlib:/var/otherautoconfig
    relative = join(dirname(__file__), 'otherlib')
    assert relative in sys.path

    absolute = '/var/otherautoconfig'
    assert absolute in sys.path


def test_debuglogging():
    "Ensure loggers from [logging] debug were set"
    logger = logging.getLogger('autoconfigtest')
    assert logger.isEnabledFor(logging.DEBUG)


def test_relpath():
    "Ensure relpath was set local to this file."
    fqn = join(dirname(__file__), 'local')
    assert fqn in sys.path
