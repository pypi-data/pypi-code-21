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
"""

Classes that setup and allow interaction with the files on disk in the
InstallArea.


"""
import logging
import os
import subprocess
import sys
import time

# Constants for the dir names
SVAR = "var"
SLIB = "lib"
SDB = "db"
SETC = "etc"
STMP = "tmp"
SUSR = "usr"
SBIN = "bin"

__RCSID__ = "$Id$"


# Utility to run a command
###############################################################################
def call(command):
    """
    Wraps up subprocess call and return caches and returns rc, stderr, stdout

    :param command: the command to be executed

    :returns: touple of the return code, call output and error output
    """
    pc = subprocess.Popen(command,
                          stdout=subprocess.PIPE,
                          stderr=subprocess.PIPE,
                          shell=True)
    out, err = pc.communicate()
    rc = pc.returncode
    return (rc, out, err)


# Utility to run a command
###############################################################################
def callSimple(command):
    """ Simpler wrapper for subprocess

    :param command: the command to be executed

    :returns: the return code of the call
    """
    rc = subprocess.call(command, shell=True)
    return rc


# Check for binary in path
###############################################################################
def checkForCommand(command):
    """ Check whether a command is in the path using which

    :param command: the command to be checked

    :returns: touple of the return code and call output
    """
    whichcmd = "which %s" % command
    rc, out, err = call(whichcmd)  # @UnusedVariable IGNORE:W0612
    return rc, out


# Utilities for log printout
###############################################################################
def printHeader(config):
    """ Prints the standard header as in install_project

    :param config: the configuration whose header is printed
    """
    # Start banner
    thelog = config.log
    start_time = time.strftime("%a, %d %b %Y %H:%M:%S", time.localtime())
    thelog.info('=' * config.line_size)
    thelog.info(('<<< %s - Start of lb-install.py %s with python %s >>>'
                % (start_time, config.script_version,
                   config.txt_python_version)).center(config.line_size))
    thelog.info('=' * config.line_size)
    thelog.debug("Command line arguments: %s" % " ".join(sys.argv))


def printTrailer(config):
    """ Prints the standard trailer as in install_project

    :param config: the configuration whose trailer is printed
    """
    # Trailer
    thelog = config.log
    end_time = time.strftime("%a, %d %b %Y %H:%M:%S", time.localtime())
    thelog.info('=' * config.line_size)
    thelog.info(('<<< %s - End of lb-install.py %s >>>'
                % (end_time, config.script_version)).center(config.line_size))
    thelog.info('=' * config.line_size)


# Class representing the repository
###############################################################################
class InstallArea(object):  # IGNORE:R0902
    """ Class representing the software InstallArea,
    with all related actions

    :param siteroot: the root of the installation area directory
    :param tmp_dir: custom temporary directory to be used in this installation
                    area
    """
    # Initialization of the area
    ##########################################################################
    def __init__(self, config, siteroot, tmp_dir=None):
        """ Init of the InstallArea, check that all directories and config files
        are present.
        """
        self.log = logging.getLogger(__name__)
        self.siteroot = siteroot

        # Making sure the directory containing the DB is initialized
        self.dbdir = os.path.join(self.siteroot, SVAR, SLIB, SDB)
        # Preparing a relative db path for remote use
        self.relative_db_path = os.path.join(SVAR, SLIB, SDB)

        if not os.path.exists(self.dbdir):
            os.makedirs(self.dbdir)
        self.dbpath = os.path.join(self.dbdir, "packages.db")
        self.relative_db_path = os.path.join(
            self.relative_db_path, "packages.db")

        # Initializing yum config
        self.etc = os.path.join(self.siteroot, SETC)
        if not os.path.exists(self.etc):
            os.makedirs(self.etc)

        # tmp directory
        self.tmpdir = os.path.join(self.siteroot, STMP)
        if tmp_dir:
            self.tmpdir = tmp_dir
        if not os.path.exists(self.tmpdir):
            os.makedirs(self.tmpdir)

        # Local bin directory
        self.usrbin = os.path.join(self.siteroot, SUSR, SBIN)
        if not os.path.exists(self.usrbin):
            os.makedirs(self.usrbin)
        # Add the local bin to the path
        os.environ['PATH'] = os.pathsep.join([os.environ['PATH'], self.usrbin])

        # Local lib directory
        self.lib = os.path.join(self.siteroot, SLIB)
        if not os.path.exists(self.lib):
            os.makedirs(self.lib)
        # Add the local bin to the path
        sys.path.append(self.lib)

        # Now calling the configuration method from the specific
        # config module...
        self.config = config
        self.yumConfig = config.getRepoConfig()

        # Defining structures and
        # Checking if all needed tools are available
        self.externalStatus = {}
        self.requiredExternals = []
        self.externalFix = {}
        self._checkPrerequisites()

        # And if all the software is there
        self.initfile = None
        self._checkRepository()

    def createYumClient(self, checkForUpdates=True):
        """ Creates a yum client

        :param checkForUpdates: Flag used to update the back end after setup
                                based on the remote configuration

        :returns: the yum client object
        """
        from .DependencyManager import LbYumClient
        conf = dict([(k, v["url"]) for k, v in list(self.yumConfig.items())])
        return LbYumClient(self.siteroot, conf,
                           checkForUpdates=checkForUpdates)

    def createDBManager(self, chainedDBManager):
        """
        Creeates the local database manager
        :param chainedDBManager: chained database mananger to be used
        :return: the data base manager
        """
        # Setting up our own local software DB
        from .db.DBManager import DBManager
        return DBManager(self.dbpath, self.relative_db_path, chainedDBManager)

    def createChainedDBManager(self):
        """
        Creates the remoted databases manager
        :return: the remote data bases manager
        """
        # Setting up the manager for remote DB
        from lbinstall.db.ChainedDBManager import ChainedConfigManager
        return ChainedConfigManager(self.siteroot)

    def getTmpDir(self):
        """
        Gets the temporary directory in use
        :return: the temporary directory
        """
        return self.tmpdir

    def _checkPrerequisites(self):
        """ Checks that external tools required by this tool to perform
        the installation """
        # Flag indicating whether a crucial external is missing
        # and we cannot run
        externalMissing = False

        for e in self.requiredExternals:
            rc, out = checkForCommand(e)
            self.externalStatus[e] = (rc, out)

        for key, val in list(self.externalStatus.items()):
            rc, exefile = val
            if rc == 0:
                self.log.info("%s: Found %s", key, exefile.strip())
            else:
                self.log.info("%s: Missing - trying compensatory measure", key)
                fix = self.externalFix[key]
                if fix is not None:
                    fix()
                    rc2, out2 = checkForCommand(key)
                    self.externalStatus[key] = (rc2, out2)
                    if rc2 == 0:
                        self.log.info("%s: Found %s", key, out2)
                    else:
                        self.log.error("%s: missing", key)
                        externalMissing = True
                else:
                    externalMissing = True
        return externalMissing

    def _checkRepository(self):
        """ Checks whether the repository was initialized """
        self.initfile = os.path.join(self.etc, "repoinit")
        if not os.path.exists(self.initfile):
            # self.installRpm("LBSCRIPTS")
            with open(self.initfile, "w") as fini:
                fini.write(time.strftime("%a, %d %b %Y %H:%M:%S",
                                         time.localtime()))
        # BC: Remove auto update and add specific command instead
        # else:
        #    self._checkUpdates()

    def getRelocateMap(self):
        """ Returns the mapping between siteroot and extract location
        :returns: the relocation mapping
        """
        # XXX Need to clean up config system
        return self.config.getRelocateMap(self.siteroot)
