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
SQLAlchemy model for the DB of installed packages.

:author: Ben Couturier
'''

from sqlalchemy import Column, ForeignKey, Integer, String
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship
from sqlalchemy import UniqueConstraint

from lbinstall.Model import Provides as dmProvides
from lbinstall.Model import Requires as dmRequires
from lbinstall.Model import Package as dmPackage
from lbinstall.Model import normalizeVersionRelease

Base = declarative_base()


class Package(Base):
    __tablename__ = 'package'
    id = Column(Integer, primary_key=True)
    name = Column(String(250), nullable=False)
    version = Column(String(250), nullable=False)
    release = Column(String(250), nullable=False)
    checksum = Column(String(250), nullable=True)
    checksum_type = Column(String(50), nullable=True)
    group = Column(String(250), nullable=False)
    location = Column(String(1000), nullable=True)
    relocatedLocation = Column(String(1000), nullable=True)
    postinstallrun = Column(String(1), nullable=True)
    UniqueConstraint('name', 'version', name='PackageDuplication')

    def toDmPackage(self):
        """ Converts a db package to DependencyManager format

        :returns: the DependencyManager package"""
        p = dmPackage(name=self.name,
                      version=self.version,
                      release=self.release,
                      group=self.group,
                      relocatedLocation=self.relocatedLocation)
        return p

    def rpmName(self):
        """ Formats the name of the RPM package

        :returns: the rpm name"""
        return "%s-%s-%s" % (self.name, self.version, self.release)


class Require(Base):
    __tablename__ = 'require'
    id = Column(Integer, primary_key=True)
    name = Column(String(250))
    version = Column(String(250), nullable=True)
    release = Column(String(250), nullable=True)
    flags = Column(String(250), nullable=True)
    package_id = Column(Integer, ForeignKey('package.id'))
    package = relationship(Package, backref="requires")

    def toDmRequires(self):
        """ Converts a db require to DependencyManager format

        :returns: the DependencyManager require"""
        r = dmRequires(name=self.name,
                       version=self.version,
                       release=self.release,
                       flags=self.flags)
        return r


class Provide(Base):
    __tablename__ = 'provide'
    id = Column(Integer, primary_key=True)
    name = Column(String(250))
    version = Column(String(250))
    release = Column(String(250), nullable=True)
    flags = Column(String(250), nullable=True)
    package_id = Column(Integer, ForeignKey('package.id'))
    package = relationship(Package, backref="provides")

    def toDmProvides(self):
        """ Converts a db provide to DependencyManager format

        :returns: the DependencyManager provide"""

        # Hack put in place as we seem to have some provides
        # where the release is a number appended at the end
        # of the version "-" separated.
        (tmpver, tmprel) = normalizeVersionRelease(self.version, self.release)
        p = dmProvides(name=self.name,
                       version=tmpver,
                       release=tmprel,
                       flags=self.flags)
        return p
