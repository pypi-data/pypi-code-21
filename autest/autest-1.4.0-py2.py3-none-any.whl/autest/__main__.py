
from __future__ import absolute_import, division, print_function

import sys
import os

import hosts
import hosts.output

import autest
import autest.core.testrun
from autest.core.engine import Engine
import autest.common.execfile as execfile

from autest.common.settings import *
from autest.core.variables import Variables
import autest.api as api


def main():
    # set default subcommand to run if there are none present
    if len(sys.argv) >= 2:
        if '-' in sys.argv[1] and sys.argv[1] not in ['-h', '--help']:
            sys.argv.insert(1, 'run')
    else:
        sys.argv.insert(1, 'run')

    # create primary commandline parser
    setup = Settings()

    run = setup.add_command("run", help='(Default Option) Runs tests')
    list = setup.add_command("list", help='Lists all the test available to Autest')

    setup.path_argument(
        ["-D", "--directory"],
        default=os.path.abspath('.'),
        help="The directory with all the tests in them")

    setup.path_argument(
        ["--autest-site"],
        help="A user provided autest-site directory to use instead of the default")

    setup.path_argument(
        ["--sandbox"],
        default=os.path.abspath('./_sandbox'),
        exists=False,
        help="The root directory in which the tests will run")

    setup.list_argument(
        ["--env"],
        metavar="Key=Value",
        help="Set a variable to be used in the local test environment. Replaces value inherited from shell.")

    setup.list_argument(
        ["-f", "--filters"],
        dest='filters',
        default=['*'],
        help="Filter the tests run by their names")

    setup.add_argument(
        ['-V', '--version'], action='version',
        version='%(prog)s {0}'.format(autest.__version__))

    run.list_argument(
        ["-R", "--reporters"],
        default=['default'],
        help="Names of Reporters to use for report generation")

    run.add_argument(
        ["-j", "--jobs"],
        default=1,
        type=JobValues,
        help="The number of test to try to run at the same time")

    run.string_argument(
        ['-C', '--clean'],
        default='passed',
        help='''
        Level of cleaning for after a test is finished.
        all > exception > failed > warning > passed > skipped > unknown> none
        Defaults at passed
        ''')

    list.add_argument(
        ['--json'],
        action='store_true',
        help="outputs the list of available tests in JSON format"
    )

    # this is a commandline tool so make the cli host
    hosts.setDefaultArgs(setup)

    # -------------------------------------------
    # setup vars
    variables = Variables({
        'Autest': Variables({
            ########################
            # Process Control
            # Long delay before process trees are shut down
            'StopProcessLongDelaySeconds': 10,
            #  Short delay after first process kill before next will be kill
            'StopProcessShortDelaySeconds': 1,
            #  delay after control-c before kill
            'KillDelaySecond': 10, # most programs should finish in tens second

            ########################
            # Process Spawning

            # False -> autoselect logic used
            # True -> Use shell, Bad commands don't report clearly
            'ForceUseShell': None,

            ########################
            # Engine configuration
            # 'Test_dir': setup.arguments.directory,
            # 'Filters': setup.arguments.filters,
            # 'Run_dir': setup.arguments.sandbox,
            # 'Autest_site': setup.arguments.autest_site,
            # 'Action': setup.arguments.subcommand,
            ########################
            # Command specific arguments
            'Run': Variables({
                # 'Jobs': setup.arguments.jobs,
                # 'Reporters': setup.arguments.reporters,
                # 'Clean': clean_level,
            }),
            'List': Variables({})
        })
    })

    # parser should have all option defined by program and or host type defined
    setup.partial_parse()

    # make default host
    myhost = hosts.ConsoleHost(setup)
    # setup the extended streams to run
    hosts.Setup(myhost)

    hosts.output.WriteDebugf(
        "init", "Before extension load: args = {0}\n unknown = {1}", setup.arguments, setup.unknowns)

    # setup shell environment
    env = os.environ.copy()
    if setup.arguments.env:
        for i in setup.arguments.env:
            try:
                k, v = i.split("=", 1)
                env[k] = v
            except ValueError:
                hosts.output.WriteWarning(
                    "--env value '{0}' ignored. Needs to in the form of Key=Value".format(i))

    # -------------------------------------------
    # look in autest-site directory to see if we have a file to define user
    # options
    if setup.arguments.autest_site is None:
        # this is the default
        path = os.path.join(setup.arguments.directory, 'autest-site')
    else:
        # This is a custom location
        path = os.path.abspath(setup.arguments.autest_site)

    old_path = sys.path[:]
    sys.path.append(path)
    # see if we have a file to load to get new options
    options_file = os.path.join(path, "init.cli.ext")
    if os.path.exists(options_file):
        _locals = {
            'Settings': setup,
            'AutestSitePath': path,
            "host": hosts.output,
            'AuTestVersion': api.AuTestVersion,
        }
        execfile.execFile(options_file, _locals, _locals)
    # parse the options and error if we have unknown options
    setup.final_parse()
    hosts.output.WriteDebugf(
        "init", "After extension load: args = {0}", setup.arguments)

    # see if we have any custom setup we want to do globally.
    options_file = os.path.join(path, "setup.cli.ext")
    if os.path.exists(options_file):
        _locals = {
            'os': os,
            'ENV': env,
            'Variables': variables,
            'Arguments': setup.arguments,
            "host": hosts.output,
            'AutestSitePath': path,
            'AuTestVersion': api.AuTestVersion,
        }
        execfile.execFile(options_file, _locals, _locals)
    sys.path = old_path

    # setup command specific arguments
    if setup.arguments.subcommand == 'run':
        # taken from tester.py
        clean_choices = {"none": -1,
                         "unknown": 0,
                         "skipped": 1,
                         "passed": 2,
                         "warning": 3,
                         "failed": 4,
                         "exception": 5,
                         "all": 6}

        # setup the level of cleaning
        if setup.arguments.clean:
            if setup.arguments.clean in clean_choices:
                variables.Autest.Run.Clean = clean_choices[setup.arguments.clean]
            else:
                hosts.output.WriteWarning(
                    "-C/--clean value '{0}' ignored. Defaulting to cleaning all passed. See help for valid choices.".format(setup.arguments.clean))
                variables.Autest.Run.Clean = 2
        else:
            variables.Autest.Run.Clean = 2

        variables.Autest.Run.Jobs = setup.arguments.jobs
        variables.Autest.Run.Reporters = setup.arguments.reporters
    elif setup.arguments.subcommand == 'list':
        variables.Autest.List.output_json = setup.arguments.json

    # put rest of the engine-scope args into variables
    variables.Autest.TestDir = setup.arguments.directory
    variables.Autest.Filters = setup.arguments.filters
    variables.Autest.RunDir = setup.arguments.sandbox
    variables.Autest.Autest_site = setup.arguments.autest_site
    variables.Autest.Action = setup.arguments.subcommand

    # this is a cli program so we only make one engine and run it
    # a GUI might make a new GUI for every run as it might have new options,
    # or maybe not
    myEngine = Engine(env=env, variables=variables)

    try:
        ret = myEngine.Start()
    except SystemExit:
        hosts.output.WriteError("Autest shutdown because of critical error!", exit=False, show_stack=False)
        ret = 1
    exit(ret)


if __name__ == '__main__':
    main()
