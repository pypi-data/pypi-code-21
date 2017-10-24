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

Test that tries a full install of a version of Brunel in /tmp

@author: Ben Couturier
'''
import unittest
import shutil
from lbinstall.Installer import Installer
from lbinstall.LHCbConfig import Config


class Test(unittest.TestCase):

    def setUp(self):
        import os
        import logging
        logging.basicConfig(level=logging.INFO)
        if os.environ.get('MYSITEROOT', None):
            self.siteroot = os.environ['MYSITEROOT']
        else:
            self.siteroot = "/tmp/siteroot"
        # Prior to doing the test, remove the Installer folder
        shutil.rmtree(self.siteroot, ignore_errors=True)
        dbpath = "%s/var/lib/db/packages.db" % self.siteroot
        if os.path.exists(dbpath):
            os.unlink(dbpath)
        config = Config(None, skipConfig=True)
        config.repos['lhcbdev'] = {'url': 'http://lhcb-rpm.web.cern.ch/'
                                          'lhcb-rpm/lhcbdevtests'}
        self._mgr = Installer(self.siteroot, config=config)

    def tearDown(self):
        shutil.rmtree(self.siteroot, ignore_errors=True)

    def testInstall(self):
        '''
        test the procedure that queries for the list of packages to install
        '''
        import os
        if os.environ.get("RUN_LONG_TESTS", None):
            pkgname = "A"
            plist = self._mgr.remoteFindPackage(pkgname)
            self._mgr._install(plist)

if __name__ == "__main__":
    # import sys;sys.argv = ['', 'Test.testFindPackage']
    unittest.main()
