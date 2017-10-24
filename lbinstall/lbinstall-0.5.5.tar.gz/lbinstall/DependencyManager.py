###############################################################################
# (c) Copyright 2012-2016 CERN                                                #
#                                                                             #
# This software is distributed under the terms of the GNU General Public      #
# Licence version 3 (GPL Version 3), copied verbatim in the file "COPYING".   #
#                                                                             #
# In applying this licence, CERN does not waive the privileges and immunities #
# granted to it by virtue of its status as an Intergovernmental Organization  #
# or submit itself to any jurisdiction.                                       #
###############################################################################
'''
Parsing of YUM metadata files to retrieve the available packages
and their dependencies.

for example to list all versions of BRUNEL in the repository::

  client = LbYumClient(os.environ['MYSITEROOT'])
   for p in client.listRPMPackages("BRUNEL.*"):
         print "%s - %s" % (p.name, p.version)

:author: Ben Couturier
'''

from lbinstall.Model import Package, Provides
from lbinstall.Model import Requires, VersionedObject, IGNORED_PACKAGES

import xml.dom.minidom
import logging
import gzip
import os
import re
try:
    # Python 3 workaround
    import urllib.request as urllib
except:
    import urllib

# Constants for directory structure
SVAR = "var"
SCACHE = "cache"
SLBYUM = "lbinstall"
SETC = "etc"
SLBYUMCONF = "lbinstall.conf"

# List of packages to ignore for our case
IGNORED_PACKAGES = ["rpmlib(CompressedFileNames)",
                    "/bin/sh",
                    "rpmlib(PayloadFilesHavePrefix)",
                    "rpmlib(PartialHardlinkSets)"]

__RCSID__ = "$Id$"

# Setting up the logger
log = logging.getLogger()


#
# Repository: Facade in front of classes managing the various DB types
#
###############################################################################
class Repository(object):
    """ Class representing a yum repository with all associated metadata

    :param name: The name of the repository
    :param url: The url of the repository
    :param repocachedir: The cache directory used for this repository
    :param backendList: The list of the back-ends
    :param setupBackend: Flag used to setup repository back end. Default is
                         True
    :param checkForUpdates: Flag used to update the back end after setup based
                            on the remote configuration
    """
    def __init__(self, name, url, repocachedir, backendList, setupBackend=True,
                 checkForUpdates=True):
        # These are hardwired dependencies in RPM.
        # we do not need to care about them...
        log.info("Initializing repository: %s / %s" % (name, url))

        # URL of the Yum repository and associated files
        self.name = name
        self.repourl = url
        self.repomdurl = self.repourl + "/repodata/repomd.xml"
        self.localRepomdXml = os.path.join(repocachedir, "repomd.xml")

        # Cache directory and file names
        self.cachedir = repocachedir
        if not os.path.exists(self.cachedir):
            os.makedirs(self.cachedir)

        # Now initializing the backend
        self.availableBackends = backendList
        self.backend = None
        self.findLatestMatchingName = None
        self.findLatestMatchingRequire = None
        self.getAllPackages = None
        self.getAllProvides = None

        # Loading the appropriate backend
        # if requested
        if setupBackend:
            if checkForUpdates:
                self.setupBackendFromRemote()
            else:
                self.setupBackendFromLocal()
        else:
            log.warning("Backend NOT setup as requested")

    def setupBackendFromRemote(self):
        """ Checks which back-end should be used, and update DB files. """

        # first get repository metadata with the list of available files
        (data, remotemd) = self._getRemoteMetadata()

        localmd = self._getLocalMetadata()
        backend = None
        for ba in self.availableBackends:
            log.info("REMOTE Checking availability of interface: %s"
                     % ba.__name__)
            try:
                try:
                    (checksum, timestamp, filename) = remotemd[
                                                        ba.yumDataType()]
                except KeyError:
                    log.warning("Remote repository does not provide %s DB"
                                % ba.__name__)
                    continue

                # A priori we have a match (KeyError otherwise)
                backend = ba(self)
                self.backend = backend
                ltimestamp = None
                try:
                    (lchecksum, ltimestamp, lfilename) = localmd[
                                                            ba.yumDataType()]
                except:
                    pass
                    # Doesn't matter, we download DB in this case

                if (not self.backend.hasDB() or
                   ltimestamp is None or
                   timestamp > ltimestamp):
                    # We need to update the DB in this case
                    furl = self.repourl + "/" + filename
                    log.info("Updating the RPM database for % s" % ba.__name__)
                    self.backend.getLatestDB(furl)
                    # Now saving the metadata to the repomd file
                    with open(self.localRepomdXml, 'wb') as ftmp:
                        ftmp.write(data)

                # Loading data necessary for the backend
                self.backend.load()

            except Exception as e:  # IGNORE:W0702
                backend = None
                log.error(e)
                log.warning("Error initializing %s backend - Trying next"
                            % ba.__name__)
            # Stop at first one found
            if backend is not None:
                break

        # Now loading the data
        if backend is None:
            raise Exception("No valid backend found")
        else:
            log.info("Repository %s - Chosen backend: %s"
                     % (self.name, backend.mName))
            # Now initializing the methods delegated to the backend
            self.setBackend()

    def setupBackendFromLocal(self):
        """ Checks which back-end should be used, using local cache. """

        localmd = self._getLocalMetadata()
        backend = None
        for ba in self.availableBackends:
            log.info("LOCAL Checking availability of interface: %s"
                     % ba.__name__)
            try:
                try:
                    (checksum, timestamp, filename) = localmd[ba.yumDataType()]
                except KeyError:
                    log.warning("Repository %s - Local repository does not "
                                "provide %s DB - Trying next"
                                % (self.name, ba.__name__))
                    continue

                # A priori we have a match (KeyError otherwise)
                backend = ba(self)
                self.backend = backend
                # Loading data necessary for the backend
                self.backend.load()

            except Exception as e:  # IGNORE:W0703
                backend = None
                log.warning("Repository %s - Error: %s" % (self.name, str(e)))
                log.warning("Repository %s - Error initializing %s backend "
                            "Trying next" % (self.name, ba.__name__))
            # Stop at first one found
            if backend is not None:
                break

        # Now loading the data
        if backend is None:
            raise Exception("No valid backend found")
        else:
            log.info("Repository %s - Chosen backend: %s"
                     % (self.name, backend.mName))
            # Now initializing the methods delegated to the backend
            self.setBackend()

    def setBackend(self, backend=None):
        """
        Sets the backend and makes sure the methods are properly delegated

        :param backend: the back end to be set-up
        """
        # Checing if teh backend needs setting
        if backend is not None:
            self.backend = backend

        # Setting up delegation
        self.findLatestMatchingName = self.backend.findLatestMatchingName
        self.findLatestMatchingRequire = self.backend.findLatestMatchingRequire
        self.getAllPackages = self.backend.getAllPackages
        self.getAllProvides = self.backend.getAllProvides

    # Tools to get the metadata and check whether it is up to date
    ###########################################################################
    def _getRemoteMetadata(self):
        """ Gets the remote repomd file """
        log.info("NET - Getting remote metadata for %s" % self.name)
        try:
            import urllib2
        except:
            # Python 3 workaround
            from urllib import request as urllib2
        ret = None
        response = urllib2.urlopen(self.repomdurl)
        data = response.read()
        if data is not None:
            ret = self._checkRepoMD(data)
        response.close()
        return (data, ret)

    def _getLocalMetadata(self):
        """ Gets the remote repomd file """
        log.debug("LOC - Getting local metadata for %s" % self.name)
        ret = None
        if os.path.exists(self.localRepomdXml):
            with open(self.localRepomdXml, 'r') as ftmp:
                data = ftmp.read()
                if data is not None:
                    ret = self._checkRepoMD(data)
        return ret

    @classmethod
    def _checkRepoMD(cls, repomdxml):
        """ Method to parse the Repository metadata XML file

        :param repomdxml: The repository xml database

        :returns: The database timestamps
        """
        dom = xml.dom.minidom.parseString(repomdxml)
        dbTimestamps = {}
        for nd in dom.documentElement.childNodes:
            if (nd.nodeType == xml.dom.Node.ELEMENT_NODE and
               nd.tagName == "data"):
                checksum = None
                timestamp = None
                location = None
                fileType = nd.getAttribute("type")
                for nc in nd.childNodes:
                    if (nc.nodeType == xml.dom.Node.ELEMENT_NODE and
                       nc.tagName == "checksum"):
                        checksum = RepositoryXMLBackend.getNodeText(nc)
                    if (nc.nodeType == xml.dom.Node.ELEMENT_NODE and
                       nc.tagName == "timestamp"):
                        timestamp = RepositoryXMLBackend.getNodeText(nc)
                    if (nc.nodeType == xml.dom.Node.ELEMENT_NODE and
                       nc.tagName == "location"):
                        location = nc.getAttribute("href")
                dbTimestamps[fileType] = (checksum, timestamp, location)
        return dbTimestamps


#
# Class handling the YUM primary.xml..gz files
#
###########################################################################
class RepositoryXMLBackend(object):
    """
    Class interfacing with the XML interface provided by Yum repositories

    :param repository: The repository whose backend is represented by the
                       object
    """

    def __init__(self, repository):
        self.mName = "RepositoryXMLBackend"
        self.mPackages = {}
        self.mProvides = {}
        self.mPackageCount = 0
        self.mDBName = "primary.xml.gz"
        self.mPrimary = os.path.join(repository.cachedir, self.mDBName)
        self.mRepository = repository

    #
    # Public Interface for the XML Backend
    ###########################################################################
    def getLatestDB(self, url):
        """ Dowload the DB from the server

        :param url: the url of the xml database
        """
        log.info("NET - Downloading latest version of XML DB")
        urllib.urlretrieve(url, self.mPrimary)

    def hasDB(self):
        """ Check whether the DB is there """
        return os.path.exists(self.mPrimary)

    def load(self):
        """ Actually load the data """
        self._loadYumMetadataFile(self.mPrimary)

    @classmethod
    def yumDataType(cls):
        """ Returns the ID for the data type as used in the repomd.xml file

        :returns: Always returns primary
        """
        return "primary"

    def findLatestMatchingName(self, name, version, release=None):
        """
        Utility function to locate a package by name, returns the latest
        available version

        :param name: The name of the package
        :param version: The version of the package
        :param release: The release of the package

        :returns: The requested package
        """
        package = None
        try:
            availableVersions = self.mPackages[name]
            if availableVersions is not None:
                if ((version is None or len(version) == 0) and
                   len(availableVersions) > 0):
                    # returning latest
                    package = sorted(availableVersions)[-1]
                else:
                    # Trying to match the requirements vs what is available
                    req = Requires(name, version, release, flags="EQ")
                    matching = [p for p in availableVersions
                                if req.provideMatches(p)]
                    if len(matching) > 0:
                        package = sorted(matching)[-1]

        except KeyError:
            log.debug("Could not find package %s" % (name))

        # Checking whether we actually found something
        if package is None:
            log.debug("Could not find package %s.%s-%s"
                      % (name, version, release))
        return package

    def findLatestMatchingRequire(self, requirement):
        """
        Utility function to locate a package providing a given functionality

        :param requirement: the requirement that is looked up

        :returns: the package that provides the requirement
        """

        log.debug("Looking for match for %s" % requirement)
        if requirement is None:
            raise Exception(
                "_findPackageMatchingRequire passed Null requirement")

        package = None
        try:
            availableVersions = self.mProvides[requirement.name]
            if availableVersions is not None:
                if ((requirement.version is None or
                   len(requirement.version) == 0) and
                   len(availableVersions) > 0):
                    availableVersions.sort()
                    # If no version is specified we just return the latest one
                    log.debug("Found %d versions - returning latest: %s"
                              % (len(availableVersions),
                                 availableVersions[-1]))
                    package = availableVersions[-1].package
                else:
                    # Trying to match the requirements and what is available
                    matching = [p for p in availableVersions
                                if requirement.provideMatches(p)]
                    if len(matching) > 0:
                        matching.sort()
                        log.debug("Found %d version matching - returning "
                                  "latest: %s" % (len(matching), matching[-1]))
                        package = matching[-1].package
        except KeyError:
            log.debug("Could not find package providing %s-%s"
                      % (requirement.name, requirement.version))

        if package is None:
            log.debug("Could not find package providing %s-%s"
                      % (requirement.name, requirement.version))
        return package

    def getAllPackages(self, nameMatch=None):
        """ Yields the list of all packages known by the repository

        :param nameMatch: The name regex that is being looked up

        :returns: Yields the list of packages matching the name regex
        """
        for pak_list_k in self.mPackages.keys():
            if nameMatch is None or (nameMatch is not None and
                                     re.match(nameMatch,
                                              pak_list_k) is not None):
                for pa in self.mPackages[pak_list_k]:
                    yield pa

    def getAllProvides(self, nameMatch=None):
        """ Yields the list of all requires known by the repository

        :param nameMatch: The name regex that is being looked up

        :returns: Yields the list of requirements matching the name regex
        """
        for prov_list_k in self.mProvides.keys():
            if nameMatch is None or (nameMatch is not None and
                                     re.match(nameMatch,
                                              prov_list_k) is not None):
                for pa in self.mProvides[prov_list_k]:
                    yield pa

    #
    # Methods for XML parsing and data loading
    ###########################################################################
    @classmethod
    def _fromYumXML(cls, packageNode):  # IGNORE:R0912
        """ Method that instantiates a correct package instance, based on
        the YUM Metadata XML structure

        :param packageNode: the xml node representing the package metadata

        :returns: the package instance
        """

        # First checking the node passed, just in case
        if (packageNode.nodeType == xml.dom.Node.ELEMENT_NODE and
           packageNode.tagName != "package"):
            raise Exception("Trying to create Package from wrong node" +
                            str(packageNode))

        lp = Package()
        for cn in packageNode.childNodes:
            if cn.nodeType != xml.dom.Node.ELEMENT_NODE:
                continue
            if cn.tagName == "name":
                lp.name = RepositoryXMLBackend.getNodeText(cn)
            elif cn.tagName == "arch":
                lp.arch = RepositoryXMLBackend.getNodeText(cn)
            elif cn.tagName == "version":
                lp.version = cn.getAttribute("ver")
                lp.release = cn.getAttribute("rel")
                lp.epoch = cn.getAttribute("epoch")
            elif cn.tagName == "location":
                lp.location = cn.getAttribute("href")
            elif cn.tagName == "format":
                for fnode in cn.childNodes:
                    if fnode.nodeType != xml.dom.Node.ELEMENT_NODE:
                        continue
                    if fnode.tagName == "rpm:group":
                        lp.group = RepositoryXMLBackend.getNodeText(fnode)
                    if fnode.tagName == "rpm:provides":
                        for dep in fnode.childNodes:
                            if dep.nodeType != xml.dom.Node.ELEMENT_NODE:
                                continue
                            depname = dep.getAttribute("name")
                            depver = dep.getAttribute("ver")
                            deprel = dep.getAttribute("rel")
                            depepoch = dep.getAttribute("epoch")
                            depflags = dep.getAttribute("flags")
                            lp.provides.append(Provides(depname,
                                                        depver,
                                                        deprel,
                                                        depepoch,
                                                        depflags,
                                                        lp))
                    if fnode.tagName == "rpm:requires":
                        for dep in fnode.childNodes:
                            if dep.nodeType != xml.dom.Node.ELEMENT_NODE:
                                continue
                            depname = dep.getAttribute("name")
                            depver = dep.getAttribute("ver")
                            deprel = dep.getAttribute("rel")
                            depepoch = dep.getAttribute("epoch")
                            depflags = dep.getAttribute("flags")
                            deppre = dep.getAttribute("pre")
                            lp.requires.append(Requires(depname,
                                                        depver,
                                                        deprel,
                                                        depepoch,
                                                        depflags,
                                                        deppre))

        # Set the "standard version field, used for comparison
        lp.standardVersion = VersionedObject.getStandardVersion(lp.version)
        # Now return the object back...
        return lp

    @classmethod
    def getNodeText(cls, node):
        """ Gets the value of the first child text node
        :param node: The xml node:

        :returns: the data of the first child text node
        """
        for tn in node.childNodes:
            if tn.nodeType == xml.dom.Node.TEXT_NODE:
                return tn.data

    def _loadYumMetadataFile(self, filename):
        """ Loads the yum XML package list

        :pram filename: The xml filename to be loaded
        """
        fi = gzip.open(filename, 'rb')
        try:
            log.debug("Starting the parsing of the Metadata XML file")
            dom = xml.dom.minidom.parse(fi)
            log.debug("Parsing of the Metadata XML file done")
            self._loadYumMetadataDOM(dom)
        except Exception as e:
            log.error("Error while parsing file %s: %s" % (filename, str(e)))
            raise e
        fi.close()

    def _loadYumMetadataDOM(self, dom):
        """ Loads the yum XML package list

        :param dom: The dom that needs to be loaded
        """
        # Finding all packages and adding then to the repository
        log.debug("Starting to iterate though Metadata DOM")
        for nd in dom.documentElement.childNodes:
            if nd.nodeType == xml.dom.Node.ELEMENT_NODE:
                # Generating the package object from the XML
                pa = RepositoryXMLBackend._fromYumXML(nd)
                pa.setRepository(self.mRepository)
                # Adding the package to the repository
                self._addPackage(pa)
                self._addAllProvides(pa)
                self.mPackageCount += 1
                log.debug("Added %s package <%s><%s><%s>"
                          % (pa.group, pa.name, pa.version, pa.release))

                # Checking the Package type...
                if nd.getAttribute("type") != "rpm":
                    log.warning("Package type for %s is %s not RPM"
                                % (pa.name, nd.getAttribute("type")))

        log.debug("Finished to iterate though Metadata DOM")

    def _addPackage(self, package):
        """ Adds a package to the repository global list

        :param package: the package that will be added to the
                        global list
        """
        try:
            allversions = self.mPackages[package.name]
        except KeyError:
            allversions = []
        allversions.append(package)
        self.mPackages[package.name] = allversions

    def _addAllProvides(self, package):
        """ Adds a package to the map with the list of provides

        :param package: the package whoes providers will be added
        """
        for prov in package.provides:
            if prov.name not in IGNORED_PACKAGES:
                try:
                    allprovides = self.mProvides[prov.name]
                except KeyError:
                    allprovides = []
                allprovides.append(prov)
                self.mProvides[prov.name] = allprovides


#
# Class handling the YUM primary.sqlite.bz2 files
#
###########################################################################
class RepositorySQLiteBackend(object):
    """
    Class interfacing with the SQLite interface provided by Yum repositories

    :param repository: The repository whose backend is represented by the
                       object
    """

    def __init__(self, repository):
        self.mName = "RepositorySQLiteBackend"
        self.mDBName = "primary.sqlite.bz2"
        self.mDBNameUncompressed = "primary.sqlite"
        self.mPrimary = os.path.join(repository.cachedir, self.mDBName)
        self.mPrimaryUncompressed = os.path.join(repository.cachedir,
                                                 self.mDBNameUncompressed)
        self.mRepository = repository
        self.mDBConnection = None

    #
    # Public interface
    ###########################################################################
    @classmethod
    def yumDataType(cls):
        """ Returns the ID for the data type as used in the repomd.xml file

        :returns: Always returns primary_db
        """
        return "primary_db"

    def hasDB(self):
        """ Check whether the DB is there """
        return os.path.exists(self.mPrimary)

    def getLatestDB(self, url):
        """ Download the latest DB from the server

        :param url: the url of the xml database
        """
        log.debug("NET - Downloading latest version of SQLite DB")
        urllib.urlretrieve(url, self.mPrimary)

        log.debug("Decompressing latest version of SQLite DB")
        if os.path.exists(self.mPrimaryUncompressed):
            os.unlink(self.mPrimaryUncompressed)
        self._decompressDB()

    def load(self):
        """ Actually load the data """
        # Checking if we need to uncompress the DB again
        if not os.path.exists(self.mPrimaryUncompressed):
            self._decompressDB()

        # Import the the package and open DB connection
        # try:
        import sqlite3 as sql

        self.mDBConnection = sql.connect(self.mPrimaryUncompressed)

    def findLatestMatchingName(self, name, version, release=None):
        """
        Utility function to locate a package by name, returns the latest
        available version

        :param name: The name of the package
        :param version: The version of the package
        :param release: The release of the package

        :returns: The requested package
        """
        package = None
        found = self._loadPackagesByName(name, version)
        if len(found) > 0:
            req = Requires(name, version, release)
            matching = [p for p in found if req.provideMatches(p)]
            if len(matching) > 0:
                package = matching[-1]
        return package

    def getAllProvides(self, nameMatch=None):
        """
        Yields the list of all provides known by the repository

        :param nameMatch: The name regex that is being looked up

        :returns: Yields the list of requirements matching the name regex
        """
        cursor = self.mDBConnection.cursor()
        # request to find the entry in the package table
        sq = """select name, flags, epoch, version, release, pkgKey
             from provides """
        res = cursor.execute(sq)
        # Getting the results
        for (name, flags, epoch, version, release, pkgKey) in res:
            # Creating the package object
            if nameMatch is None or (nameMatch is not None and
                                     re.match(nameMatch, name) is not None):
                p = Provides(name, version, release, epoch, flags)
                # Now yield this
                yield(p)

        # Free resources
        cursor.close()

    def getAllPackages(self, nameMatch=None):
        """ Yields the list of all packages known by the repository

        :param nameMatch: The name regex that is being looked up

        :returns: Yields the list of packages matching the name regex
        """
        cursor = self.mDBConnection.cursor()
        # request to find the entry in the package table
        sq = """select pkgkey, name, version, release, epoch, rpm_group, arch, location_href
             from packages """
        res = cursor.execute(sq)

        # Getting the results
        for (pkgkey, pname, version, release,
             epoch, rpm_group, arch, location_href) in res:
            # Creating the package object
            if nameMatch is None or (nameMatch is not None and
                                     re.match(nameMatch, pname) is not None):
                pa = Package(pname, version, release,
                             epoch, None, rpm_group, arch, location_href)
                # Now getting the provides and requires
                pa.requires = self._loadRequiresByKey(pkgkey)
                pa.provides = self._loadProvidesByKey(pkgkey, pa)
                pa.setRepository(self.mRepository)
                # Now yield this
                yield(pa)

        # Free resources
        cursor.close()

    def findLatestMatchingRequire(self, requirement):
        """
        Utility function to locate a package providing a given functionality

        :param requirement: the requirement that is looked up

        :returns: the package that provides the requirement
        """

        log.debug("Looking for match for %s" % requirement)
        if requirement is None:
            raise Exception("_findPackageMatchingRequire "
                            "passed Null requirement")
        package = None

        # List of all provides with the same name
        # (we do version comparison in python)
        allprovides = self._findProvidesByName(requirement.name)
        matching = [pr for pr in allprovides
                    if requirement.provideMatches(pr)]

        # Now lookup the matching package
        if len(matching) > 0:
            prov = sorted(matching)[-1]
            allpackages = self._loadPackageProviding(prov)
            if not allpackages and prov.name not in IGNORED_PACKAGES:
                raise Exception("Could not find package providing: %s"
                                % str(prov))
            if allpackages:
                package = sorted(allpackages)[-1]
        return package

    #
    # Utility methods
    ###########################################################################
    def _loadProvidesByKey(self, pkgkey, package):
        """ Loads provide list given a package key
        :param pkgkey: the key of the package
        :param package: the package looked into

        :returns: the list of providers
        """
        allprovides = []
        cursorSub = self.mDBConnection.cursor()
        sqprov = "select name, flags, epoch, version, release from " \
                 "provides where pkgkey=?"
        resprov = cursorSub.execute(sqprov, [pkgkey])
        for (name, flags, epoch, version, release) in resprov:
            prov = Provides(name, version, release, epoch, flags, package)
            allprovides.append(prov)
        cursorSub.close()
        return allprovides

    def _loadRequiresByKey(self, pkgkey):
        """ Loads requires list given a package key

        :param pkgkey: the key of the package

        :returns: the list of requires
        """
        allrequires = []
        cursorSub = self.mDBConnection.cursor()
        sqlreq = "select name, flags, epoch, version, release, pre from " \
                 "requires where pkgkey=?"
        respreq = cursorSub.execute(sqlreq, [pkgkey])
        for (name, flags, epoch, version, release, pre) in respreq:
            if flags is None:
                flags = "EQ"
            req = Requires(name, version, release, epoch, flags, pre)
            allrequires.append(req)
        cursorSub.close()
        return allrequires

    def _findProvidesByName(self, name):
        """ Find all provides with a given name

        :param name: the name of the provider

        :returns: the list of the providers
        """
        allprovides = []
        cursorSub = self.mDBConnection.cursor()
        sqprov = "select pkgkey, name, flags, epoch, version, release from " \
                 "provides where name=?"
        resprov = cursorSub.execute(sqprov, [name])
        for (pkgkey, name, flags, epoch, version, release) in resprov:
            prov = Provides(name, version, release, epoch, flags, None)
            allprovides.append(prov)
        cursorSub.close()
        return allprovides

    def _loadPackagesByName(self, name, version=None):
        """ Lookup packages with a given name

        :param name: the name of the package
        :param version: the version of the package

        :returns: the list of package matching the name and
                  version
        """
        allpackages = []
        cursor = self.mDBConnection.cursor()
        # request to find the entry in the package table
        sq = """select pkgkey, name, version, release, epoch, rpm_group, arch, location_href
             from packages where name = ? """
        if version is not None:
            sq += " and version = ? "
            res = cursor.execute(sq, [name, version])
        else:
            res = cursor.execute(sq, [name])

        # Getting the results
        for (pkgkey, pname, version, release,
             epoch, rpm_group, arch, location_href) in res:
            # Creating the package object
            pa = Package(pname, version, release,
                         epoch, None, rpm_group, arch, location_href)
            pa.setRepository(self.mRepository)

            # Now getting the provides and requires
            pa.requires = self._loadRequiresByKey(pkgkey)
            pa.provides = self._loadProvidesByKey(pkgkey, pa)
            # and append to thelist
            allpackages.append(pa)
        cursor.close()
        return allpackages

    def _loadPackageProviding(self, provide):
        """ Lookup packages with a given name

        :param provide: the provide object

        :returns: the list of the packages
        """
        allpackages = []
        cursor = self.mDBConnection.cursor()
        # request to find the entry in the package table
        sq = """select p.pkgkey, p.name, p.version, p.release, p.epoch,
             p.rpm_group, p.arch, p.location_href
             from packages p, provides r
             where p.pkgkey = r.pkgkey
             and r.name = ?
             and r.version = ? """

        if provide.release is not None:
            sq += " and r.release = ? "
            res = cursor.execute(sq, [provide.name,
                                      provide.version,
                                      provide.release])
        else:
            res = cursor.execute(sq, [provide.name, provide.version])

        # Getting the results
        for (pkgkey, pname, version, release,
             epoch, rpm_group, arch, location_href) in res:
            # Creating the package object
            pa = Package(pname, version, release,
                         epoch, None, rpm_group, arch, location_href)
            pa.setRepository(self.mRepository)

            # Now getting the provides and requires
            pa.requires = self._loadRequiresByKey(pkgkey)
            pa.provides = self._loadProvidesByKey(pkgkey, pa)
            # and append to the list
            allpackages.append(pa)
        cursor.close()
        return allpackages

    def _decompressDB(self):
        """ Uncompress DB file to be able to open it with SQLLite """
        import bz2
        import shutil
        primaryBz2 = bz2.BZ2File(self.mPrimary, 'rb')
        primaryUncomp = open(self.mPrimaryUncompressed, 'wb')
        shutil.copyfileobj(primaryBz2, primaryUncomp)
        primaryBz2.close()
        primaryUncomp.close()


#
# LbYumClient: CLass that parses the Yum metadata and manages the repositories
#
###############################################################################
class LbYumClient(object):
    """ Client class to be invoked to to query RPMs

    :param localConfigRoot: The local configuration root folder
    :param repourls: The list of of the repository urls
    :param checkForUpdates: Flag used to update the back end after setup based
                            on the remote configuration
    """
    def __init__(self, localConfigRoot, repourls, checkForUpdates=True):
        """ Constructor for the client """
        # Basic initializations
        self.repourls = repourls
        self.lbyumcache = os.path.join(localConfigRoot, SVAR, SCACHE, SLBYUM)
        self.configured = False
        self.repositories = {}
        self.repourls = {}

        # At this point we have the repo names and URLs in self.repourls
        # we know connect to them to get the best method to get the appropriate
        # files
        self._initializeRepositories(repourls, checkForUpdates,
                                     [RepositorySQLiteBackend,
                                      RepositoryXMLBackend])

    def addRepository(self, repository):
        """ Adds a repository manually, useful for testing

        :param repository: the repository object to be added
        """
        self.repositories[repository.name] = repository
        self.repourls[repository.name] = repository.repourl

    #
    # Public methods
    ###########################################################################
    def findLatestMatchingName(self, name, version=None, release=None):
        """ Main method for locating packages by RPM name

        :param name: The name of the package
        :param version: The version of the package
        :param release: The release of the package

        :returns: The requested package
        """
        allfound = []
        package = None

        # Looking for matches in all repos
        for rep in self.repositories.values():
            log.debug("Searching RPM %s/%s/%s in %s"
                      % (name, version, release, rep.name))
            res = rep.findLatestMatchingName(name, version, release)
            if res is not None:
                allfound.append(res)

        # Sorting to get latest one
        allfound.sort()
        if len(allfound) > 0:
            package = allfound[-1]

        return package

    def listPackages(self, nameRegexp=None, versionRegexp=None,
                     releaseRegexp=None):
        """ List packages available

        :param nameRegexp: Regex for the name of the package
        :param versionRegexp: Regex for the version of the package
        :param releaseRegexp: Regex for the release of the package

        :returns: the list of packages
        """
        # Looking for matches in all repos
        for rep in self.repositories.values():
            for pa in rep.getAllPackages():
                namematch = True
                versionmatch = True
                releasematch = True
                if nameRegexp is not None and re.search(nameRegexp,
                                                        pa.name) is None:
                    namematch = False
                if versionRegexp is not None and re.search(versionRegexp,
                                                           pa.name) is None:
                    versionmatch = False
                if releaseRegexp is not None and re.search(releaseRegexp,
                                                           pa.name) is None:
                    releasematch = False
                if namematch and versionmatch and releasematch:
                    yield pa

    def listProvides(self, nameRegexp=None, versionRegexp=None,
                     releaseRegexp=None):
        """ List provides available

        :param nameRegexp: Regex for the name of the package
        :param versionRegexp: Regex for the version of the package
        :param releaseRegexp: Regex for the release of the package

        :returns: the list of provides
        """
        # Looking for matches in all repos
        for rep in self.repositories.values():
            for pa in rep.getAllProvides():
                namematch = True
                versionmatch = True
                releasematch = True
                if nameRegexp is not None and re.search(nameRegexp,
                                                        pa.name) is None:
                    namematch = False
                if versionRegexp is not None and re.search(versionRegexp,
                                                           pa.name) is None:
                    versionmatch = False
                if releaseRegexp is not None and re.search(releaseRegexp,
                                                           pa.name) is None:
                    releasematch = False
                if namematch and versionmatch and releasematch:
                    yield pa

    def findLatestMatchingRequire(self, requirement, force_local=False):
        """ Main method for locating packages by RPM name

        :param requirement: the requirement that is looked up

        :returns: the package that provides the requirement
        """
        allmatching = []
        matchingPackage = None

        # Looking for matches in all repos
        for rep in self.repositories.values():
            ma = rep.findLatestMatchingRequire(requirement)
            if ma is not None:
                if 'local' in rep.name and force_local:
                    return ma
                allmatching.append(ma)

        # Sorting to get latest one
        allmatching.sort()
        if len(allmatching) > 0:
            matchingPackage = allmatching[-1]

        return matchingPackage

    #
    # Dependency management
    ###########################################################################
    def getAllPackagesRequired(self, package):
        """
        Get all packages needed for installation (including the package itself)

        :param package: The packages whose requires need to be looked up

        :returns: the list of packages needed for installation
        """
        deps = self.getPackageDependencies(package)
        deps.append(package)
        return deps

    def getPackageDependencies(self, package):
        """
        Get all dependencies for the package (excluding the package itself)

        :param package: The packages whose dependencies need to be looked up

        :returns: the list of packages needed for installation
        """
        log.info("Checking dependencies for %s.%s-%s" % (package.name,
                                                         package.version,
                                                         package.release))
        return list(self._getpackageDeps(package, set()))

    def _getpackageDeps(self, package, alreadyprocessed):
        """ Internal method to recurse on dependencies """
        # Now iterating on all requires to find the matching requirement
        alreadyprocessed.add(package)
        requiredlist = set()
        for req in package.requires:
            (reqPackage, reqVersion, reqRelease) = (req.name,
                                                    req.version,
                                                    req.release)
            if reqPackage not in IGNORED_PACKAGES:
                log.debug("Processing deps %s.%s-%s" % (reqPackage,
                                                        reqVersion,
                                                        reqRelease))
                pa = self.findLatestMatchingRequire(req)

                # Check for circular dependencies using the set passed
                if pa in alreadyprocessed:
                    # log.warning("Cyclic dependency in repository with"
                    #              "package: %s" % pa.name)
                    continue

                if pa is not None:
                    requiredlist.add(pa)
                    # Then adding the children...
                    for subreq in self._getpackageDeps(pa, alreadyprocessed):
                        if subreq not in requiredlist:
                            requiredlist.add(subreq)
                else:
                    if reqPackage not in IGNORED_PACKAGES:
                        log.error("Package %s.%s-%s not found" % (reqPackage,
                                                                  reqVersion,
                                                                  reqRelease))
                        # raise Exception("Package %s.%s-%s not found"
                        #   % (reqPackage, reqVersion, reqRelease))
        return requiredlist

    def _initializeRepositories(self, repourls, checkForUpdates,
                                knownBackends):
        """ Initilize the repositories given their URLS """

        self.repourls = repourls
        # At this point self.repourls is a map containing the
        # list of repositories and their URLs
        # Iterate on them to setup the repositories
        for repo in self.repourls.keys():
            # Getting the main parameters for the repository:
            # URL and cache directory
            repourl = self.repourls[repo]
            repocachedir = os.path.join(self.lbyumcache, repo)
            if not os.path.exists(repocachedir):
                os.makedirs(repocachedir)

            try:
                rep = Repository(repo, repourl, repocachedir,
                                 knownBackends, True, checkForUpdates)
                log.debug("Repository %s created" % repo)
                # Now adding the repository to the map
                self.repositories[repo] = rep
            except Exception as e:  # IGNORE:W0703
                log.error("ERROR - Banning repository %s: %s" % (repo, e))

if __name__ == '__main__':
    FORMAT = '%(asctime)-15s %(message)s'
    logging.basicConfig(format=FORMAT)
    log.setLevel(logging.DEBUG)
