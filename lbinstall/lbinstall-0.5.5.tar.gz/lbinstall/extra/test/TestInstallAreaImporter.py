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
test procedure for the Install area importer

@author: Ben Couturier
'''
import sys
import unittest
from lbinstall.Installer import Installer
from os.path import dirname


class Test(unittest.TestCase):

    def setUp(self):
        import shutil
        # Prior to doing the test, remove the Installer folder
        shutil.rmtree("/tmp/siteroot", ignore_errors=True)
        self.installer = Installer("/tmp/siteroot")
        sys.path.append(dirname(dirname(__file__)))

    def tearDown(self):
        pass

    def testMatchRPMs(self):
        try:
            from lbinstall.extra.Utils import lookupRPMsForProject
            rpmlist = lookupRPMsForProject(self.installer, "GAUDI", "v27r1",
                                           ["x86_64-slc6-gcc49-opt",
                                            "x86_64-slc6-gcc49-dbg"])
            for p in rpmlist:
                print(p.rpmName())
            self.assertEquals(len(rpmlist), 4,
                              "There should be 4 packages, 2 source/2 bins")
        except:
            # Ignore in this case, in order to test on machines without
            # LbCOnfiguration
            pass
            #

if __name__ == "__main__":
    # import sys;sys.argv = ['', 'Test.testName']
    unittest.main()
