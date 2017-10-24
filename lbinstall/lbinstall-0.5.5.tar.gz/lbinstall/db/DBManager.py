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
Interface with the installed package and file DB on the local filesystem.

:author: Ben Couturier
'''
import logging
import os

from lbinstall.db.model import Provide, Require, Package, Base
from lbinstall.db.ChainedDBManager import ChainedConfigManager

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy import and_
import json
import gzip
import re
from lbinstall.Model import Provides as dmProvides
from lbinstall.Model import Requires as dmRequires
from lbinstall.Model import normalizeVersionRelease
from lbinstall.Model import IGNORED_PACKAGES


class DBManager:
    '''
    Class that allows interacting with the SQLite DB  containing thelist
    of installed packages.

    :param filename: the name of the database
    :param relative_filename: the generic relative filename for remote
                              databases
    :param chainedDBmanager: remote databases manager object
    '''

    def __init__(self, filename, relative_filename, chainedDBManager):

        self.hashing_exceptions = {
            # Firs add LCG folder and inside put the version (re.match[1])
            r'^LCG_([^_]*)_(.*)': ['LCG', 1]
        }

        self._filename = filename
        self._relative_filename = relative_filename
        self._chainedDBManager = chainedDBManager
        self.log = logging.getLogger(__name__)
        self._filestore = os.path.join(os.path.dirname(filename), "files")
        # Checking if there is a DB already...
        if not os.path.exists(self._filename):
            self.log.warn("Creating new local package DB at %s"
                          % self._filename)
            self.engine = create_engine('sqlite:///%s' % self._filename)
            Base.metadata.create_all(self.engine)
            Base.metadata.bind = self.engine
        else:
            self.engine = create_engine('sqlite:///%s' % self._filename)

        self.DBSession = sessionmaker(bind=self.engine)
        self.session = None
        self._init_remote_db_connections()

    # Crete remote sessions
    def _init_remote_db_connections(self):
        ''' initializes the remote session from the configuration file '''
        chained_db_lists = self._chainedDBManager.getDbs()
        self.RemoteSessions = []
        for element in chained_db_lists:
            current_path = os.path.join(element, self._relative_filename)
            if not os.path.exists(current_path):
                continue
            tmp_engine = create_engine('sqlite:///%s' % current_path)
            self.RemoteSessions.append({
                'name': element,
                'DBSession': sessionmaker(bind=tmp_engine),
                'current_session': None,
                'path': current_path
                })

    # Get remote session
    def _getRemoteSession(self, remoteSession):
        ''' Return new remote session if needed '''
        if remoteSession['current_session'] is None:
            self.log.debug("Creating a new session for %s" %
                           remoteSession['path'])
            remoteSession['current_session'] = remoteSession['DBSession']()
        return remoteSession['current_session']

    # File metada storage is list of files on disk
    ################################################################
    def _getFMDataStoreName(self, packagename):
        ''' Returns the path for the file that should contain
        the package file metadata '''
        if packagename is None:
            raise Exception("Please specify the package name")
        # Exception handler
        middir = None
        path = None
        for hash_exception in self.hashing_exceptions.keys():
            m = re.match(hash_exception, packagename)
            if m:
                rules = self.hashing_exceptions[hash_exception]
                middir = ""
                counter = 0
                for rule in rules:
                    counter += 1
                    if isinstance(rule, int):
                        subfolder = m.group(rule)
                    else:
                        subfolder = rule
                    middir = os.path.join(middir, subfolder)
                middir = os.path.join(middir, m.group(counter)[0].lower())
                path = os.path.join(self._filestore,
                                    middir,
                                    packagename + ".dat.gz")
                break
        if not path or not os.path.exists(path):
            middir = packagename[0].lower()
            path = os.path.join(self._filestore,
                                middir,
                                packagename + ".dat.gz")
        return path

    def dumpFMData(self, name, filemetadata):
        '''
        Save the file list  to disk

        :param name: the name of the package
        :param filemetadata: the metadata of the package
        '''
        filename = self._getFMDataStoreName(name)
        if not os.path.exists(os.path.dirname(filename)):
            os.makedirs(os.path.dirname(filename))

        # This because in python 2.6 you cannot use
        # with with GzipFile...
        f = None
        try:
            f = gzip.open(filename, "w")
            try:
                data = bytes(json.dumps(filemetadata), 'utf-8')
            except:
                data = bytes(json.dumps(filemetadata))
            f.write(data)
        except:
            raise
        finally:
            if f is not None:
                f.close()

    def loadFMData(self, name):
        ''' Save the file list  to disk

        :param name: the name of the package
        '''
        filename = self._getFMDataStoreName(name)

        ret = None
        # This because in python 2.6 you cannot use
        # with with GzipFile...
        f = None
        try:
            f = gzip.open(filename, "r")
            data = f.read()
            data = data.decode("utf-8")
            ret = json.loads(data)
        except:
            pass
        finally:
            if f is not None:
                f.close()
        return ret

    def removeFMData(self, name):
        ''' Save the file list  to disk

        :param name: the name of the package'''
        filename = self._getFMDataStoreName(name)
        if os.path.exists(filename):
            os.unlink(filename)

    def _getSession(self):
        ''' Return new session if needed '''
        if self.session is None:
            self.session = self.DBSession()
        return self.session

    def addPackage(self, dmpackage, filemetadata):
        '''
        takes a package object from the DependencyManager and stores
        it to the DB. Just matches the two structures, probably can be
        done better need to review those classes in view of the new
        integration of SQLAlchemy...

        :param dmpackage: the package in DependencyManager format
        :param filemetadata: the file metadata map
        '''

        # First saving the metadata in a file...
        self.dumpFMData(dmpackage.rpmName(), filemetadata)
        # Now the DB part
        session = self._getSession()
        pack = Package(name=dmpackage.name,
                       version=dmpackage.version,
                       release=dmpackage.release,
                       group=dmpackage.group,
                       location=dmpackage.location,
                       relocatedLocation=dmpackage.relocatedLocation)

        for r in dmpackage.requires:
            req = Require(name=r.name,
                          version=r.version,
                          flags=r.flags)
            pack.requires.append(req)

        for p in dmpackage.provides:
            prov = Provide(name=p.name,
                           version=p.version,
                           flags=p.flags)
            pack.provides.append(prov)
        session.add(pack)
        session.commit()
        return pack

    def setPostInstallRun(self, dbpackage, value):
        '''
        Sets the postInstallRunFlag...

        :param dbpackage: the package in db format
        :param value: the result of the post install script
        '''
        session = self._getSession()
        matching = session.query(Package) \
                          .filter(and_(Package.name == dbpackage.name,
                                       Package.version == dbpackage.version,
                                       Package.release == dbpackage.release)) \
                          .all()
        matching[0].postinstallrun = value
        # package = session.merge(package) # Didn't work for some reason...
        dbpackage.postinstallrun = value
        session.commit()

    def removePackage(self, dmpackage):
        '''
        takes a package object from the DependencyManager and remove
        the related entries in the DB

        :param dmpackage: the package in DependencyManager format
        '''
        # Find the DB part
        session = self._getSession()
        matching = session.query(Package) \
                          .filter(and_(Package.name == dmpackage.name,
                                       Package.version == dmpackage.version,
                                       Package.release == dmpackage.release)) \
                          .all()
        # Delete without forgetting provides and requires
        for p in matching:
            for r in p.requires:
                session.delete(r)
            for r in p.provides:
                session.delete(r)
            session.delete(p)
        session.commit()

        # Removing the metadata for the package
        self.removeFMData(dmpackage.rpmFileName())

    def dbStats(self):
        ''' Global DB stats used for tests '''
        session = self._getSession()

        local_stats = (session.query(Package).count(),
                       session.query(Provide).count(),
                       session.query(Require).count())
        # Add the remote stats
        remote_stats = [0, 0, 0]
        for remote_session in self.RemoteSessions:
            session = self._getRemoteSession(remote_session)
            remote_stats[0] += session.query(Package).count()
            remote_stats[1] += session.query(Provide).count()
            remote_stats[2] += session.query(Require).count()

        full_stats = (local_stats[0] + remote_stats[0],
                      local_stats[1] + remote_stats[1],
                      local_stats[2] + remote_stats[2])
        return full_stats

    def findPackagesWithProv(self, reqname, local_only=False):
        """
        Return a list of packages providing a specific req

        :param reqname: the requirement name
        :param local_only: flag to search only in the local database

        :return: the list of packages providing the specific req
        """
        session = self._getSession()
        ids = []
        for p in session.query(Provide).filter(Provide.name == reqname).all():
            ids.append(p.package.id)

        ret = []
        for pid in ids:
            for p in session.query(Package).filter(Package.id == pid):
                dmpack = p.toDmPackage()
                for prov in p.provides:
                    dmpack.provides.append(prov.toDmProvides())
                for req in p.requires:
                    dmpack.requires.append(req.toDmRequires())
                ret.append(dmpack)

        if local_only:
            return ret
        # Search the remote chained dbs
        for remote_session in self.RemoteSessions:
            session = self._getRemoteSession(remote_session)
            ids = []
            for p in session.query(Provide).filter(
                    Provide.name == reqname).all():
                ids.append(p.package.id)
            for pid in ids:
                for p in session.query(Package).filter(Package.id == pid):
                    dmpack = p.toDmPackage()
                    for prov in p.provides:
                        dmpack.provides.append(prov.toDmProvides())
                    for req in p.requires:
                        dmpack.requires.append(req.toDmRequires())
                    ret.append(dmpack)
        return ret

    def findPackagesWithReq(self, reqname, local_only=False):
        """
        Return a list of packages requiring a specific req

        :param reqname: the requirement name
        :param local_only: flag to search only in the local database

        :return: the list of packages requiring the specific req
        """
        session = self._getSession()
        ids = set()
        for p in session.query(Require).filter(Require.name == reqname).all():
            ids.add(p.package.id)

        ret = []
        for pid in ids:
            for p in session.query(Package).filter(Package.id == pid):
                dmpack = p.toDmPackage()
                for prov in p.provides:
                    dmpack.provides.append(prov.toDmProvides())
                for req in p.requires:
                    dmpack.requires.append(req.toDmRequires())
                ret.append(dmpack)

        if local_only:
            return ret
        # Search the remote chained dbs
        for remote_session in self.RemoteSessions:
            session = self._getRemoteSession(remote_session)
            ids = []
            for p in session.query(Require).filter(
                    Require.name == reqname).all():
                ids.append(p.package.id)
            for pid in ids:
                for p in session.query(Package).filter(Package.id == pid):
                    dmpack = p.toDmPackage()
                    for prov in p.provides:
                        dmpack.provides.append(prov.toDmProvides())
                    for req in p.requires:
                        dmpack.requires.append(req.toDmRequires())
                    ret.append(dmpack)
        return ret

    def findRequiresByName(self, reqname):
        '''
        Return a list of requirements with a specific name
        The matching is done directly in python

        :param reqname: the requirement name

        :return: the list of requirements with the specific name

        '''
        session = self._getSession()
        ret = []
        for p in session.query(Require).filter(Require.name == reqname).all():
            ret.append(dmRequires(p.name,
                                  p.version,
                                  p.release,
                                  flags=p.flags))
        for remote_session in self.RemoteSessions:
            session = self._getRemoteSession(remote_session)
            for p in session.query(Require).filter(
                    Require.name == reqname).all():
                ret.append(dmRequires(p.name,
                                      p.version,
                                      p.release,
                                      flags=p.flags))
        return ret

    def findProvidesByName(self, reqname):
        '''
        Return a list of providers with a specific name
        The matching is done directly in python

        :param reqname: the providers name

        :return: the list of providers with the specific name
        '''
        session = self._getSession()
        ret = []
        for p in session.query(Provide).filter(Provide.name == reqname).all():
            ret.append(dmProvides(p.name,
                                  p.version,
                                  p.release,
                                  flags=p.flags))
        for remote_session in self.RemoteSessions:
            session = self._getRemoteSession(remote_session)
            for p in session.query(Provide).filter(
                    Provide.name == reqname).all():
                ret.append(dmProvides(p.name,
                                      p.version,
                                      p.release,
                                      flags=p.flags))
        return ret

    # Tool to check whether the DB provides a specific requirement
    # #############################################################################
    def provides(self, requirement):
        '''
        Check if some software provides a specific requirement

        :param requirement: the requirement name

        :returns: True if a software provides the requirement
        '''
        allprovides = self.findProvidesByName(requirement.name)
        matching = [pr for pr in allprovides if requirement.provideMatches(pr)]

        return len(matching) > 0

    # Listing the installed packages and check whether one is installed
    # #############################################################################
    def isPackagesInstalled(self, p):
        '''
        Check whether a matching package is installed

        :param p: the package that needs to be check

        :returns: true if installed
        '''
        session = self._getSession()
        matching = session.query(Package) \
                          .filter(and_(Package.name == p.name,
                                       Package.version == p.version,
                                       Package.release == p.release)).all()
        # Search the remote chained dbs
        for remote_session in self.RemoteSessions:
            session = self._getRemoteSession(remote_session)
            matching.extend(session.query(Package)
                                   .filter(and_(Package.name == p.name,
                                                Package.version == p.version,
                                                Package.release == p.release))
                                   .all())
        return len(matching) > 0

    def listPackages(self, match=None, vermatch=None, relmatch=None):
        '''
        List the triplets name, version, release

        :param match: Regex for the name of the package
        :param vermatch: Regex for the version of the package
        :param relmatch: Regex for the release of the package

        :returns the list of tuples including the name, version, release and
                 source of the database packages.
        '''
        for (p, source) in self.getDBPackages(match, vermatch, relmatch, True):
            yield (p.name, p.version, p.release, source)

    def getDBPackages(self, match=None, vermatch=None, relmatch=None,
                      show_source=False, local_only=False, exact_search=False):
        '''
        Return the packages matching a given

        :param match: Regex for the name of the package
        :param vermatch: Regex for the version of the package
        :param relmatch: Regex for the release of the package
        :param show_source: If True, the source (local/remote) is included
        :param local_only: If True, only local search is performed
        :param exact_search: if True, the exact name match will be retained

        :returns: the lists of database packages
        '''
        if match is None:
            match = "%"
        else:
            if not exact_search:
                match = match + "%"
        if vermatch is None:
            vermatch = "%"
        if relmatch is None:
            relmatch = "%"
        session = self._getSession()
        for p in session.query(Package) \
                        .filter(and_(Package.name.like(match),
                                     Package.version.like(vermatch),
                                     Package.release.like(relmatch))).all():
            if show_source:
                yield (p, " local")
            else:
                yield p
        if not local_only:
            # Search the remote chained dbs
            for remote_session in self.RemoteSessions:
                session = self._getRemoteSession(remote_session)
                for p in session.query(Package).filter(
                        and_(Package.name.like(match),
                             Package.version.like(vermatch),
                             Package.release.like(relmatch))).all():
                    if show_source:
                        yield (p, remote_session['name'])
                    else:
                        yield p

    def getPackages(self, match=None, vermatch=None, relmatch=None,
                    local_only=False, exact_search=False):
        '''
        Return the packages matching a given name

        :param match: Regex for the name of the package
        :param vermatch: Regex for the version of the package
        :param relmatch: Regex for the release of the package
        :param local_only: If True, only local search is performed
        :param exact_search: if True, the exact name match will be retained

        :returns: the lists of database packages
        '''
        packages = self.getDBPackages(match=match,
                                      vermatch=vermatch,
                                      relmatch=relmatch,
                                      local_only=local_only,
                                      exact_search=exact_search)
        ret = []
        for p in packages:
            dmpack = p.toDmPackage()
            for prov in p.provides:
                dmpack.provides.append(prov.toDmProvides())
            for req in p.requires:
                dmpack.requires.append(req.toDmRequires())
            ret.append(dmpack)
        return ret

    # Checking dependencies between installed packages
    # #############################################################################
    def findPackagesRequiringPackage(self, match=None, vermatch=None,
                                     relmatch=None, local_only=False):
        ''' Returns list of packages depending on this one

        :param match: Regex for the name of the package
        :param vermatch: Regex for the version of the package
        :param relmatch: Regex for the release of the package
        :param local_only: If True, only local search is performed

        :returns: the lists of database packages
        '''
        dbpackage = list(self.getDBPackages(match=match, vermatch=vermatch,
                                            relmatch=relmatch,
                                            local_only=local_only))[0]
        return self.findPackagesRequiringDBPackage(dbpackage,
                                                   local_only=local_only)

    def findPackagesRequiringDBPackage(self, dbpackage, local_only=False):
        '''
        Return list of packages depending on this one

        :param dbpackage: database package
        :param local_only: If True, only local search is performed

        :returns: the lists of database packages
        '''
        ret = []
        for p in dbpackage.provides:
            if p.name in IGNORED_PACKAGES:
                continue

            self.log.debug("Checking provide %s of %s",
                           p, dbpackage.rpmName())

            (tmpver, tmprel) = normalizeVersionRelease(p.version,
                                                       p.release)
            corresp_req = dmRequires(p.name, tmpver,
                                     tmprel, flags=p.flags)
            requiring = set()
            # Look for packages requiring this
            allrequiring = self.findPackagesWithReq(p.name,
                                                    local_only=local_only)
            for pack in allrequiring:
                for req in pack.requires:
                    if req.provideMatches(p.toDmProvides()):
                        if pack.rpmName() != dbpackage.rpmName():
                            requiring.add(pack)
                        break
            self.log.debug("%s packages require %s" % (len(requiring), p.name))
            if len(requiring) > 0:
                # In this case we need to check whether nobody else
                # is providing the requirement
                otherproviding = set()
                allproviding = self.findPackagesWithProv(p.name,
                                                         local_only=local_only)
                for pack in allproviding:
                    for prov in pack.provides:
                        if corresp_req.provideMatches(prov):
                            # and pack != dbpackage.toDmPackage():
                            # If package requires itself(e.g. providing /bin/sh
                            # that is not a problem so we eliminate oneself
                            # from this list...
                            if pack.rpmName() != dbpackage.rpmName():
                                otherproviding.add(pack)
                            break
                self.log.debug("Nb other packages providing %s: %s"
                               % (p.name, len(otherproviding)))
                if (len(requiring) > 0 and len(otherproviding) == 0):
                    if (p.name, p.version, p.release) not in \
                       [(v1.name, v1.version, v1.release) for (v1, _) in ret]:
                            self.log.debug("Package needed for %s %s %s"
                                           % (p.name, p.version, p.release))
                            ret.append((p, requiring))
        return ret
