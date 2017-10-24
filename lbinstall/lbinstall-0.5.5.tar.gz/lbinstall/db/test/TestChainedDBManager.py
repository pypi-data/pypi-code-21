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
Test for ChaineDBManager.
'''
import unittest
import os
import logging
import shutil
from lbinstall.db.ChainedDBManager import ChainedConfigManager
from lbinstall.Installer import Installer
import json
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
        self._mgr = Installer(self.siteroot, config=self.config)

    def tearDown(self):
        shutil.rmtree(self.siteroot, ignore_errors=True)

    def testaddChainManager(self):
        '''
        Check that we can add a new chain database into the configuration
        '''
        manager = ChainedConfigManager(self.siteroot)
        # Add a normal path
        manager.addDb('/cvmfs/lhcbdev.cern.ch/test')
        # Test an non existing path
        self.assertRaises(Exception, manager.addDb,
                          '/path/to/non/existing/file/system')

        with open(self.configFile, 'rb') as ftmp:
            data = json.loads(ftmp.read().decode("utf-8"))
        ref = ['/cvmfs/lhcbdev.cern.ch/test']
        self.assertEquals(data, ref, "List of chained db")

    def testgetTheCainedDatabases(self):
        '''
        Check that we can get all the chained database from the configuration
        '''
        ref = ['/cvmfs/lhcbdev.cern.ch/test']
        ref_full = ['/cvmfs/lhcbdev.cern.ch/test',
                    '/path/to/non/existing/file/system']

        with open(self.configFile, 'wb') as f:
            try:
                data = bytes(json.dumps(ref_full), 'utf-8')
            except:
                data = bytes(json.dumps(ref_full))
            f.write(data)

        # We want to get the data from the file in order to test "unmonted"
        # file systems
        manager = ChainedConfigManager(self.siteroot)
        data = manager.getDbs()
        self.assertEquals(data, ref, "List of chained db")

if __name__ == "__main__":
    # import sys;sys.argv = ['', 'Test.testInsert']
    unittest.main()
