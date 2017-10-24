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
import tempfile

from os.path import abspath

from lbinstall.YumChecker import YumChecker

# Class for known install exceptions
###############################################################################


class LCGYumConsistencyException(Exception):
    """ Custom exception for lb-install

    :param msg: the exception message
    """

    def __init__(self, msg):
        """ Constructor for the exception """
        # super(LCGYumConsistencyException, self).__init__(msg)
        Exception.__init__(self, msg)


# Classes and method for command line parsing
###############################################################################


class LCGYumConsistencyOptionParser(optparse.OptionParser):
    """ Custom OptionParser to intercept the errors and rethrow
    them as LCGYumConsistencyExceptions """

    def error(self, msg):
        """
        Arguments parsing error message exception handler

        :param msg: the message of the exception
        :return: Raises LCGYumConsistencyException with the exception message
        """
        raise LCGYumConsistencyException("Error parsing arguments: " +
                                         str(msg))

    def exit(self, status=0, msg=None):
        """
        Arguments parsing error message exception handler

        :param status: the status of the application
        :param msg: the message of the exception
        :return: Raises LCGYumConsistencyException with the exception message
        """
        raise LCGYumConsistencyException("Error parsing arguments: " +
                                         str(msg))


class LCGYumConsistencyClient(object):
    """ Main class for the tool """

    def __init__(self, configType, arguments=None,
                 dry_run=False, prog="LCGYumConsistency"):
        """ Common setup for both clients """
        self.configType = configType
        self.log = logging.getLogger(__name__)
        self.arguments = arguments
        self.checker = None
        self.prog = prog

        parser = LCGYumConsistencyOptionParser(usage=usage(self.prog))
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
        parser.add_option('--no-details',
                          dest="nodetails",
                          default=False,
                          action="store_true",
                          help="Displays only the name of"
                               " the missing packages.")
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
            siteroot = tempfile.gettempdir()

            # Now setting the logging depending on debug mode...
            if opts.debug or opts.info:
                logging.basicConfig(format="%(levelname)-8s: "
                                           "%(funcName)-25s - %(message)s")
                if opts.info:
                    logging.getLogger().setLevel(logging.INFO)
                else:
                    logging.getLogger().setLevel(logging.DEBUG)
            # Now setting the logging depending on debug mode...

            # Setting up repo url customization
            # By default repourl is none, in which case the hardcoded default
            # is used skipConfig allows returning a config with the LHCb
            # repositories
            from lbinstall.LHCbConfig import Config
            conf = Config()

            # Initializing the installer
            self.checker = YumChecker(siteroot=siteroot,
                                      disableYumCheck=False,
                                      config=conf,
                                      strict=True,
                                      simple_output=opts.nodetails)
            # Getting the function to be invoked
            self.run(opts, args)

        except LCGYumConsistencyException as lie:
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
        if len(args) == 0:
            raise LCGYumConsistencyException("Argument list too short")

        rpms_list = [("LCG_%s" % args[0], None, None)]
        tmp_list = []
        for rpm in rpms_list:
            tmp_list.extend(self.checker.queryPackages(rpm[0],
                                                       rpm[1],
                                                       rpm[2]))
        rpms_list = tmp_list

        self.checker.checkPackgesFromTuples(rpms_list)


# Usage for the script
###############################################################################
def usage(cmd):
    """ Prints out how to use the script...

    :param cmd: the command executed
    """
    cmd = os.path.basename(cmd)
    return """\n
%(cmd)s LCG_VERSION
Verifies the consistency of RPM(s) from the yum repository. It can work without
without any rpname in order to verify the entire yum database

""" % {"cmd": cmd}


def LCGYumConsistency(configType="LHCbConfig", prog="lcgyumcheck"):
    """
    Default caller for command line LCGYumConsistency client
    :param configType: the configuration used
    :param prog: the name of the executable
    """

    logging.basicConfig(format="%(levelname)-8s: %(message)s")
    logging.getLogger().setLevel(logging.WARNING)
    sys.exit(LCGYumConsistencyClient(configType, prog=prog).main())

# Main just chooses the client and starts it
if __name__ == "__main__":
    LCGYumConsistency()
