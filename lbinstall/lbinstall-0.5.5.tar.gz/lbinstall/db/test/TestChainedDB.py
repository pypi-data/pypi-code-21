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
        self._mgr = Installer(self.siteroot, config=self.config)
        self.db = DBManager(':memory:', 'var/lib/db/packages.db',
                            self._mgr._chainedDBManger)

        from lbinstall.DependencyManager import Package as dmPackage
        from lbinstall.DependencyManager import Provides as dmProvides
        from lbinstall.DependencyManager import Requires as dmRequires

        provides = [dmProvides("P1", "1.0.0", "1"),
                    dmProvides("P", None, None)]
        requires = [dmRequires("P0", "4.2.0", "1")]
        p1 = dmPackage("P1", "1.0.0", "1", group="LHCb")
        for t in provides:
            p1.provides.append(t)
        for t in requires:
            p1.requires.append(t)
        self.db.addPackage(p1, None)

        p2 = dmPackage("P2", "1.0.0", "1", group="LHCb")
        for t in [dmProvides("P2", "1.0.0", "1"), dmProvides("P", None, None)]:
            p2.provides.append(t)

        for t in [dmRequires("P1", "1.0.0", "1")]:
            p2.requires.append(t)
        self.db.addPackage(p2, None)

    def tearDown(self):
        shutil.rmtree(self.siteroot, ignore_errors=True)

    def testRemoteConnections(self):
        ''' Check the remote database connection by validating stats'''
        current_stats = self.db.dbStats()
        # Add a new chained db
        self._mgr._chainedDBManger.addDb('/cvmfs/lhcbdev.cern.ch/test')

        self.db._init_remote_db_connections()

        new_stats = self.db.dbStats()
        for i in range(len(current_stats)):
            self.assertNotEqual(new_stats[i], current_stats[i],
                                "Stats with chained db")

if __name__ == "__main__":
    # import sys;sys.argv = ['', 'Test.testInsert']
    unittest.main()
