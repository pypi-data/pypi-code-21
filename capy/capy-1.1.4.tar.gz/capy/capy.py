#!/usr/bin/env python

import sys
import argparse
import xmlrpclib
from datetime import datetime
from conf import Config
from util import Color, STDERR_LOGGER, STDOUT_LOGGER, check_cmd, exit_error
from test import TestAction
from cmd import DeviceRunner

DESCRIPTION = '''CAPY is a helper for running calabash tests on iOS and Android'''
LONG_DESCRIPTION = DESCRIPTION
NAME = 'capy'
VERSION = '1.1.4'


####################################################################################################
# Version check
####################################################################################################
def check_version():
    msg = check_package(NAME, VERSION)
    if msg:
        c = Color.LIGHT_GREEN
        print c + '+----------------------------------------+'
        print c + '| {m:30}'.format(m=msg) + c + ' |'
        print c + '| {m:38}'.format(m=' ') + c + ' |'
        print c + '| {m:42}'.format(m='Please run: ' + Color.ENDC + 'pip install -U ' + NAME) + c + ' |'
        print c + '+----------------------------------------+' + Color.ENDC


def check_package(name, current_version):
    pypi = xmlrpclib.ServerProxy('https://pypi.python.org/pypi')
    available = pypi.package_releases(name)
    if not available:
        # Try to capitalize pkg name
        available = pypi.package_releases(name.capitalize())

    msg = name
    if not available:
        msg = None
    elif available[0] != current_version:
        msg += ' has new release (%s) available' % available[0]
    else:
        msg = None
    return msg


def check_calabash():
    cmds = ['calabash-android', 'cucumber']
    for cmd in cmds:
        if not check_cmd(cmd):
            exit_error('Command %s was NOT found. Please make sure calabash is installed.' % cmd)


####################################################################################################
# Helper methods
####################################################################################################
def get_config():
    return Config(file_name='capy_conf.yaml', private_file_name='capy_private.yaml')


def read_build(args):
    return args.build[0] if args.build else None


def version():
    print '%s %s' % (NAME, VERSION)
    print DESCRIPTION


def console(build_name, device_name):
    check_calabash()

    config = get_config()
    device = config.device_manager.get_device(device_name)
    build = config.build_manager.check_and_get_build(device.os, build_name)
    print Color.GREEN + "Opening console for device '%s' with '%s'..." % (device.name, build.name) + Color.ENDC
    DeviceRunner(device).open_console(build)


def run(build_name, device_name, test_name, with_report=False):
    check_calabash()

    # save execution start
    start_time = datetime.now().replace(microsecond=0)

    config = get_config()

    device = config.device_manager.get_device(device_name)
    build = config.build_manager.get_build(device.os, build_name)
    test = config.test_manager.get_test(test_name)

    if with_report:
        # use custom loggers
        sys.stdout = STDOUT_LOGGER
        STDOUT_LOGGER.start_for_device(device)
        sys.stderr = STDERR_LOGGER
        STDERR_LOGGER.start_for_device(device)

    if test.before:
        for action in test.before:
            exec_action(action, config, build, device)

    # just to make sure build is available (this will download it if not)
    build = config.build_manager.check_and_get_build(device.os, build_name)
    version_names_getter = lambda: config.build_manager.get_version_names(build)

    print Color.GREEN + "Running '%s' on device '%s' with '%s'..." % (test.name, device.name, build.name) + Color.ENDC
    runner = DeviceRunner(device)
    runner.run_test(test, build, version_names_getter, report=with_report)

    if test.after:
        for action in test.after:
            exec_action(action, config, build, device)

    # show time
    end_time = datetime.now().replace(microsecond=0)
    diff = end_time - start_time
    print '+-------------------------------------------------------------------------'
    print '| Total testing time is: ', diff
    print '+-------------------------------------------------------------------------'

    if with_report and runner.latest_report_dir:
        # move logs
        STDOUT_LOGGER.move_to(runner.latest_report_dir)
        STDERR_LOGGER.stop()
        STDERR_LOGGER.move_to(runner.latest_report_dir)
        STDERR_LOGGER.stop()


def exec_action(test_action, config, build, device):
    print Color.GREEN + "Running action '%s' on device '%s' with '%s'..." % (test_action, device.name, build.name) + Color.ENDC
    if test_action == TestAction.DOWNLOAD:
        config.build_manager.download(build)
    elif test_action == TestAction.INSTALL:
        DeviceRunner(device).install(build)
    elif test_action == TestAction.UNINSTALL:
        DeviceRunner(device).uninstall(build)


def list(builds=False, devices=False, tests=False):
    config = get_config()

    line_start = Color.GREEN

    print line_start + '+------------------------------------------------------------------------------------' + Color.ENDC
    if builds:
        print line_start + '| ' + Color.LIGHT_YELLOW + 'BUILDS:'
        print line_start + '|'
        for os, builds_dict in config.build_manager.builds.iteritems():
            print line_start + '| ' + os
            for name, build in sorted(builds_dict.iteritems()):
                print build.show(line_start + '|    ')
        print line_start + '|------------------------------------------------------------------------------------' + Color.ENDC
    if devices:
        print line_start + '| ' + Color.LIGHT_YELLOW + 'DEVICES:'
        print line_start + '|'
        for name, device in sorted(config.device_manager.devices.iteritems()):
            print device.show(line_start + '| ')
        print line_start + '|------------------------------------------------------------------------------------' + Color.ENDC
    if tests:
        print line_start + '| ' + Color.LIGHT_YELLOW + 'TESTS:'
        print line_start + '|'
        for name, test in sorted(config.test_manager.tests.iteritems()):
            print test.show(line_start + '| ')
        print line_start + '+------------------------------------------------------------------------------------' + Color.ENDC


def download(build_name, os):
    check_calabash()

    config = get_config()
    build = config.build_manager.get_build(os, build_name)
    print Color.GREEN + "Downloading build '%s' for '%s'..." % (build.name, build.os) + Color.ENDC
    config.build_manager.download(build)


def install(build_name, device_name):
    check_calabash()

    config = get_config()
    device = config.device_manager.get_device(device_name)
    build = config.build_manager.check_and_get_build(device.os, build_name)
    print Color.GREEN + "Installing '%s' to device '%s'..." % (build.name, device.name) + Color.ENDC
    DeviceRunner(device).install(build)


def uninstall(build_name, device_name):
    check_calabash()

    config = get_config()
    device = config.device_manager.get_device(device_name)
    build = config.build_manager.check_and_get_build(device.os, build_name)
    print Color.GREEN + "Uninstalling '%s' from device '%s'..." % (build.name, device.name) + Color.ENDC
    DeviceRunner(device).uninstall(build)


###########################################################
# Main
###########################################################
def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('-b', '--build', nargs=1, metavar='B',
                        help="Choose different build B to use for tests")
    parser.add_argument('-c', '--console', nargs=1, metavar='D',
                        help="Open calabash console for device D")
    parser.add_argument('-d', '--download', choices=['android', 'ios'],
                        help="Download build for given platform")
    parser.add_argument('-i', '--install', nargs=1, metavar='D',
                        help="Install current build on device D")
    parser.add_argument('-l', '--list', action='store_true',
                        help="List all supported builds, devices and tests")
    parser.add_argument('-lb', '--list-build', action='store_true',
                        help="List all supported builds")
    parser.add_argument('-ld', '--list-device', action='store_true',
                        help="List all supported devices")
    parser.add_argument('-lt', '--list-test', action='store_true',
                        help="List all supported tests")
    parser.add_argument('-r', '--run', nargs=2, metavar=('D', 'T'),
                        help="Run test T on device D")
    parser.add_argument('-rr', '--run-report', nargs=2, metavar=('D', 'T'),
                        help="Run test T on device D and create HTML report")
    parser.add_argument('-v', '--version', action='store_true',
                        help="Show version")
    parser.add_argument('-u', '--uninstall', nargs=1, metavar='D',
                        help="Uninstall build from device D")
    args = parser.parse_args()

    # run
    if args.run:
        run(build_name=read_build(args), device_name=args.run[0], test_name=args.run[1])
    elif args.run_report:
        run(build_name=read_build(args), device_name=args.run_report[0], test_name=args.run_report[1], with_report=True)
    # console
    elif args.console:
        console(build_name=read_build(args), device_name=args.console[0])
    # list
    elif args.list:
        list(builds=True, devices=True, tests=True)
    elif args.list_build:
        list(builds=True)
    elif args.list_device:
        list(devices=True)
    elif args.list_test:
        list(tests=True)
    # version
    elif args.version:
        version()
    # download
    elif args.download:
        download(build_name=read_build(args), os=args.download)
    # install
    elif args.install:
        install(build_name=read_build(args), device_name=args.install[0])
    # uninstall
    elif args.uninstall:
        uninstall(build_name=read_build(args), device_name=args.uninstall[0])
    # show help by default
    else:
        parser.parse_args(['--help'])

    # check for updates
    check_version()


################################
# run main
################################
if __name__ == '__main__':
    main()
