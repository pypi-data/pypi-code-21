'''
Created on 10 Aug 2016

@author: Ben Couturier
'''
import os
import unittest
import logging
import shutil
from lbinstall.PackageManager import PackageManager


class Test(unittest.TestCase):

    def setUp(self):
        self.filename = "A-1.0.0-1.noarch.rpm"
        self.url = "http://lhcb-rpm.web.cern.ch/lhcb-rpm/lhcbdevtests/"\
                   "%s" % self.filename
        if os.environ.get('MYSITEROOT', None):
            self.siteroot = os.environ['MYSITEROOT']
        else:
            self.siteroot = "/tmp/siteroot"
        shutil.rmtree(self.siteroot, ignore_errors=True)
        if not os.path.exists(self.siteroot):
            os.makedirs(self.siteroot)
            os.makedirs("%s/tmp" % self.siteroot)
        logging.basicConfig()
        if not os.path.exists(self.filename):
            try:
                # Python 3 workaround
                import urllib.request as urllib
            except:
                import urllib
            urllib.urlretrieve(self.url, self.filename)

    def tearDown(self):
        shutil.rmtree(self.siteroot, ignore_errors=True)

    def testGetGroup(self):
        ''' Check that we can get the group of a given RPM  '''
        pm = PackageManager(self.filename, self.siteroot)
        print("RPM Group: %s" % pm.getGroup())
        self.assertEqual(pm.getGroup(), "default", "Could not get group")

    def testRequires(self):
        ''' Check that we can get the list of requirements of a given RPM
        Returned as a list of triplet (reqname, reqversion, flag) '''
        pm = PackageManager(self.filename, self.siteroot)
        print("RPM Requires:", pm.getRequires())
        res = pm._getRequires()
        ref = [('B', '1.0.0-1', 'EQ'),
               ('C', '1.0.0-1', 'EQ'),
               ('rpmlib(PayloadFilesHavePrefix)', '4.0-1', 'LE'),
               ('rpmlib(CompressedFileNames)', '3.0.4-1', 'LE')]
        self.assertEquals(res, ref, "List of requires")

    def testProvides(self):
        ''' Check that we can get the list of provides of a given RPM  '''
        pm = PackageManager(self.filename, self.siteroot)
        print("RPM Provides:", pm.getProvides())
        res = pm._getProvides()
        ref = [('A', '1.0.0-1', 'EQ')]
        self.assertEquals(res, ref, "List of provides")

    def testGetPrefixes(self):
        ''' Check that we extract the RPM prefix properly  '''
        pm = PackageManager(self.filename, self.siteroot)
        ret = pm.getPrefixes()
        print("RPM Prefixes:", ret)
        ref = ['/opt/LHCbSoft']
        self.assertEquals(ret, ref, "RPM Prefix")

    def testExtract(self):
        ''' Check that we can extract a file  '''
        try:
            tmp_dir = self.siteroot
            pm = PackageManager(self.filename, self.siteroot, tmp_dir=tmp_dir)
            prefixmap = {pm.getPrefixes()[0]: self.siteroot}
            pm.setrelocatemap(prefixmap)
            pm.extract(prefixmap)
            pm.checkFileSizesOnDisk()
            pm.removeFiles()
        except Exception as e:
            self.fail("Failed due to: %s" % e)

    def testGetTopDir(self):
        ''' Check for the top directory of the files in the RPM  '''
        pm = PackageManager(self.filename, self.siteroot)
        ref = "./opt/LHCbSoft/"
        self.assertEquals(pm.getTopDir(),
                          ref, "Checking the topdir for the package")

    def testGetPackage(self):
        ''' Check that we can get the list of provides of a given RPM  '''
        pm = PackageManager(self.filename, self.siteroot)
        _res = pm.getPackage()
        self.assertEquals(_res.name, 'A', "Check the name of the package")

    def testGetFileMetadata(self):
        ''' Checks the method that returns the list of files'''
        pm = PackageManager(self.filename, self.siteroot)
        res = pm.getFileMetadata()
        self.assertTrue(len(res) == 172, "172 files and dirs in RPM")

if __name__ == "__main__":
    # import sys;sys.argv = ['', 'Test.testFindPackage']
    unittest.main()
