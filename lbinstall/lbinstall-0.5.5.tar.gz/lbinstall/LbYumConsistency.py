###############################################################################
# (c) Copyright 2016 CERN                                                     #
#                                                                             #
# This software is distributed under the terms of the GNU General Public      #
# Licence version 3 (GPL Version 3), copied verbatim in the file "COPYING".   #
#                                                                             #
# In applying this licence, CERN does not waive the privileges and immunities #
# granted to it by virtue of its status as an Intergovernmental Organization  #
# or submit itself to any jurisdiction.                                       #
###############################################################################
'''
Command line client that interfaces to the Installer class

:author: Stefan-Gabriel Chitic
'''
from __future__ import print_function
import logging
import optparse
import os
import re
import sys
import traceback

from os.path import abspath

from lbinstall.YumChecker import YumChecker

# Class for known install exceptions
###############################################################################


class LbYumConsistencyException(Exception):
    """ Custom exception for lb-install

    :param msg: the exception message
    """

    def __init__(self, msg):
        """ Constructor for the exception """
        # super(LbYumConsistencyException, self).__init__(msg)
        Exception.__init__(self, msg)


# Classes and method for command line parsing
###############################################################################


class LbYumConsistencyOptionParser(optparse.OptionParser):
    """ Custom OptionParser to intercept the errors and rethrow
    them as LbYumConsistencyExceptions """

    def error(self, msg):
        """
        Arguments parsing error message exception handler

        :param msg: the message of the exception
        :return: Raises LbYumConsistencyException with the exception message
        """
        raise LbYumConsistencyException("Error parsing arguments: " + str(msg))

    def exit(self, status=0, msg=None):
        """
        Arguments parsing error message exception handler

        :param status: the status of the application
        :param msg: the message of the exception
        :return: Raises LbYumConsistencyException with the exception message
        """
        raise LbYumConsistencyException("Error parsing arguments: " + str(msg))


class LbYumConsistencyClient(object):
    """ Main class for the tool """

    MODE_DISPLAY_GRAPH = "graph"
    MODE_CHECK = "check"

    MODES = [MODE_CHECK, MODE_DISPLAY_GRAPH]

    def __init__(self, configType, arguments=None,
                 dry_run=False, prog="LbYumConsistency"):
        """ Common setup for both clients """
        self.configType = configType
        self.log = logging.getLogger(__name__)
        self.arguments = arguments
        self.checker = None
        self.prog = prog

        parser = LbYumConsistencyOptionParser(usage=usage(self.prog))
        parser.add_option('-d', '--debug',
                          dest="debug",
                          default=False,
                          action="store_true",
                          help="Show debug information")
        parser.add_option('--info',
                          dest="info",
                          default=False,
                          action="store_true",
                          help="Show logging messages with level INFO")
        parser.add_option('--details',
                          dest="details",
                          default=False,
                          action="store_true",
                          help="Displays the full information about the"
                               " missing packages. If not set, only the name"
                               " of the missing packages is diplayed")
        parser.add_option('--repo',
                          dest="repourl",
                          default=None,
                          action="store",
                          help="Specify repository URL")
        parser.add_option('--nolhcbrepo',
                          dest="nolhcbrepo",
                          default=False,
                          action="store_true",
                          help="Do not use the LHCb repositories")
        parser.add_option('--extrarepo',
                          dest="extrarepo",
                          default=[],
                          action="append",
                          help="Specify extra RPM repositories to use")
        parser.add_option('--rpmcache',
                          dest="rpmcache",
                          default=None,
                          action="append",
                          help="Specify RPM cache location")
        parser.add_option('--root',
                          dest="siteroot",
                          default=None,
                          action="store",
                          help="Specify MYSITEROOT on the command line")
        parser.add_option('--disable-update-check',
                          dest="noyumcheck",
                          default=False,
                          action="store_true",
                          help="use the YUM metadata in the cache "
                               "without updating")
        parser.add_option('--disable-yum-check',
                          dest="noyumcheck",
                          default=False,
                          action="store_true",
                          help="use the YUM metadata in the cache "
                               "without updating")
        parser.add_option('--tree-mode',
                          dest="tree_mode",
                          default=False,
                          action="store_true",
                          help="Used in graph mode to view"
                               " the graph as a tree instead"
                               " of a full display")
        parser.add_option('--dot-filename',
                          dest="dot_filename",
                          default='output',
                          action="store",
                          help="The output filename for dot file")
        parser.add_option('--csv-export',
                          dest="csv_name",
                          default=None,
                          action="store",
                          help="The output filename for missing dependencies")
        self.parser = parser

    def main(self):
        """ Main method for the ancestor:
        call parse and run in sequence

        :returns: the return code of the call
        """
        rc = 0
        try:
            opts, args = self.parser.parse_args(self.arguments)
            # Checkint the siteroot and URL
            # to choose the siteroot
            siteroot = None
            if opts.siteroot is not None:
                siteroot = opts.siteroot
                os.environ['MYSITEROOT'] = opts.siteroot
            else:
                envroot = os.environ.get('MYSITEROOT', None)
                if envroot is None:
                    raise LbYumConsistencyException(
                        "Please specify MYSITEROOT in the environment "
                        "or use the --root option")
                else:
                    siteroot = envroot

            # Now setting the logging depending on debug mode...
            if opts.debug or opts.info:
                logging.basicConfig(format="%(levelname)-8s: "
                                    "%(funcName)-25s - %(message)s")
                if opts.info:
                    logging.getLogger().setLevel(logging.INFO)
                else:
                    logging.getLogger().setLevel(logging.DEBUG)

            if opts.csv_name:
                self.csv_name = opts.csv_name
            else:
                self.csv_name = None
            if opts.tree_mode:
                self.tree_mode = True
            else:
                self.tree_mode = False

            if opts.dot_filename:
                self.dot_filename = opts.dot_filename
            else:
                self.dot_filename = "output"

            if opts.details:
                self.no_details = not opts.details
            else:
                self.no_details = True

            # Setting up repo url customization
            # By default repourl is none, in which case the hardcoded default
            # is used skipConfig allows returning a config with the LHCb
            # repositories
            from lbinstall.LHCbConfig import Config
            conf = Config(opts.repourl, skipConfig=opts.nolhcbrepo)

            for i, url in enumerate(opts.extrarepo):
                conf.repos["extrarepo_%d" % i] = {"url": url}

            # Initializing the installer
            self.checker = YumChecker(siteroot=siteroot,
                                      disableYumCheck=opts.noyumcheck,
                                      config=conf,
                                      strict=True,
                                      simple_output=self.no_details)
            if opts.rpmcache:
                for cachedir in opts.rpmcache:
                    self.checker.addDirToRPMCache(abspath(cachedir))

            # Getting the function to be invoked
            self.run(opts, args)

        except LbYumConsistencyException as lie:
            print("ERROR: " + str(lie), file=sys.stderr)
            self.parser.print_help()
            rc = 1
        except:
            print("Exception in lb-install:", file=sys.stderr)
            print('-'*60, file=sys.stderr)
            traceback.print_exc(file=sys.stderr)
            print('-'*60, file=sys.stderr)
            rc = 1
        return rc

    def run(self, opts, args):
        """ Main method for the command

        :param opts: The option list
        :param args: The arguments list
        """
        # Parsing first argument to check the mode
        if len(args) > 0:
            cmd = args[0].lower()
            if cmd in LbYumConsistencyClient.MODES:
                mode = cmd
            else:
                raise LbYumConsistencyException("Unrecognized command: %s" %
                                                args)
        else:
            raise LbYumConsistencyException("Argument list too short")

        if ((mode == LbYumConsistencyClient.MODE_DISPLAY_GRAPH or
             mode == LbYumConsistencyClient.MODE_CHECK)):
            i = 1
            first_pass = True
            rpms_list = []
            while i < len(args):
                rpmname = args[i]
                if rpmname is None and first_pass:
                    raise LbYumConsistencyException(
                        "Please specify at least the name "
                        "of the RPM to install")
                version = None
                release = None
                if i + 1 < len(args) and re.match('([\d\.]+)', args[i+1]):
                    version = args[i+1]
                    i = i+1
                if i + 1 < len(args) and re.match('(\d+)', args[i+1]):
                    release = args[i+1]
                    i = i + 1

                # If the version is in the name of the RPM then use that...
                m = re.match("(.*)-([\d\.]+)-(\d+)$", rpmname)
                if m is not None:
                    rpmname = m.group(1)
                    version = m.group(2)
                    release = m.group(3)
                rpms_list.append((rpmname, version, release))
                i = i + 1
                first_pass = False
            if len(rpms_list) == 0:
                self.log.info("Working with entire database")
                rpms_list = self.checker.queryPackages()
            else:
                tmp_list = []
                for rpm in rpms_list:
                    tmp_list.extend(self.checker.queryPackages(rpm[0],
                                                               rpm[1],
                                                               rpm[2]))
                rpms_list = tmp_list
            if mode == LbYumConsistencyClient.MODE_CHECK:
                for rpmname, version, release in rpms_list:
                    self.log.info("Checking consistency for: %s %s %s"
                                  % (rpmname, version, release))
                self.checker.checkPackgesFromTuples(rpms_list,
                                                    csv_name=self.csv_name)
            elif mode == LbYumConsistencyClient.MODE_DISPLAY_GRAPH:
                for rpmname, version, release in rpms_list:
                    self.log.info("Displaying graph for RPMs: %s %s %s"
                                  % (rpmname, version, release))
                    self.installer.displayDependenciesGraph(
                        rpms_list, tree_mode=self.tree_mode,
                        filename=self.dot_filename)
        else:
            self.log.error("Command not recognized: %s" % mode)


# Usage for the script
###############################################################################
def usage(cmd):
    """ Prints out how to use the script...

    :param cmd: the command executed
    """
    cmd = os.path.basename(cmd)
    return """\n%(cmd)s -  installs software in MYSITEROOT directory'

The environment variable MYSITEROOT MUST be set for this script to work.

It can be used in the following ways:

%(cmd)s check [<rpmname> [<version> [<release>]]
Verifies the consistency of RPM(s) from the yum repository. It can work without
without any rpname in order to verify the entire yum database

%(cmd)s graph [<rpmname regexp>]
Generates a dot file to be used to display the dependencies of a rpm

""" % {"cmd": cmd}


def LbYumConsistency(configType="LHCbConfig", prog="lbyumcheck"):
    """
    Default caller for command line LbYumConsistency client
    :param configType: the configuration used
    :param prog: the name of the executable
    """

    logging.basicConfig(format="%(levelname)-8s: %(message)s")
    logging.getLogger().setLevel(logging.WARNING)
    sys.exit(LbYumConsistencyClient(configType, prog=prog).main())

# Main just chooses the client and starts it
if __name__ == "__main__":
    LbYumConsistency()
