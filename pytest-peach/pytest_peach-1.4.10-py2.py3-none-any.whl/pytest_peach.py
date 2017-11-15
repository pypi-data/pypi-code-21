#!/usr/bin/python

'''pytest-peach extension
Copyright (c) 2017 Peach Tech

Provides integration with Peach API Security
https://peach.tech

'''

from __future__ import print_function
import os, warnings, logging
import pytest
import peachapisec

logger = logging.getLogger(__name__)
__pytest_peach_enabled = False
__peach_last_testcase = ""

def pytest_addoption(parser):
    
    parser.addoption(
        '--peach',
        action='store',
        default=None,
        type=str,
        help="Enable Peach API Security support by setting to 'on'")
    
def getTestName(item):
    name = item.name
    endIndex = name.rfind('[')
    if endIndex > 0:
        return name[:endIndex]
    return name

def pytest_configure(config):
        if not config.option.peach:
            return
        
        global __pytest_peach_enabled
        __pytest_peach_enabled = True
        
        if config.getoption('verbose') > 0:
            logger.setLevel(logging.DEBUG)
        else:
            logger.setLevel(logging.INFO)
        
        logFormatter = logging.Formatter("%(asctime)s [%(levelname)-5.5s] pytest-peach: %(message)s")
        consoleHandler = logging.StreamHandler()
        consoleHandler.setFormatter(logFormatter)
        logger.addHandler(consoleHandler)
        
        #fileHandler = logging.FileHandler('pytest-peach.log')
        #fileHandler.setFormatter(logFormatter)
        #logger.addHandler(fileHandler)
        
        os.environ["HTTP_PROXY"] = peachapisec.proxy_url()
        os.environ["HTTPS_PROXY"] = peachapisec.proxy_url()
        logger.info("pytest-peach initializing.")
        #logger.debug(">>pytest_configure")
        

def pytest_unconfigure(config):
    if not config.option.peach:
        return
    
    #logger.trace(">>pytest_unconfigure")
    peachapisec.suite_teardown()


def pytest_report_teststatus(report):
    '''
    Fake all tests passing
    '''
    
    global __pytest_peach_enabled
    if not __pytest_peach_enabled:
        return

    report.outcome = 'passed'
    return None

import bdb
import sys
from time import time

import py
import pytest
from _pytest._code.code import TerminalRepr, ExceptionInfo

@pytest.hookimpl(tryfirst=True)
def pytest_runtest_protocol(item, nextitem):
    global __pytest_peach_enabled
    if not __pytest_peach_enabled:
        return
    
    global __peach_last_testcase

    #logger.trace(">>pytest_runtest_protocol")
    testCaseName = getTestName(item)

    #print(dir(item))
    if item.get_marker("skip"):
        logger.info("Skipping '%s'", testCaseName)
        return True

    #import code
    #code.interact(local=locals())

    if not __peach_last_testcase == testCaseName:
        logger.info("Running '%s'", testCaseName)
    
    while True:
        logger.debug(testCaseName)
        runtestprotocol(item, nextitem=nextitem)
        __peach_last_testcase = testCaseName
    
        if peachapisec.state() != 'Continue':
            break
        else:
            logger.debug("Peach State: %s", peachapisec.state())
    
    return True

def runtestprotocol(item, log=True, nextitem=None):
    hasrequest = hasattr(item, "_request")
    if hasrequest and not item._request:
        item._initrequest()
            
    rep = call_and_report(item, "setup", log)
    reports = [rep]
    if rep.passed:
        if item.config.option.setupshow:
            show_test_item(item)
        if not item.config.option.setuponly:
            reports.append(call_and_report(item, "call", log))
    reports.append(call_and_report(item, "teardown", log,
        nextitem=nextitem))
    # after all teardown hooks have been called
    # want funcargs and request info to go away
    if hasrequest:
        item._request = False
        item.funcargs = None
    return reports

def call_runtest_hook(item, when, **kwds):
    hookname = "pytest_runtest_" + when
    ihook = getattr(item.ihook, hookname)
    func = lambda: ihook(item=item, **kwds)
    func()

def call_and_report(item, when, log=True, **kwds):

    global __peach_last_testcase
    testCaseName = getTestName(item)

    if when == "setup":
        peachapisec.setup()
        try:
            call_runtest_hook(item, when, **kwds)
        except Exception as ex:
            if not __peach_last_testcase == testCaseName:
                logger.info("Error on setup: %s", ex)
            else:
                logger.debug("Error on setup: %s", ex)

    elif when == "call":
        peachapisec.testcase(testCaseName)

        try:
            call_runtest_hook(item, when, **kwds)
        except Exception as ex:
            if not __peach_last_testcase == testCaseName:
                logger.info("Error: %s", ex)
            else:
                logger.debug("Error: %s", ex)

    elif when == "teardown":
        peachapisec.teardown()
        try:
            call_runtest_hook(item, when, **kwds)
        except Exception as ex:
            if not __peach_last_testcase == testCaseName:
                logger.info("Error on teardown: %s", ex)
            else:
                logger.debug("Error on teardown: %s", ex)
        
    return TestReport(item.nodeid, item.location,
                      dict([(x,1) for x in item.keywords]), "passed", None, when,
                      [], 1)

class BaseReport(object):

    def __init__(self, **kw):
        self.__dict__.update(kw)

    def toterminal(self, out):
        if hasattr(self, 'node'):
            out.line(getslaveinfoline(self.node))

        longrepr = self.longrepr
        if longrepr is None:
            return

        if hasattr(longrepr, 'toterminal'):
            longrepr.toterminal(out)
        else:
            try:
                out.line(longrepr)
            except UnicodeEncodeError:
                out.line("<unprintable longrepr>")

    def get_sections(self, prefix):
        for name, content in self.sections:
            if name.startswith(prefix):
                yield prefix, content

    @property
    def longreprtext(self):
        """
        Read-only property that returns the full string representation
        of ``longrepr``.
        .. versionadded:: 3.0
        """
        tw = py.io.TerminalWriter(stringio=True)
        tw.hasmarkup = False
        self.toterminal(tw)
        exc = tw.stringio.getvalue()
        return exc.strip()

    @property
    def capstdout(self):
        """Return captured text from stdout, if capturing is enabled
        .. versionadded:: 3.0
        """
        return ''.join(content for (prefix, content) in self.get_sections('Captured stdout'))

    @property
    def capstderr(self):
        """Return captured text from stderr, if capturing is enabled
        .. versionadded:: 3.0
        """
        return ''.join(content for (prefix, content) in self.get_sections('Captured stderr'))

    passed = property(lambda x: x.outcome == "passed")
    failed = property(lambda x: x.outcome == "failed")
    skipped = property(lambda x: x.outcome == "skipped")

    @property
    def fspath(self):
        return self.nodeid.split("::")[0]

class TestReport(BaseReport):
    """ Basic test report object (also used for setup and teardown calls if
    they fail).
    """
    def __init__(self, nodeid, location, keywords, outcome,
                 longrepr, when, sections=(), duration=0, **extra):
        #: normalized collection node id
        self.nodeid = nodeid

        #: a (filesystempath, lineno, domaininfo) tuple indicating the
        #: actual location of a test item - it might be different from the
        #: collected one e.g. if a method is inherited from a different module.
        self.location = location

        #: a name -> value dictionary containing all keywords and
        #: markers associated with a test invocation.
        self.keywords = keywords

        #: test outcome, always one of "passed", "failed", "skipped".
        self.outcome = outcome

        #: None or a failure representation.
        self.longrepr = longrepr

        #: one of 'setup', 'call', 'teardown' to indicate runtest phase.
        self.when = when

        #: list of pairs ``(str, str)`` of extra information which needs to
        #: marshallable. Used by pytest to add captured text
        #: from ``stdout`` and ``stderr``, but may be used by other plugins
        #: to add arbitrary information to reports.
        self.sections = list(sections)

        #: time it took to run just the test
        self.duration = duration

        self.__dict__.update(extra)

    def __repr__(self):
        return "<TestReport %r when=%r outcome=%r>" % (
            self.nodeid, self.when, self.outcome)


class UnexpectedError(Exception):
    pass

# end
