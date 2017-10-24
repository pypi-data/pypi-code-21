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
Test of the DependencyManager class
@author: Ben Couturier
'''

from lbinstall import LHCbConfig
from tempfile import mkdtemp
from shutil import rmtree
import logging
import os
import unittest
import xml.dom.minidom
from lbinstall.DependencyManager import *


class TestRepository(unittest.TestCase):

    def setUp(self):
        FORMAT = '%(asctime)-15s %(message)s'
        logging.basicConfig(format=FORMAT)
        import lbinstall.DependencyManager
        lbinstall.DependencyManager.log.setLevel(logging.DEBUG)

        # Config should be soimplified...
        self.siteroot = mkdtemp("testrepo")
        config = LHCbConfig.Config()
        yumConfig = config.getRepoConfig()
        self.lbYumClient = LbYumClient("",
                                       dict([(k, v["url"]) for k, v in
                                            list(yumConfig.items())]))
        repository = Repository("TestRepo",
                                "http://dummyUrl", ".", None, False)
        backend = RepositoryXMLBackend(repository)
        repoxmlfile = os.path.join(os.path.dirname(__file__), "TestRepo.xml")
        dom = xml.dom.minidom.parse(repoxmlfile)
        backend._loadYumMetadataDOM(dom)
        repository.setBackend(backend)
        self.lbYumClient.addRepository(repository)

    def tearDown(self):
        rmtree(self.siteroot)

    def testPackageMatching(self):
        r = Requires("TestPackage", "1.0.0", "1", None, "EQ", None)
        p = self.lbYumClient.findLatestMatchingRequire(r)
        self.assertNotEqual(p, None)
        self.assertEqual(p.version, "1.0.0")

    def testPackageByNameWithRelease(self):
        p = self.lbYumClient.findLatestMatchingName("TP2", "1.2.5", "1")
        self.assertNotEqual(p, None)
        self.assertEqual(p.version, "1.2.5")
        self.assertEqual(p.release, "1")

    def testPackageByNameWithoutRelease(self):
        p = self.lbYumClient.findLatestMatchingName("TP2", "1.2.5", None)
        self.assertNotEqual(p, None)
        self.assertEqual(p.version, "1.2.5")
        self.assertEqual(p.release, "2")

    def testPackageByNameWithoutVersion(self):
        p = self.lbYumClient.findLatestMatchingName("TP2", None, None)
        self.assertNotEqual(p, None)
        self.assertEqual(p.version, "1.2.5")
        self.assertEqual(p.release, "2")

    def testDependencyGreater(self):
        p = self.lbYumClient.findLatestMatchingName("TP2", None, None)
        self.assertNotEqual(p, None)
        self.assertEqual(p.version, "1.2.5")
        self.assertEqual(p.release, "2")

        alldeps = self.lbYumClient.getPackageDependencies(p)
        self.assertEqual(1, len(alldeps))
        self.assertEqual(alldeps[0].name, "TestPackage")
        self.assertEqual(alldeps[0].version, "1.3.7")

    def testDependencyEqual(self):
        p = self.lbYumClient.findLatestMatchingName("TP3", None, None)
        self.assertNotEqual(p, None)
        self.assertEqual(p.version, "1.18.22")
        self.assertEqual(p.release, "2")

        alldeps = self.lbYumClient.getPackageDependencies(p)
        self.assertEqual(1, len(alldeps))
        self.assertEqual(alldeps[0].name, "TestPackage")
        self.assertEqual(alldeps[0].version, "1.2.5")

    def testCyclicDependency(self):
        p = self.lbYumClient.findLatestMatchingName("TCyclicDep", None, None)
        self.assertNotEqual(p, None)
        self.assertEqual(p.version, "1.0.0")
        self.assertEqual(p.release, "1")

        alldeps = self.lbYumClient.getPackageDependencies(p)
        self.assertEqual(2, len(alldeps))

    def testFindReleaseUpdate(self):
        p = self.lbYumClient.findLatestMatchingName("TPRel", "4.2.7", "1")
        self.assertNotEqual(p, None)
        self.assertEqual(p.version, "4.2.7")
        self.assertEqual(p.release, "1")

        req = Requires(p.name, None, None)
        newest = self.lbYumClient.findLatestMatchingRequire(req)
        self.assertEqual(newest.version, "4.2.8")
        self.assertEqual(newest.release, "1")

        req2 = Requires(p.name, p.version, None, flags="EQ")
        newer = self.lbYumClient.findLatestMatchingRequire(req2)
        self.assertEqual(newer.version, "4.2.7")
        self.assertEqual(newer.release, "2")

        # alldeps = self.lbYumClient.getPackageDependencies(p)
        # self.assertEqual(2, len(alldeps))


if __name__ == "__main__":
    unittest.main()
