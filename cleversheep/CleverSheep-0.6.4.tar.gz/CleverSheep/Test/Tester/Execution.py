"""Main execution control for the Tester.

"""

import sys
import argparse
import logging
import time

from CleverSheep.Test.Tester import Coordinator
from CleverSheep.Test.Tester import Errors

from CleverSheep.Test.Tester import Logging
from CleverSheep.Test.Tester import WatchDog
from CleverSheep.Test.Tester import CmdLine
from CleverSheep.Test.Tester import options
from CleverSheep.App import Config


#{ Command line and option support

_preTestFilterCallbacks = []
_postCollectionCallbacks = []
_optionsParsedCallbacks = []


class Parser(argparse.ArgumentParser):
    """Wrapper around the arg parse argument parser"""

    def __init__(self):
        """Initialise the member variables"""
        super(Parser, self).__init__(add_help=False)

        self.args = None
        self.unhandled_args = None

    def has_arg(self, arg_name):
        """
        Check if an argument is defined

        :param arg_name: The name of the argument
        :return: If it is present
        """
        return hasattr(self.args, arg_name)

    def get_arg_value(self, arg_name):
        """
        Get the value of an arg

        :param arg_name: The name of the argument
        :return: The value of the arg
        """
        return getattr(self.args, arg_name)

    def parse_known_args(self, args=None, namespace=None):
        """Override the default behavior to store the handled args
        and the unhandled args

        :param args: passed through to argparse.ArgumentParser parse_known_args
        :param namespace: passed through to argparse.ArgumentParser
         parse_known_args
        """
        self.args, self.unhandled_args =\
            super(Parser, self).parse_known_args(args, namespace)


class UserOptionNamespace:
    """A simple class used to mimic a namespace for the user options"""

    def __init__(self, **kwargs):
        self.__dict__.update(kwargs)


class ParserManager(object):
    """A class for managing the argument parsers used within CleverSheep

    Currently there are two, their purpose is a follows:
      * Main Parser - the main parser for the remaining CleverSheep arguments
      * User Parser - the parser for any user defined arguments
    """

    def __init__(self):
        """Create the argument parsers"""
        self.usage = "%(prog)s [options] [test-nums ...]"

        self.args = None

        self.main_argument_parser = Parser()
        self._setup_main_parser()

        self.user_argument_parser = Parser()
        self.user_option_group = self.user_argument_parser.add_argument_group(
            "User Defined Arguments",
            "Defined by the user for various purposes.")

    def has_arg(self, name):
        """Check if any of the parsers have an argument

        :param name: The name of the argument to look for
        :return : Boolean if the arg is found
        """
        if self.main_argument_parser.has_arg(name):
            return True

        if self.user_argument_parser.has_arg(name):
            return True

        return False

    def get_unhandled_args(self):
        """Get any unhandled args, this is expected to be called after all
        three parsers have parsed their arguments

        :return : Returns any args not handled by the argparses
        """
        return self.user_argument_parser.unhandled_args

    def get_args(self):
        """Get all the arg values for the main and user parsers but not the core
        parser. This mimics what the old optparser code used to do but may want
        to be changed in the future.

        :return : Returns the args for the main and user argument parses
        """
        if self.args is None:
            self.args = vars(self.main_argument_parser.args)

            self.args.update(vars(self.user_argument_parser.args))

        return self.args

    def get_arg_value(self, name):
        """Get the value of an arg

        :param name: The name of the arg to get the value of
        :return : Returns the value of the arg specified by name or None if the
          arg cannot be found
        """
        if self.main_argument_parser.has_arg(name):
            return self.main_argument_parser.get_arg_value(name)

        if self.user_argument_parser.has_arg(name):
            return self.user_argument_parser.get_arg_value(name)

        return None

    def _setup_main_parser(self):
        """Setup the options in the main parser"""
        self.main_argument_parser.add_argument(
            "--log-file", action="store",
            default="test.log",
            metavar="PATH",
            help="Set the log file to PATH (default = test.log)")
        self.main_argument_parser.add_argument(
            "--log-level", action="store",
            default="debug", metavar="LEVEL",
            help="Set the logging level to LEVEL (default = debug)."
                 " Valid values: %s" % " ".join(
                Logging.validLevels))
        self.main_argument_parser.add_argument(
            "--timeout", action="store",
            type=int,
            metavar="T", default=0,
            help="Do not use this - its behaviour is not well defined.")
        self.main_argument_parser.add_argument(
            "--uids", action="append",
            default=[],
            help="Select IDs to be run. Use multiple options and or comma"
                 " separated list.")
        self.main_argument_parser.add_argument(
            "--modules", action="append",
            default=[],
            help="Select modules to be run. Use multiple options and or comma"
                 " separated list. Partial names will match.")

        # COMMON OPTIONS
        self.main_argument_parser.add_argument(
            "--summary", action="store_true",
            help="Dump a summary of the loaded tests")
        self.main_argument_parser.add_argument(
            "--ids-summary",
            action="store_true",
            help=argparse.SUPPRESS)
        self.main_argument_parser.add_argument(
            "-i", "--ignore-case",
            action="store_true",
            help="Ignore case when searching test descriptions")
        self.main_argument_parser.add_argument(
            "--skip-passed", "--resume",
            action="store_true",
            help="Resume execution, skipping all previously passed tests")
        self.main_argument_parser.add_argument(
            "--run-broken",
            action="store_true",
            help="Run tests marked as broken")
        self.main_argument_parser.add_argument(
            "--keep-going",
            action="store_true",
            help="Keep going when a test fails")
        self.main_argument_parser.add_argument(
            "--patch-subprocess",
            action="store_true",
            help="Patch sub-process functions to provide status output")
        self.main_argument_parser.add_argument(
            "--add-status-comment",
            action="append",
            default=[],
            help="Define additional comments used for status line,"
                 " in addition to the standard '#>' form")
        self.main_argument_parser.add_argument(
            "--no-times",
            action="store_true",
            help="Do not put time stamps in the log file.")
        self.main_argument_parser.add_argument(
            "--columns", action="store",
            type=int,
            metavar="COL",
            help="Try to restrict output to COL columns (min=60)")
        self.main_argument_parser.add_argument(
            "--unsorted",
            action="store_true",
            help="Do not sort tests into numeric order."
                 "\nMust provide test numbers on command line.")
        self.main_argument_parser.add_argument(
            "--random", action="store",
            type=int, default=0,
            metavar="N",
            help="Use N as seed for random test execution order (default=0)"
                 "\nThe default of zero implies no randomisation."
                 "\nA negative number means seed using system time."
                 "\nA positive number means seed using N.")

        self.main_argument_parser.add_argument(
            "--max-exec-time",
            action="store", type=float,
            metavar="T", default=0.0,
            help="Try to avoid running tests that take longer than T seconds.")
        self.main_argument_parser.add_argument(
            "--times", action="store_true",
            help="List average execution times for selected tests")
        self.main_argument_parser.add_argument(
            "--all-times",
            action="store_true",
            help="List all execution times for selected tests")
        self.main_argument_parser.add_argument(
            "--run-timeout",
            action="store", type=int,
            metavar="T", default=0,
            help="Timeout the test run after T seconds")

        self.main_argument_parser.add_argument(
            "-q", "--quiet", action="store_true",
            help="Only report pass, fail, etc. Omit details of failures.")
        self.main_argument_parser.add_argument(
            "-n", "--no-action", action="store_true",
            help="Do not perform any actions, but still invoke registered reporters")

        # DOCUMENTATION OPTIONS
        doc_group = self.main_argument_parser.add_argument_group(
            "Documentation Options",
            "For generating documentation from tests.")
        doc_group.add_argument("--details", action="store_true",
                               help="Dump a detailed list of the loaded tests")
        doc_group.add_argument("--list-ids", action="store_true",
                               help="List the IDs of matching tests")
        doc_group.add_argument(
            "--dump-tag", action="append", metavar="TAG",
            help="Dump meta-information defined by TAG. Can be repeated.")
        doc_group.add_argument("--list-modules", action="store_true",
                               help="List the modules of matching tests")
        doc_group.add_argument("--list-no-ids", action="store_true",
                               help="List tests without test IDs")
        doc_group.add_argument(
            "--sphinx", action="store",
            metavar="DIR",
            help="Generate documention in Sphinx format DIR")
        doc_group.add_argument(
            "--doc-root", action="store", default=None,
            metavar="PATH",
            help="Set documentation root to PATH (default=Use full paths)")

        # JOURNAL OPTIONS
        journal_group = self.main_argument_parser.add_argument_group(
            "Journalling Options")
        journal_group.add_argument("--enable-journal", action="store_true",
                         help="Enable the long-term journal.")

        # DEBUG ARGS
        debug_group = self.main_argument_parser.add_argument_group(
            "Debugging Options",
            "Useful when debugging problems with tests.")

        debug_group.add_argument("--full-stack", action="store_true",
                           help="Print full stack traceback for test failures.")
        debug_group.add_argument(
            "--full-inner-stack", action="store_true",
            help="Print full inner stack traceback for test failures.")
        debug_group.add_argument(
            "--partial-inner-stack", action="store_true",
            help="Print partial inner stack traceback for test failures.")
        debug_group.add_argument(
            "--all-diffs", action="store_const", const=None,
            dest="num_diffs",
            help="Show all differences when strings do not match")
        debug_group.add_argument(
            "--num-diffs", action="store", type=int, default=1,
            metavar="N",
            help="Display N differences when strings do not match (default=1)")
        debug_group.add_argument("--fail-on", action="store", type=int, default=-1,
                           metavar="N",
                           help="Make each test fail on the Nth asstertion")

    def parse_main_arguments(self):
        """Parse the main arguments."""
        self.main_argument_parser.parse_known_args()

    def add_user_argument(self, *args, **kwargs):
        """Add a user defined argument"""
        self.user_option_group.add_argument(*args, **kwargs)

    def parse_user_arguments(self):
        """Parse the user arguments, should be called after the main args have
        been parsed. Any left over args from the main parser are passed to the
        user parser"""
        self.user_argument_parser.parse_known_args(
            self.main_argument_parser.unhandled_args)

        # Somewhat of a hack to allow the help text to cover all the parsers
        # we create another parser with help text which encapsulates all the
        # options
        help_parser = argparse.ArgumentParser(
            usage=self.usage,
            parents=[self.main_argument_parser,
                     self.user_argument_parser])
        help_parser.parse_known_args(self.user_argument_parser.unhandled_args)

    def get_user_arguments(self):
        """Get any user defined arguments

        :return : Returns any user defined arguments
        """
        return self.user_argument_parser.args


# Create a ParserManager and associate it with the options class, this will mean
# that the config manager knows about the command line option values
parser_manager = ParserManager()
options.set_command_line_option_manager(parser_manager)


def parseUserOptions():
    # TODO: Hack to get around a nasty circular dependency.
    from CleverSheep.Test import Tester

    parser_manager.parse_user_arguments()

    # TODO this needs to in fact suck my dick and also be a namespace with
    # each option name and its value if it takes one
    Tester.userOptions = parser_manager.get_user_arguments()


def add_optionsParsedCallback(func):
    """Add a callback for when the command line options have been parsed.

    This allows a test script to register a function to be called immediately
    after the test framework has finished parsing the command line options. The
    function is invoked simply as ``func()``. You can register multiple
    functions, in which case they are invoked in the order they were
    registered.

    The callbacks are invoked immediately after any user options (those defined
    using ``add_option``) have been parsed.

    :Param func:
        The function to be invoked once the command line options have been
        parsed.

    """
    if func not in _optionsParsedCallbacks:
        _optionsParsedCallbacks.append(func)


def add_preTestFilterCallback(func):
    _preTestFilterCallbacks.append(func)


def add_postCollectionCallback(func):
    _postCollectionCallbacks.append(func)


def invokePreTestFilterCallbacks():
    for func in _preTestFilterCallbacks:
        func()


def invokePostCollectionCallbacks(collection):
    for func in _postCollectionCallbacks:
        func(collection)


# TODO: This seems to be in the wrong module. Something like discovery seems
#       more appropriate.
def add_argument(*args, **kwargs):
    """Add a user (test writer) defined command line option.

    This function can be used to add extra command line options for a set of
    tests. The args and kwargs should match those that would be given to an
    argparse add_argument call
    """
    parser_manager.add_user_argument(*args, **kwargs)


def parseCoreOptions(features={}):
    """Parse the core options and setup the logging. We have to parse the
    core args first as the values the logging library needs are default command
    line values.
    """
    parser_manager.parse_main_arguments()

    logger = Coordinator.getServiceProvider("logging")
    logger.setLogPath(options.get_option_value("log_file"))
    log_level = options.get_option_value("log_level").lower()
    if log_level not in Logging.validLevels:
        sys.exit("Invalid '--log-level'\n"
                 "Valid values are: %s" % " ".join(Logging.validLevels))
    # TODO: Would be cleaner to make the logger understand the names and lose
    #       the dependency on the standard logger module.
    logger.setLogLevel(getattr(logging, log_level.upper()))


def processOptions():
    if options.get_option_value("timeout"):
        setDefaultTimeout(options.get_option_value("timeout"))


def parseCommandLineOptions(features={}):
    # Parse command line. First pass is with the Tester's built-in options
    # and then a second pass looks for user-defined options.
    parser_manager.parse_main_arguments()

    # TODO: The rc-file processing should probably be done in __init__.py.
    rcpath, values = parseRc()
    if rcpath:
        options.set_config_file_options(rcpath, values)

    processOptions()
    parseUserOptions()

    # Allow test scripts the chance to react to the end of command line
    # processing. This is done before test selection because we allow
    # (but not encourage) the callbacks to modify the command line
    # arguments.
    for func in _optionsParsedCallbacks:
        func()

    CmdLine.parseTestSelections(parser_manager.get_unhandled_args())


def getArgs():
    """Get the command line arguments.

    This function returns the command line arguments use when the tests
    were invoked. It can be used in a post-options parsed callback (see
    `add_optionsParsedCallback`) or any time thereafter. The result of
    calling it any earlier is undefined.

    The returned value is the actual list of arguments after all options
    have been parsed (and removed). You can modify this list and it will
    affect the arguments that the test framework sees.

    This allows very specialised test script argument processing. In
    particular, if you use this in a post-options parsed callback then
    any changes to the argument list will affect test selection.

    Using this to change the argument list after the post-options parsed
    callbacks have all been invoked has undefined effects; and you should then
    then treat the return value as read only.

    """
    return parser_manager.get_args()


#}


#{ Global test execution control and querying support


# The writer of a test can arrange to get called back upon certain events
# occurring.
#
# - Once the command line options have been parsed.
# - At the end of a test run; i.e. all tests have run, whether they all passed
#   or not.
# - Just before the test framework is about to exit; i.e. the test framework
#   code has nothing else to do at all.
_testRunEndCallbacks = []
_testExitCallbacks = []


def add_testRunEndCallback(func):
    """Register a function to be invoked when a test run ends.

    The function is invoked after all tests have finished being executed.

    More than one function can be registered. The function is called with no
    arguments. You can register multiple functions, in which case they are
    invoked in the order they were registered.

    :Param func:
        The function to be invoked once the test run has ended.

    """
    if func not in _testRunEndCallbacks:
        _testRunEndCallbacks.append(func)


def add_test_exit_callback(func):
    """Register a function to be invoked just before exiting the test
    framework.

    More than one function can be registered. The function is called with no
    arguments. You can register multiple functions, in which case they are
    invoked in the order they were registered.

    :Param func:
        The function to be invoked once the test run has ended.

    """
    if func not in _testExitCallbacks:
        _testExitCallbacks.append(func)


def currentTestHasFailed():
    """Returns True if the current (just run) test has failed.

    This is intended to be used in tear down methods (``tearDown`` and
    ``suiteTearDown``). Some times if can be useful to behave differently when
    tearing down after a failed test - for example you might wish so save
    (rather than delete) temporary files.

    """
    manager = Coordinator.getServiceProvider("manager")
    return manager.executingTest.hasFailed


def setDefaultTimeout(timeoutPeriod):
    """Set the default watchdog timeout period.

    Tests can be run with a watchdog active to force tests to terminate after
    a specific time. This is useful, for example, in unattended overnight test runs
    where you wish to ensure that a non-terminating test run is treated as an error,
    so that subsequent test runs get a chance to execute.

    Normally the default timeout is ``None``; i.e. disabled.

    :Param timeoutPeriod:
        The watchdog timeout period in whole seconds.
    """

    options.set_option("timeout", timeoutPeriod)


#}
#{ Test script entry points


import os


def currentTestInfo():
    manager = Coordinator.getServiceProvider("manager")
    try:
        test = manager.executingTest
    except (AttributeError, NameError):
        test = None
    if test is not None:
        return test.info


class General(object):
    """Base class for the General service.

    """
    features = {

    }

    def collectTests(self, collectMethod, info, ignoreFiles=[]):
        # Find a collector
        collector = Coordinator.getServiceProvider("collection")
        collectFunc = collector.getFunction(collectMethod)

        # TODO: Collection should possibly interact with the manager.
        try:
            sys.stdout.flush()
            collection = WatchDog.runUnderWatchDog(
                options.get_option_value("timeout"),
                collector.doCollect, collectFunc, info,
                ignoreFiles=ignoreFiles)
        except WatchDog.Timeout as exc:
            sys.stderr.write("Timout during test collection\n")
            sys.stderr.write(Errors.fmtException(exc) + "\n")
            sys.exit(1)

        fail = False
        collection.prune()
        for uid, exc in collection.getProblems():
            sys.stderr.write("Test loading error\n%s\n" % exc)
            fail = True
        if fail:
            sys.exit(1)

        invokePostCollectionCallbacks(collection)
        return collection


class CSGeneral(Coordinator.Provider, General):
    """A general to command the test troops.

    """
    features = {

    }

    def __init__(self):
        pass

    def bootStrap(self, collectMethod, info):
        """Run the test framework.

        This will perform the test collection phase and then hand over control
        to a test manager [TODO: The manager concept may disappear].

        Currently, only the default built in manager is supported. In the
        future this will behave differently depending on which manager has been
        selected.

        """
        # Perform a minimal command line option parsing in order to establish
        # things like which manager is being used. Then create the manager
        # object.
        parseCoreOptions(features=self.features)
        manager = Coordinator.getServiceProvider("manager")
        logger = Coordinator.getServiceProvider("logging")

        # Collect the tests, which can result in more command options being
        # defined.
        collection = self.collectTests(collectMethod, info)

        # Now do a full parsing of the command line options.
        parseCommandLineOptions(features=self.features)
        logger.set_columns(options.get_option_value("columns"))
        invokePreTestFilterCallbacks()

        manager.loadJournal()
        manager.setCollection(collection)
        selector = options.get_option_value("select")
        manager.addSelector(selector)
        string_search_summary_lines =\
            selector.build_string_search_summary_lines()

        if options.get_option_value("no_action"):
            manager.null_action()
            return
        elif options.get_option_value("times") or options.get_option_value("all_times"):
            manager.listTimes()
            return
        elif options.get_option_value("summary"):
            manager.summarise()
            return
        elif options.get_option_value("list_ids"):
            manager.listIDs()
            return
        elif options.get_option_value("dump_tag"):
            manager.dumpTags(options.get_option_value("dump_tag"))
            return
        elif options.get_option_value("list_modules"):
            manager.listModules()
            return
        elif options.get_option_value("list_no_ids"):
            manager.listIDs(no_ids=True)
            return
        elif options.get_option_value("sphinx"):
            manager.sphinx()
            return
        elif options.get_option_value("details"):
            manager.detail()
            return
        elif options.get_option_value("ids_summary"):
            manager.show_ids()
            return

        logger.start()

        # If string selectors are being used print them out to make it obvious
        # to the user. This is done as if you mistype a command line option it
        # will be treated as a string filter
        if len(string_search_summary_lines) > 0:
            status = Coordinator.getServiceProvider("status")
            for line in string_search_summary_lines:
                logger.write(line, indent_lines=False)
                status.write(line)

        options.set_option("cs_start_time", time.time())
        exit_code = manager.run()

        # Perform one-time tidy up.
        for func in _testExitCallbacks:
            try:
                func()
            except:
                pass

        return exit_code


Coordinator.registerProvider("cscore", ("general",), CSGeneral())


#}
#{ Suspect stuff

def parseRc():
    """Parse the user's ``.cstesterrc`` file, if it exists.

    """
    configFile = Config.ConfigFile()
    path = os.path.expanduser("~/.cstesterrc")
    try:
        f = open(path)
    except IOError:
        return None, configFile
    d = {}
    exec(f.read(), d, d)

    for name, value in d.iteritems():
        if name.startswith("_"):
            continue
        setattr(configFile, name, value)
    return path, configFile

#}
