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
Test for ChaineDBManager ops.
'''
import unittest
import os
import logging
import shutil
from lbinstall.db.ChainedDBManager import ChainedConfigManager
from lbinstall.Installer import Installer
from lbinstall.db.DBManager import DBManager
from lbinstall.LHCbConfig import Config


class Test(unittest.TestCase):

    configFile = None

    def setUp(self):
        logging.basicConfig(level=logging.INFO)
        if os.environ.get('MYSITEROOT', None):
            self.siteroot = os.environ['MYSITEROOT']
        else:
            self.siteroot = "/tmp/siteroot"
        # Prior to doing the test, remove the Installer folder
        shutil.rmtree(self.siteroot, ignore_errors=True)
        dbpath = "%s/var/lib/db/packages.db" % self.siteroot
        self.configFile = "%s/etc/chainedDBs.json" % self.siteroot
        if os.path.exists(dbpath):
            os.unlink(dbpath)
        self.config = Config(None, skipConfig=True)
        self.config.repos['lhcbdev'] = {'url': 'http://lhcb-rpm.web.cern.ch/'
                                               'lhcb-rpm/lhcbdevtests'}
        self._mgr = Installer(self.siteroot, config=self.config,
                              chained_db_list=['/cvmfs/lhcbdev.cern.ch/test'])
        self.db = DBManager(':memory:', 'var/lib/db/packages.db',
                            self._mgr._chainedDBManger)

    def tearDown(self):
        shutil.rmtree(self.siteroot, ignore_errors=True)

    def testgetDBPackages(self):
        ''' Check the get of remote package'''
        tmp = list(self.db.getDBPackages("COMPAT"))
        self.assertNotEqual(len(tmp), 0,
                            "At least one package in the remote db")

    def testCheckifAPackagesIsInstalled(self):
        ''' Check the get of remote package'''
        tmp = list(self.db.getDBPackages("COMPAT"))
        p = tmp[0]
        self.assertTrue(self.db.isPackagesInstalled(p),
                        "The package is installed in the remote db")

    def testfindProvidesByName(self):
        ''' Check if a given provider is found by name on the chained db'''
        tmp = self.db.findProvidesByName("COMPAT")
        self.assertNotEqual(len(tmp), 0,
                            "At least one provider in the remote db")

    def testfindRequiresByName(self):
        ''' Check if a given require is found by name on the chained db'''
        tmp = self.db.findRequiresByName("COMPAT")
        self.assertNotEqual(len(tmp), 0,
                            "At least one require in the remote db")

    def testfindPackagesRequiringDBPackage(self):
        '''
        Check findPackagesRequiringDBPackage retrieves all the require
        and providers from remote db
        '''
        tmp = list(self.db.getDBPackages("COMPAT"))
        dbp2 = tmp[0]
        reqpacks = self.db.findPackagesRequiringDBPackage(dbp2)
        from pprint import pprint
        pprint(reqpacks)
        self.assertNotEqual(len(tmp), 0,
                            "At least one package requires COMPAT in "
                            "the remote db")


if __name__ == "__main__":
    # import sys;sys.argv = ['', 'Test.testInsert']
    unittest.main()
