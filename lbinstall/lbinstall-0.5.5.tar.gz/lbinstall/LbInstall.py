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

:author: Ben Couturier
'''
from __future__ import print_function
import logging
import optparse
import os
import re
import sys
import traceback

from os.path import abspath

from lbinstall.Installer import Installer

# Class for known install exceptions
###############################################################################


class LbInstallException(Exception):
    """ Custom exception for lb-install

    :param msg: the exception message
    """

    def __init__(self, msg):
        """ Constructor for the exception """
        # super(LbInstallException, self).__init__(msg)
        Exception.__init__(self, msg)


# Classes and method for command line parsing
###############################################################################


class LbInstallOptionParser(optparse.OptionParser):
    """ Custom OptionParser to intercept the errors and rethrow
    them as lbInstallExceptions """

    def error(self, msg):
        """
        Arguments parsing error message exception handler

        :param msg: the message of the exception
        :return: Raises LbInstallException with the exception message
        """
        raise LbInstallException("Error parsing arguments: " + str(msg))

    def exit(self, status=0, msg=None):
        """
        Arguments parsing error message exception handler

        :param status: the status of the application
        :param msg: the message of the exception
        :return: Raises LbInstallException with the exception message
        """
        raise LbInstallException("Error parsing arguments: " + str(msg))


class LbInstallClient(object):
    """ Main class for the tool """

    MODE_INSTALL = "install"
    MODE_QUERY = "query"
    MODE_LIST = "list"
    MODE_UPDATE = "update"
    MODE_CHECK = "check"
    MODE_RM = "remove"
    MODE_DOWNLOAD = "download"
    MODE_REINSTALL = "reinstall"
    MODE_DISPLAY_GRAPH = "graph"

    MODES = [MODE_INSTALL, MODE_QUERY, MODE_LIST, MODE_RM, MODE_UPDATE,
             MODE_CHECK, MODE_DOWNLOAD, MODE_REINSTALL,
             MODE_DISPLAY_GRAPH]

    def __init__(self, configType, arguments=None,
                 dry_run=False, prog="LbInstall"):
        """ Common setup for both clients """
        self.configType = configType
        self.log = logging.getLogger(__name__)
        self.arguments = arguments
        self.installer = None
        self.prog = prog
        self.dry_run = None
        self.justdb = None
        self.query_provides = False
        self.is_regex = False
        self.overwrite = None
        self.tmp_dir = None
        self.pool_size = 5

        parser = LbInstallOptionParser(usage=usage(self.prog))
        # parser.disable_interspersed_args()
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
        parser.add_option('--dry-run',
                          dest="dryrun",
                          default=False,
                          action="store_true",
                          help="Only print the command that will be run")
        parser.add_option('--just-db',
                          dest="justdb",
                          default=False,
                          action="store_true",
                          help="Install the packages to the local DB only")
        parser.add_option('--no-strict',
                          dest="no_strict",
                          default=False,
                          action="store_true",
                          help="Disables the fail if a dependency cannot "
                               "be resolved")
        parser.add_option('--overwrite',
                          dest="overwrite",
                          default=False,
                          action="store_true",
                          help="Overwrite the files from the package")
        parser.add_option('--force',
                          dest="force",
                          default=False,
                          action="store_true",
                          help="Force action(e.g. removal of "
                               "required package)")
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
        parser.add_option('--nodeps',
                          dest="nodeps",
                          default=False,
                          action="store_true",
                          help="install the package without dependencies")
        parser.add_option('--withdeps',
                          dest="withdeps",
                          default=False,
                          action="store_true",
                          help="update the package with all dependencies. It"
                               "works only on update method")
        parser.add_option('--tmp_dir',
                          dest="tmp_dir",
                          default=None,
                          action="store",
                          help="specify a custom tmp directory instead of "
                               "the default $SITEROOT/tmp")
        parser.add_option('--chained_database',
                          dest="chained_db",
                          default=None,
                          action="store",
                          help="use a remote database/install area "
                               "in addition to the local one")
        parser.add_option('--download-pool-size',
                          dest="pool_size",
                          default=5,
                          action="store",
                          help="the size of the pool thread"
                               " used to download files")
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
        parser.add_option('--with-regex',
                          dest="is_regex",
                          default=False,
                          action="store_true",
                          help="Allows regular expressions in the "
                               "packages names")
        parser.add_option('--provides',
                          dest="query_provides",
                          default=False,
                          action="store_true",
                          help="Queries the packages that provides the"
                               " argument")
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
                    raise LbInstallException("Please specify MYSITEROOT in "
                                             "the environment or use the "
                                             "--root option")
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

            # Check for chained database:
            chained_db_list = []
            if opts.chained_db:
                if ';' in opts.chained_db:
                    chained_db_list = opts.chained_db.split(';')
                else:
                    chained_db_list = [opts.chained_db]

            if opts.tmp_dir:
                self.tmp_dir = opts.tmp_dir

            # Check for nodeps argument
            nodeps = False
            if opts.nodeps:
                nodeps = True
            if opts.pool_size:
                self.pool_size = int(opts.pool_size)
            if opts.withdeps:
                self.withdeps = True
            else:
                self.withdeps = False
            if opts.query_provides:
                self.query_provides = True
            else:
                self.query_provides = False
            if opts.is_regex:
                self.is_regex = True
            else:
                self.is_regex = False
            if opts.tree_mode:
                self.tree_mode = True
            else:
                self.tree_mode = False

            if opts.dot_filename:
                self.dot_filename = opts.dot_filename
            else:
                self.dot_filename = "output"

            # Checking for strinc flag
            self.strict = not opts.no_strict

            # Setting up repo url customization
            # By default repourl is none, in which case the hardcoded default
            # is used skipConfig allows returning a config with the LHCb
            # repositories
            from lbinstall.LHCbConfig import Config
            conf = Config(opts.repourl, skipConfig=opts.nolhcbrepo)

            #
            for i, url in enumerate(opts.extrarepo):
                conf.repos["extrarepo_%d" % i] = {"url": url}

            # Initializing the installer
            self.installer = Installer(siteroot=siteroot,
                                       disableYumCheck=opts.noyumcheck,
                                       chained_db_list=chained_db_list,
                                       nodeps=nodeps,
                                       config=conf,
                                       tmp_dir=self.tmp_dir,
                                       pool_size=self.pool_size,
                                       strict=self.strict)
            if opts.rpmcache:
                for cachedir in opts.rpmcache:
                    self.installer.addDirToRPMCache(abspath(cachedir))

            # Checking if we should do a dry-run
            self.dry_run = self.dry_run or opts.dryrun

            # Checking if we should do a dry-run
            self.justdb = opts.justdb

            # Shall we overwrite the files if already on disk
            # In principle yes, softer policy for CVMFS installs though...
            self.overwrite = opts.overwrite

            # Getting the function to be invoked
            self.run(opts, args)

        except LbInstallException as lie:
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
            if cmd in LbInstallClient.MODES:
                mode = cmd
            else:
                raise LbInstallException("Unrecognized command: %s" % args)
        else:
            raise LbInstallException("Argument list too short")

        # Now executing the command
        if mode == LbInstallClient.MODE_QUERY:
            # Mode that list packages according to a regexp
            if not self.is_regex:
                new_args = []
                for arg in args[1:]:
                    arg = re.escape(arg)
                    new_args.append(arg)
                args = [args[0]]
                args.extend(new_args)
            if self.query_provides:
                self.installer.queryProviders(*args[1:])
            else:
                self.installer.queryPackages(*args[1:])
        elif mode == LbInstallClient.MODE_LIST:
            # Mode that list packages according to a regexp
            self.installer.listInstalledPackages(* args[1:])
        elif (mode == LbInstallClient.MODE_RM or
              mode == LbInstallClient.MODE_INSTALL or
              mode == LbInstallClient.MODE_UPDATE or
              mode == LbInstallClient.MODE_CHECK or
              mode == LbInstallClient.MODE_DOWNLOAD or
              mode == LbInstallClient.MODE_DISPLAY_GRAPH or
              mode == LbInstallClient.MODE_REINSTALL):
            i = 1
            first_pass = True
            rpms_list = []
            while i < len(args):
                rpmname = args[i]
                if rpmname is None and first_pass:
                    raise LbInstallException("Please specify at least the name"
                                             " of the RPM to install")
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
            if mode == LbInstallClient.MODE_CHECK:
                for rpmname, version, release in rpms_list:
                    self.log.info("Verifing installed packages : %s %s %s"
                                  % (rpmname, version, release))
                self.installer.checkPackgesFromTuples(rpms_list)
            elif mode == LbInstallClient.MODE_RM:
                for rpmname, version, release in rpms_list:
                    self.log.info("Removing RPM: %s %s %s"
                                  % (rpmname, version, release))
                self.installer.remove(rpms_list, force=opts.force,
                                      justdb=self.justdb,
                                      dry_run=self.dry_run)
            elif mode == LbInstallClient.MODE_DISPLAY_GRAPH:
                for rpmname, version, release in rpms_list:
                    self.log.info("Displaying graph for RPMs: %s %s %s"
                                  % (rpmname, version, release))
                    self.installer.displayDependenciesGraph(
                        rpms_list, tree_mode=self.tree_mode,
                        filename=self.dot_filename)
            elif mode == LbInstallClient.MODE_DOWNLOAD:
                for rpmname, version, release in rpms_list:
                    self.log.info("Downloading RPMs for : %s %s %s"
                                  % (rpmname, version, release))
                self.installer.install(rpms_list, download_only=True,
                                       justdb=self.justdb,
                                       overwrite=self.overwrite,
                                       dry_run=self.dry_run)
            elif mode == LbInstallClient.MODE_INSTALL:
                for rpmname, version, release in rpms_list:
                    self.log.info("Installing RPM: %s %s %s"
                                  % (rpmname, version, release))
                self.installer.install(rpms_list,
                                       justdb=self.justdb,
                                       overwrite=self.overwrite,
                                       dry_run=self.dry_run)
            elif mode == LbInstallClient.MODE_UPDATE:
                for rpmname, version, release in rpms_list:
                    self.log.info("Updating RPM: %s %s %s"
                                  % (rpmname, version, release))
                self.installer.update(rpms_list,
                                      justdb=self.justdb,
                                      dry_run=self.dry_run,
                                      nodeps=(not self.withdeps))
            elif mode == LbInstallClient.MODE_REINSTALL:
                for rpmname, version, release in rpms_list:
                    self.log.info("Reinstalling RPM: %s %s %s"
                                  % (rpmname, version, release))
                self.installer.reinstall(rpms_list,
                                         justdb=self.justdb,
                                         dry_run=self.dry_run,
                                         nodeps=(not self.withdeps))
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

%(cmd)s install <rpmname> [<version> [<release>]]
Installs a RPM from the yum repository

%(cmd)s remove <rpmname> [<version> [<release>]]
Removes a RPM from the local system

%(cmd)s update <rpmname> [<version> [<release>]]
Updates a RPM from the yum repository. The rpmname
needs to be the same as the one installed on the local system and the
version should be grater than the local one, or if equal, the release
should be grater.

%(cmd)s reinstall <rpmname> [<version> [<release>]]
Reinstall a RPM from the yum repository. The rpmname, version and release
needs to be the same as the one installed on the local system

%(cmd)s download <rpmname> [<version> [<release>]]
Downloads a RPM from the yum repository

%(cmd)s query [<rpmname regexp>]
List packages available in the repositories configured with a name
matching the regular expression passed.

%(cmd)s list [<rpmname regexp>]
List packages installed on the system matching the regular expression passed.

%(cmd)s check [<rpmname regexp>]
Verifies is the RPMs are installed correctly on local system.

%(cmd)s graph [<rpmname regexp>]
Generates a dot file to be used to display the dependencies of a rpm

""" % {"cmd": cmd}


def LbInstall(configType="LHCbConfig", prog="LbInstall"):
    """
    Default caller for command line lbinstall client
    :param configType: the configuration used
    :param prog: the name of the executable
    """
    logging.basicConfig(format="%(levelname)-8s: %(message)s")
    logging.getLogger().setLevel(logging.WARNING)
    sys.exit(LbInstallClient(configType, prog=prog).main())

# Main just chooses the client and starts it
if __name__ == "__main__":
    LbInstall()
