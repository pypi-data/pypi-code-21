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
Test for SQLAlchemy interface to the SQL repo of installed packages.
'''
import unittest

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from lbinstall.db.model import Package, Require, Provide, Base

import os
import shutil


class Test(unittest.TestCase):

    def setUp(self):

        # create siteroot - Needed by the Chained DB
        if os.environ.get('MYSITEROOT', None):
            self.siteroot = os.environ['MYSITEROOT']
        else:
            self.siteroot = "/tmp/siteroot"
        shutil.rmtree(self.siteroot, ignore_errors=True)
        os.mkdir(self.siteroot)
        os.mkdir(os.path.join(self.siteroot, 'etc'))

        self.engine = create_engine('sqlite:///:memory:', echo=True)
        Base.metadata.create_all(self.engine)
        Base.metadata.bind = self.engine
        self.DBSession = sessionmaker(bind=self.engine)

    def tearDown(self):
        shutil.rmtree(self.siteroot, ignore_errors=True)

    def testAddPackage(self):
        session = self.DBSession()

        p = Package(name='PACKAGE1',
                    version="1.0.0",
                    release="1",
                    group="LHCb")
        req = Require(name="REQ_PACKAGE0", version="2.1.2")
        req2 = Require(name="REQ_PACKAGE2", version="1.1.0")
        prov = Provide(name="PROV_PACKAGE1", version="1.0.0")
        p.provides.append(prov)
        p.requires.append(req)
        p.requires.append(req2)
        session.add(p)
        session.commit()

        session = self.DBSession()
        packages = session.query(Package).filter_by(name="PACKAGE1").all()
        self.assert_(len(packages) == 1,
                     "There should be one package in the DB called PACKAGE1")

        p2 = packages[0]
        for r2 in p2.requires:
            print("REQ: ", r2.name, " ", p2.version)
        for r in p2.provides:
            print("PROV:", r.name, " ", r.version)

        for p in session.query(Provide) \
                        .filter(Provide.name == "PROV_PACKAGE1").all():
            print(p.name, p.version)

if __name__ == "__main__":
    # import sys;sys.argv = ['', 'Test.testInsert']
    unittest.main()
