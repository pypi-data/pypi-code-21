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
Installer for the for LHCb Software.
All it needs is the name of a local directory to use to setup the install area
and the yum repository configuration.

:author: Ben Couturier, Stefan-Gabriel Chitic
'''
import logging
import os
import sys
import traceback
from os.path import abspath
import shutil
import stat

from lbinstall.Model import IGNORED_PACKAGES
from lbinstall.Model import VersionedObject
from lbinstall.InstallAreaManager import InstallArea
from lbinstall.PackageManager import PackageManager
from lbinstall.extra.RPMExtractor import sanitycheckrpmfile
from lbinstall.extra.ThreadPoolManager import ThreadPool
from lbinstall.Graph import Graph
from lbinstall.DependencyManager import IGNORED_PACKAGES
from lbinstall.Model import Requires


# Little util to find a file in a directory tree
def findFileInDir(basename, dirname):
    """ Look for a file with a given basename in a
    directory struture.
    :returns: the first file found... """
    for root, _, files in os.walk(dirname, followlinks=True):
        if basename in files:
            return abspath(os.path.join(root, basename))
    return None


class Installer(object):
    '''
    LHCb Software installer.
    This class can be used to query the remote YUM database,
    and to install packages on disk.
    It create the InstallArea files needed for the installation.
    You can create it either:

    * Passing the siteroot of the Installation, in which case the
      repositories are setup to the default LHCb ones

    * Passing a full InstallAreaConfig as the named parameter config,
      in which case all customizations are possible (by specifying the
      configType parameter). A class like LHCbConfig.py must be created
      in that case.

    :param siteroot: The folder where Installer will install software
    :param config: The configuration used by Installer
    :param localRPMcache: A local folder to used instead of downloading the
                          rpms
    :param disableYumCheck: Disables the YUM check
    :param chained_db_list: A list sqllite db location to be used in
                            cascade as local db.
    :param nodeps: The installer will ignore the dependencies of the
                   packages to install
    :param tmp_dir: A custom directory to be used a tmp instead of
                    <siteroot>/tmp/
    :param pool_size: The pool size of the download thread pool
    :param stric: Flag used to stop an action if a dependency is not satisfied
    '''

    def __init__(self, siteroot, config=None,
                 localRPMcache=None, disableYumCheck=False,
                 chained_db_list=[], nodeps=False,
                 tmp_dir=None, pool_size=5,
                 strict=True):
        '''Class to install a set of packages to a specific area
        '''
        self.log = logging.getLogger(__name__)
        self._siteroot = os.path.abspath(siteroot)
        self._lcgDir = os.path.join(self._siteroot, "lcg")
        if config is None:
            from lbinstall.LHCbConfig import Config
            config = Config()
        self._config = config
        self._nodeps = nodeps
        self.pool_size = pool_size
        self.threadPool = ThreadPool(self.pool_size)
        # Creating the install area and getting the relevant info
        self.__installArea = InstallArea(self._config, self._siteroot,
                                         tmp_dir=tmp_dir)
        self._lbYumClient = self.__installArea \
                                .createYumClient(not disableYumCheck)
        self._chainedDBManger = self.__installArea.createChainedDBManager()
        self._localDB = self.__installArea.createDBManager(
            self._chainedDBManger)
        self._relocateMap = self.__installArea.getRelocateMap()
        self._tmpdir = self.__installArea.getTmpDir()
        self._localRPMcache = []
        if localRPMcache is not None:
            self._localRPMcache = localRPMcache
        for chained_db in chained_db_list:
            self._chainedDBManger.addDb(chained_db)
        self.strict = strict

    # Various utilities to query the yum database
    # ############################################################################

    def getPackageListFromTuples(self, tuplesList, local=False,
                                 exact_search=False):
        """Transforms a list of tuples to a list of packages

        :param tuplesList: A list of tuples (name, version, release) to be
                           transformed into list of packages
        :param local: If true, the search will be done only on local db
                      instead of the remote repository.
        :param exact_search: If true, the search will be look exactly for the
                             given name. Otherwhise, it will look packages with
                             names like name%.

        :returns: a list of database packages
        """
        packagelist = []
        for rpmname, version, release in tuplesList:
            if local:
                packages = self.localFindPackages(rpmname,
                                                  version,
                                                  release,
                                                  exact_search=exact_search)
                packagelist.extend(packages)
            else:
                packagelist.extend(self.remoteFindPackage(rpmname,
                                                          version,
                                                          release))
        return packagelist

    def remoteListProvides(self, nameRegexp):
        """ List provides matching in the remote repo

        :param nameRegexp: Regex for the name of the package

        :returns: a list of providers
        """
        return self._lbYumClient.listProvides(nameRegexp)

    def remoteFindPackage(self, name, version=None, release=None):
        """
        Finds the remote package (from YUM repo) based on name, version
        and release

        :param name: the name of the package
        :param version: (optional) the version of the package
        :param release: (optional) the release of the package

        :returns: the remote package
        """
        req = Requires(name, version, release, None, "EQ", None)
        pack = self._lbYumClient.findLatestMatchingRequire(req)

        res = [pack] if pack is not None else []
        return res

    def localFindPackages(self, name, version=None, release=None,
                          exact_search=False):
        """
        Finds the local installed package based on name, version and
        release

        :param name: the name of the package
        :param version: (optional) the version of the package
        :param release: (optional) the release of the package
        :param exact_search: If true, the search will be look exactly for the
                             given name. Otherwhise, it will look packages with
                             names like name%.

        :returns: the list of local packages
        """
        return self._localDB.getPackages(match=name,
                                         vermatch=version,
                                         relmatch=release,
                                         local_only=True,
                                         exact_search=exact_search)

    def listDependencies(self, package):
        ''' Return the list of dependencies of a given package

        :param package: The package of whose dependencies will be returned

        :returns: the list of dependencies
        '''
        return [rpm[0] for rpm, _ in
                self._getPackagesToInstall(package, ignoreInstalled=True)]

    def remoteListPackages(self, nameRegexp=None,
                           versionRegexp=None,
                           releaseRegexp=None):
        """
        List the remote packages with whose name, version or release are
        similar to the params.

        :param nameRegexp: Regex for the name of the package
        :param versionRegexp: Regex for the version of the package
        :param releaseRegexp: Regex for the release of the package

        :returns: the list of remote packages
        """
        packages = self._lbYumClient.listPackages(nameRegexp,
                                                  versionRegexp,
                                                  releaseRegexp)
        return packages

    # Queries to the local DB
    # ############################################################################3
    def localListPackages(self, nameRegexp=None,
                          versionRegexp=None,
                          releaseRegexp=None):
        """
        List the local installed packages with whose name, version or release
        are similar to the params.

        :param nameRegexp: Regex for the name of the package
        :param versionRegexp: Regex for the version of the package
        :param releaseRegexp: Regex for the release of the package

        :returns: the list of local packages
        """
        packages = self._localDB.listPackages(nameRegexp,
                                              versionRegexp,
                                              releaseRegexp)
        return packages

    def displayDependenciesGraph(self, rpms, filename="output",
                                 tree_mode=False):
        """
        Function used to generate dot files for graph representation

        :param rpms: The list of rpms needed in the graph display
        :param filename: the output filename
        :param tree_mode: Flag used to convert the full graph view, to tree
                          mode, where dependencies are display in topological
                          order. E.g If a->b->c->d and a->d, the connection
                          from a->d will be removed since it is already present
                          and during the installation it will be added before c
        """
        packagelist = self.getPackageListFromTuples(rpms)
        install_graph = None
        missing_deps = []
        for p in packagelist:
            install_graph, missing_deps_tmp = self._getPackagesToInstall(
                p, ignoreInstalled=True,
                packagelist=packagelist,
                install_graph=install_graph)
            missing_deps.extend(missing_deps_tmp)
        if len(missing_deps) != 0:
            self.display_missing_deps(missing_deps)
        install_graph.generate_dot(
            tree_mode=tree_mode,
            filename=filename)

    def getPackageListToInstall(self, packagelist,
                                nodeps=False, ignoreInstalled=False,
                                nodeps_update=False,
                                ignoredInstalledList=[]):
        """
        Gets the package list that will be installed including (optional) their
        dependencies

        :param packagelist: the package list of files to install
        :param nodeps: If True, exclude dependencies
        :param ignoreInstalled: Special flag to ignore the installed pkgs. When
                               updating, and the dry_run flag is true, we are
                               not actually removing the files before
                               installing new ones, so the install procedure
                               needs to know that is a dry_run update, in order
                               to avoid an exception such as the files are
                               already installed.

        :returns: the list of packages that will be installed including
                  (optional) their dependencies

        """
        if not packagelist:
            raise Exception("Please specify one or more packages")

        # Looking for the files to install
        rpmtoinstall = list()
        install_graph = None
        missing_deps = []
        if not nodeps and not self._nodeps:
            for p in packagelist:
                install_graph, missing_deps_tmp = self._getPackagesToInstall(
                    p, ignoreInstalled=ignoreInstalled,
                    packagelist=packagelist,
                    extrapackages=set(),
                    install_graph=install_graph,
                    nodeps_update=nodeps_update,
                    ignoredInstalledList=ignoredInstalledList)
                missing_deps.extend(missing_deps_tmp)
            if len(missing_deps) != 0:
                self.display_missing_deps(missing_deps)
            # Get the correct correct order of packages to install
            rpmtoinstall = install_graph.getPackageOrder()
            extrapackages = rpmtoinstall
            rpms_to_install_tmp = []
            for rpm in rpmtoinstall:
                # Checking that one of the packages already
                # scheduled for install do not already provide the package...
                req = Requires(rpm.name, rpm.version, rpm.release, None,
                               "EQ", None)
                tmp = self._findInExtrapackages(req, extrapackages)
                if tmp is not None and not ignoreInstalled and tmp != rpm:
                    self.log.warning("%s already fulfilled by %s, to "
                                     "be installed" % (str(rpm), tmp.name))
                else:
                    rpms_to_install_tmp.append(rpm)
            rpmtoinstall = rpms_to_install_tmp
        else:
            for p in packagelist:
                if not self._localDB.isPackagesInstalled(p):
                    rpmtoinstall.append(p)
                else:
                    self.log.warning("%s already installed" % p.rpmName())

        if ignoreInstalled:
            return rpmtoinstall
        for package in rpmtoinstall:
            local_packages = self.localFindPackages(package.name,
                                                    None,
                                                    None)
            for local_package in local_packages:
                if local_package.name == package.name:
                    cmpVers = VersionedObject.cmpStandardVersion(
                        VersionedObject.getStandardVersion(package.version),
                        VersionedObject.getStandardVersion(
                            local_package.version))

                    if (cmpVers > 0 or
                        (cmpVers == 0 and
                         (package.release > local_package.release))):
                        raise Exception('Please use update! The script '
                                        'needs to install %s-%s-%s, but the '
                                        'package %s-%s-%s is already '
                                        'installed' % (package.name,
                                                       package.version,
                                                       package.release,
                                                       local_package.name,
                                                       local_package.version,
                                                       local_package.release))
                    if (cmpVers < 0 or
                        (cmpVers == 0 and
                         (package.release < local_package.release))):
                        raise Exception('You are downgrading! Please remove '
                                        'first the existing version! The  '
                                        'script needs to install %s-%s-%s, '
                                        'but the  package %s-%s-%s is already '
                                        'installed' % (package.name,
                                                       package.version,
                                                       package.release,
                                                       local_package.name,
                                                       local_package.version,
                                                       local_package.release))
                    if (cmpVers == 0 and (
                            package.release == local_package.release)):
                        raise Exception('Please use reinstall! The script '
                                        'needs to install %s-%s-%s, but the '
                                        'package %s-%s-%s is already '
                                        'installed' % (package.name,
                                                       package.version,
                                                       package.release,
                                                       local_package.name,
                                                       local_package.version,
                                                       local_package.release))

        return rpmtoinstall

    # Verify installed packages:
    def checkPackages(self, packages):
        """
        Checks is a list of packages are correctly installed

        :param packages: list of package to check
        """
        problems = []
        pm = PackageManager(None, self._siteroot, no_rpm_tasks=True)
        for package_raw in packages:
            package = package_raw.rpmName()
            hash_algo_known = None
            filemetadata = self._localDB.loadFMData(package)
            for fname, isdir, md5, size in filemetadata:
                filename = "%s%s" % (self._siteroot, fname)
                self.log.debug("Checking %s of package %s existence" %
                               (filename, package))
                if isdir:
                    if not os.path.isdir(filename):
                        problems.append({
                            'package': package,
                            'filename': filename,
                            'problem': 'Directory does not exists'})
                        self.log.debug("FAILED")
                    else:
                        self.log.debug("SUCCESS")
                else:
                    if md5 == "":
                        if not os.path.islink(filename):
                            problems.append({
                                'package': package,
                                'filename': filename,
                                'problem': 'Link does not exists'})
                            self.log.debug("FAILED")
                        else:
                            self.log.debug("SUCCESS")

                        self.log.debug("Checking %s of package %s file size" %
                                       (filename, package))
                        statres = os.lstat(filename)
                        if size != statres[stat.ST_SIZE]:
                            problems.append({
                                    'package': package,
                                    'filename': filename,
                                    'problem': 'File size is incorrect'})
                            self.log.debug("FAILED")
                        else:
                            self.log.debug("SUCCESS")
                    else:
                        if not os.path.isfile(filename):
                            problems.append({
                                'package': package,
                                'filename': filename,
                                'problem': 'File does not exists'})
                            self.log.debug("FAILED")
                        else:
                            self.log.debug("SUCCESS")

                        self.log.debug("Checking %s of package %s file size" %
                                       (filename, package))
                        statres = os.lstat(filename)
                        if size != statres[stat.ST_SIZE]:
                            problems.append({
                                    'package': package,
                                    'filename': filename,
                                    'problem': 'File size is incorrect'})
                            self.log.debug("FAILED")
                            continue
                        else:
                            self.log.debug("SUCCESS")

                        self.log.debug("Checking %s of package %s chechsum"
                                       % (filename, package))
                        ok = False
                        if hash_algo_known:
                            chechsum = pm.check_sum(filename,
                                                    hash_algo_known)
                            if chechsum == md5:
                                ok = True
                        else:
                            for hash_algo in pm.PGPHASHALGO:
                                if hash_algo is None:
                                    continue
                                chechsum = pm.check_sum(filename,
                                                        hash_algo)
                                if chechsum == md5:
                                    ok = True
                                    hash_algo_known = hash_algo
                                    break
                        if ok:
                            self.log.debug("SUCCESS")
                        else:
                            problems.append({
                                'package': package,
                                'filename': filename,
                                'problem': 'Checksum is incorrect'})
                            self.log.debug("FAILED")
            for problem in problems:
                self.log.error("Check of %s from package %s failed because: %s"
                               % (problem['filename'], problem['package'],
                                  problem['problem']))

    # Installation routines
    # ############################################################################
    def install(self, rpms_to_install, ignoreInstalled=False,
                download_only=False,
                justdb=False, overwrite=False, dry_run=False, nodeps=False,
                nodeps_update=False, ignoredInstalledList=[]):
        """
        Installation procedure, it takes a list of package tuples.

        :param rpms_to_install: The list of rpms (tuple format - name, version
                                release) to be installed
        :param ignoreInstalled: Special flag to ignore installed pkgs. When
                               updating, and the dry_run flag is true, we are
                               not actually removing the files before
                               installing new ones, so the install procedure
                               needs to know that is a dry_run update, in order
                               to avoid an exception such as the files are
                               already installed.
        :param download_only: If True, the installation stops after the rpms
                              are download from the remote repository
        :param justdb: If true, just the database will be updated for the
                       installation and no file operations will be performed
        :param overwrite: If true and the files of the packages to be installed
                          are already in the installation area, they will be
                          overwritten.
        :param nodeps: do not installe dependencies

        """
        packagelist = self.getPackageListFromTuples(rpms_to_install)
        self._install(packagelist,
                      justdb=justdb,
                      overwrite=overwrite,
                      dry_run=dry_run,
                      ignoreInstalled=ignoreInstalled,
                      download_only=download_only,
                      nodeps=nodeps,
                      nodeps_update=nodeps_update,
                      ignoredInstalledList=ignoredInstalledList)

    def _install(self, packagelist,
                 justdb=False,
                 overwrite=False,
                 nodeps=False,
                 dry_run=False,
                 ignoreInstalled=False,
                 download_only=False,
                 nodeps_update=False,
                 ignoredInstalledList=[]):
        '''
        Installation procedure, it takes a list of package objects.

        :param packagelist: the list of packages to be installed
        :param justdb: If true, just the database will be updated for the
                       installation and no file operations will be performed
        :param overwrite: If true and the files of the packages to be installed
                          are already in the installation area, they will be
                          overwritten.
        :param nodeps: If True, exclude dependencies
        :param dry_run: If true, the installer will just display the packages
                        involved, without performing any action on files or on
                        database
        :param ignoreInstalled: Special flag to ignore installed pkgs. When
                                updating, and the dry_run flag is true, we are
                                not actually removing the files before
                                installing new ones, so the install procedure
                                needs to know that is a dry_run update, in
                                order to avoid an exception such as the files
                                are already installed.
        :param download_only: If True, the installation stops after the rpms
                              are download from the remote repository
        '''
        if download_only:
            ignoreInstalled = True

        rpmtoinstall = self.getPackageListToInstall(
            packagelist, nodeps=nodeps, ignoreInstalled=ignoreInstalled,
            nodeps_update=nodeps_update,
            ignoredInstalledList=ignoredInstalledList)

        # Deduplicating in case some package were there twice
        # but keep the order...
        # There might be two as we take list of packages,
        # and getPackagesToInstall is called multiple
        # times...
        rpmtoinstalldeduprev = []
        for p in rpmtoinstall:
            if p not in rpmtoinstalldeduprev:
                rpmtoinstalldeduprev.append(p)

        # If dry run, just display the info
        if dry_run:
            msg = "\n\t".join([p.rpmName() for p in rpmtoinstalldeduprev])
            self.log.info(("Dry run mode, install list (%s packages):\n\t "
                           " %s") % (len(rpmtoinstalldeduprev), msg))
            return

        # Now downloading
        if not download_only:
            self.log.warning("%s RPM files to install" %
                             len(rpmtoinstalldeduprev))
        filestoinstall = {}
        for package in rpmtoinstalldeduprev:
            localcopy = self._findFileLocally(package)
            if localcopy is not None:
                if not download_only:
                    self.log.info("Using file %s from cache" % localcopy)
                filestoinstall[package] = (localcopy, True)
            else:
                self.threadPool.add_task(self._downloadfiles,
                                         [package], metadata=True,
                                         forced=download_only)
        results_download = self.threadPool.get_results()
        for result_download in results_download:
            if result_download['success']:
                filename = result_download['result']['installlist'][0]
                filestoinstall[filename] = (
                    result_download['result']['files'][0], False)
            else:
                raise Exception("Error in downloading files")

        if download_only:
            return
        # Reorder after download
        filestoinstall_tmp = []
        for package in rpmtoinstalldeduprev:
            filestoinstall_tmp.append(filestoinstall[package])
        filestoinstall = filestoinstall_tmp

        # And installing...
        # We should deal with the order to avoid errors in case of problems
        # Half waythrough XXX
        filesinstalled = []
        # List is already reversed by the topological sort
        for (rpm, inLocalCache) in filestoinstall:
            self._installpackage(rpm, justdb=justdb,
                                 overwrite=overwrite,
                                 removeAfterInstall=(not inLocalCache))
            filesinstalled.append(rpm)

        if len(filesinstalled) > 0:
            self.log.info("Installed:")
            for f in filesinstalled:
                self.log.info(os.path.basename(f))
        else:
            self.log.info("Nothing Installed")

    def _findInExtrapackages(self, req, extrapackages):
        ''' Util function to check if a package scheduled
        to be installed already fulfills a given requirement

        :param req: the requirement to check
        :param extrapackages: the list of packages that will
                              be installed

        :returns: the package that fulfills the requirement or
                  None
        '''
        for extrap in extrapackages:
            if extrap.fulfills(req):
                return extrap
        return None

    def _getPackagesToRemove(self, p,
                             extrapackages=None):
        '''
        Proper single package installation method

        :param p: the package that will be removed
        :param extrapackages: the list of packages that will
                              be removed

        :returns: the list of packages to remove
        '''
        # Setting up data if needed
        if extrapackages is None:
            extrapackages = set()

        # Checking if the package is not there..
        if not self._localDB.isPackagesInstalled(p):
            self.log.warning("%s is not installed" % p.rpmName())
            return []

        # We are planning to remove p, so its provides are now a granted
        extrapackages.add(p)
        toremove = [p]
        # Iterating though the reuired packages
        for req in p.requires:
            if req.name in IGNORED_PACKAGES:
                continue
            match = self._lbYumClient.findLatestMatchingRequire(req)
            if match and match not in extrapackages:
                toremove += self._getPackagesToRemove(match,
                                                      extrapackages)
        return toremove

    def _getPackagesToInstall(self, p,
                              extrapackages=set(),
                              ignoreInstalled=False,
                              packagelist=None,
                              install_graph=None,
                              nodeps_update=False,
                              ignoredInstalledList=[]):
        '''
        Proper single package installation method

        :param p: the package that will be installed
        :param extrapackages: the list of packages that will be installed
        :param ignoreInstalled: Special flag to ignore installed pkgs. When
                                updating, and the dry_run flag is true, we are
                                not actually removing the files before
                                installing new ones, so the install procedure
                                needs to know that is a dry_run update, in
                                order to avoid an exception such as the files
                                are already installed.
        :param packagelist: the list of packages to be installed

        :returns: the graph of packages to install
        '''
        if install_graph is None:
            install_graph = Graph()
        # Checking if the package is already there..
        if self._localDB.isPackagesInstalled(p) and not ignoreInstalled:
            if len(ignoredInstalledList) == 0:
                self.log.warning("Please use reinstall! %s already installed" %
                                 p.rpmName())
            return install_graph, []
        extrapackages.add(p)
        # Iterating though the reuired packages, first checking
        # what's already on the local filesystem...
        nothing_added = True
        missing_deps = []
        for req in p.requires:
            if req.name in IGNORED_PACKAGES:
                continue
            # Checking that one of the typed in packages
            # do not already provide the package...
            tmp = self._findInExtrapackages(req, packagelist)
            tmp_ignored_installed = self._findInExtrapackages(
                req, ignoredInstalledList)
            if tmp is not None and (not ignoreInstalled or nodeps_update):
                self.log.warning("%s already fulfilled by %s, to be "
                                 "installed" % (str(req), tmp.name))
            elif tmp_ignored_installed is not None:
                self.log.warning(
                    "%s already fulfilled by %s-%s-%s, 'already installed" %
                    (str(req), tmp_ignored_installed.name,
                     tmp_ignored_installed.version,
                     tmp_ignored_installed.release))
            elif ((not ignoreInstalled or nodeps_update) and
                    self._localDB.provides(req)):
                # Now checking whether the package isn't already installed...
                self.log.info("%s already available on local system" %
                              str(req))
            else:
                # Ok lets find in from YUM now...
                match = self._lbYumClient.findLatestMatchingRequire(req)
                if match:
                    nothing_added = False
                    install_graph.add_edge([p, match])
                    if match not in extrapackages:
                        install_graph, missingTmp = self._getPackagesToInstall(
                            match, extrapackages,
                            ignoreInstalled=ignoreInstalled,
                            packagelist=packagelist,
                            install_graph=install_graph,
                            nodeps_update=nodeps_update,
                            ignoredInstalledList=ignoredInstalledList)
                        missing_deps.extend(missingTmp)
                elif self.strict:
                    missing_deps.append({
                        'dependency': req,
                        'package': p
                    })

        if not len(p.requires) or nothing_added:
            Nertex = "%s|%s|%s" % (p.name,
                                   p.version,
                                   p.release)
            install_graph.add_vertex(Nertex, p)
        return install_graph, missing_deps

    def _installpackage(self, filename, removeAfterInstall=True,
                        justdb=False, overwrite=False):
        ''' To install a RPM and record the info in the local DB

        :param filename: the name of the file that is installed
        :param removeAfterInstall: If true, the rpm will be deleted after
                                   installation from the cache directory
        :param justdb: If true, just the database will be updated for the
                       installation and no file operations will be performed
        :param overwrite: If true and the files of the packages to be installed
                          are already in the installation area, they will be
                          overwritten.
        '''
        # The PackageManager responsible for dealing
        # with the local package file
        pm = PackageManager(filename, self._siteroot, self._relocateMap,
                            tmp_dir=self._tmpdir)
        # DBManager to update local DB
        db = self._localDB
        # Metadata associated with the RPM
        dbp = pm.getPackage()
        try:
            # Now extract the file to disk
            self.log.warning("Installing %s just-db=%s" % (filename, justdb))
            if not justdb:
                pm.extract(overwrite=overwrite)
            else:
                self.log.warning(
                    "--just-db mode, will not install files from %s"
                    % filename)
            # Update the local DB
            db.addPackage(dbp, pm.getRelocatedFileMetadata())

            # Now checking
            if not justdb:
                pm.checkFileSizesOnDisk()

        except Exception as e:
            self.log.error(e)
            # Rollback here
            db.removePackage(dbp)
            raise

        if not justdb:
            try:
                # Running the post install
                self._runPostInstall(pm, dbp)
            except Exception as e:
                self.log.error(e)
                traceback.print_exc()
                self.log.error("Error running post install for %s" % filename)
        else:
            self.log.warning("--just-db mode, will not attempt to run "
                             "post-install for %s"
                             % filename)

        # Now cleanup if install was successfull
        if removeAfterInstall:
            self.log.debug("Install of %s succesful, removing RPM"
                           % filename)
            # Checking the location, do not remove files that are in a
            # local cache...
            willremove = True
            for cachedir in self._localRPMcache:
                if abspath(filename).startswith(abspath(cachedir)):
                    self.log.debug("File %s in local cache, will not remove"
                                   % filename)
                    willremove = False
            if willremove:
                self.log.info("Removing %s" % filename)
                os.unlink(filename)

    def _runPostInstall(self, packageManager, dbPackage):
        ''' Runs the post install script for a given
        package

        :param packageManager: the package manager
        :param dbPackage: the package of whose post install script
                          should run - in database format
        '''

        # First checking whether we have a script to run
        piscriptcontent = packageManager.getPostInstallScript()
        if not piscriptcontent:
            return

        # Opensing the tempfile and running it
        db = self._localDB
        db.setPostInstallRun(dbPackage, "N")

        # Setting the RPM_INSTALL_PREFIX expected by the scripts
        newenv = dict(os.environ)
        # Forcing the siteroot as needed by some scripts
        newenv["MYSITEROOT"] = self._siteroot
        prefix = packageManager.getInstallPrefix()
        if prefix is not None:
            self.log.warning("Setting RPM_INSTALL_PREFIX to %s" % prefix)
            newenv["RPM_INSTALL_PREFIX"] = prefix

        import tempfile
        import subprocess
        self.log.info("Running post-install scripts for %s"
                      % packageManager.getFullName())
        with tempfile.NamedTemporaryFile(prefix="lbpostinst",
                                         delete=False) as piscript:
            try:
                data = bytes(piscriptcontent, 'utf-8')
            except:
                data = bytes(piscriptcontent)
            piscript.write(data)
            piscript.flush()
            shellpath = "/bin/sh"
            bashpath = "/bin/bash"
            if os.path.exists(bashpath):
                shellpath = bashpath

            rc = subprocess.check_call([shellpath, piscript.name],
                                       stdout=sys.stdout,
                                       stderr=sys.stderr,
                                       env=newenv)
            if rc == 0:
                db.setPostInstallRun(dbPackage, "Y")
            else:
                db.setPostInstallRun(dbPackage, "E")

    def addDirToRPMCache(self, cachedir):
        ''' Add a directory to the list of dirs that will be scanned
        to look for RPM files before scanning them

        :param cachedir: the path to the cache directory
        '''
        self._localRPMcache.append(cachedir)

    def _findFileLocally(self, package):
        ''' Look for RPM  in the local cache directory

        :param package: the package to look for
        '''
        for cachedir in self._localRPMcache:
            # Try to look for file on local disk
            self.log.debug("Looking for %s in %s"
                           % (package.rpmFileName(), cachedir))
            localfile = findFileInDir(package.rpmFileName(), cachedir)
            if localfile is not None:
                return localfile
        return None

    def _downloadfiles(self, installlist, location=None, metadata=False,
                       forced=False):
        """ Downloads a list of files

        :param installlist: the files that need download for installation
        :param location: the location where to download data
        :param metadata: If true, it the function return a dict with
                         the list of downloaded files
        :param force: If True, the file will be downloaded even if it
                      is in local cache.
        """

        # Default to the TMP directory...
        if location is None:
            location = self._tmpdir

        try:
            # Python 3 workaround
            import urllib.request as urllib
        except:
            import urllib

        files = []
        for pack in installlist:
            filename = pack.rpmFileName()
            full_filename = os.path.join(location, filename)
            files.append(full_filename)

            # Checking if file is there and is ok
            needs_download = True
            if os.path.exists(full_filename):
                fileisok = self._checkRpmFile(full_filename)
                # fileisok could be None, but in that case we could
                # not check so download again
                if fileisok or fileisok is None:
                    needs_download = False

            # Now doing the download
            if not needs_download and not forced:
                self.log.debug("%s already exists, will not download"
                               % filename)
            else:
                counter_download = 0
                while counter_download < 2:
                    tmp_name = "%s.tmp" % (full_filename)
                    self.log.info("Downloading %s to %s" % (pack.url(),
                                                            tmp_name))

                    try:
                        urllib.urlretrieve(pack.url(), tmp_name)
                        fileisok = self._checkRpmFile(tmp_name)
                        if fileisok or fileisok is None:
                            shutil.copy(tmp_name, full_filename)
                            break
                    except Exception as e:
                        self.log.error("Error in downloading file %s with" %
                                       (full_filename, e))
                    finally:
                        if os.path.exists(tmp_name):
                            self.log.info("Removing temporary file: %s" %
                                          tmp_name)
                            os.unlink(tmp_name)
                    counter_download += 1
                if counter_download == 2:
                    raise Exception("Error in downloading file %s" % filename)
        if metadata:
            return {
                'installlist': installlist,
                'files': files
                }
        return files

    def _checkRpmFile(self, full_filename):
        """ Check a specific RPM file

        :param full_filename: the path to the file that needs checking
        """
        return sanitycheckrpmfile(full_filename)

    # Package removal
    # ############################################################################
    def remove(self, rpms_to_remove, justdb=False, dry_run=False, force=False,
               nodeps=True):
        ''' Implement the remove of packages

        :param rpms_to_remove: The list of rpms (tuple format - name, version
                               release) to be removed
        :param justdb: If true, just the database will be updated for the
                       installation and no file operations will be performed
        :param dry_run: If true, the installer will just display the packages
                        involved, without performing any action on files or on
                        database
        :param force: If true, the operation will be forced.
        '''
        packagelist = self.getPackageListFromTuples(rpms_to_remove,
                                                    local=True,
                                                    exact_search=True,
                                                    )
        self._remove(packagelist,
                     justdb=justdb,
                     force=force,
                     dry_run=dry_run,
                     nodeps=nodeps)

    def _remove(self, removelist, justdb=False, force=False,
                dry_run=False, nodeps=True):
        '''
        Remove packages from the system

        :param packagelist: the list of packages to be removed
        :param justdb: If true, just the database will be updated for the
                       installation and no file operations will be performed
        :param force: If true, the operation will be forced.
        :param dry_run: If true, the installer will just display the packages
                        involved, without performing any action on files or on
                        database
        '''
        if not force:
            for p in removelist:
                required_by = self._localDB \
                                  .findPackagesRequiringPackage(p.name,
                                                                p.version,
                                                                p.release,
                                                                True)
                for _, r in required_by:
                    for req in r:
                        if req not in removelist:
                            raise Exception(("Package %s is required "
                                             " by %s. Please use "
                                             "--force" %
                                             (p.name, req.name)))
        if not nodeps:
            removelist_tmp = []
            for p in removelist:
                removelist_tmp += self._getPackagesToRemove(p)
            removelist = removelist_tmp
        if dry_run:
            msg = "\n\t".join([p.rpmName() for p in removelist])
            self.log.info(("Dry run mode, %s packages to remove:\n\t"
                           " %s") % (len(removelist), msg))
            return

        # Deduplicating in case some package were there twice
        # but keep the order...
        # There might be two as we take list of packages,
        # and getPackagesToInstall is called multiple
        # times...
        rpmtoremovededuprev = []
        for p in removelist:
            if p not in rpmtoremovededuprev:
                rpmtoremovededuprev.append(p)
        self.log.warning("%s RPM files to remove" % len(rpmtoremovededuprev))
        toRemoveDBPackages = set()
        for p in rpmtoremovededuprev:
            dbPackage = list(self._localDB.getDBPackages(match=p.name,
                                                         vermatch=p.version,
                                                         relmatch=p.release,
                                                         local_only=True,
                                                         exact_search=True))
            toRemoveDBPackages.update(dbPackage)
        for p in toRemoveDBPackages:
            self._removeOne(p, force=force, justdb=justdb)

    def _removeOne(self, package, force=False, justdb=False):
        '''
        Remove one package from DB and disk

        :param package: the package to be removed
        :param force: If true, the operation will be forced.
        :param justdb: If true, just the database will be updated for the
                       installation and no file operations will be performed
        '''
        self.log.warning("Removing %s %s %s" % (package.name,
                                                package.version,
                                                package.release))

        filemetadata = self._localDB.loadFMData(package.rpmName())
        if not justdb:
            # Doing the files first
            for l in filemetadata:
                file_path = "%s%s" % (self._siteroot, '%s' % l[0])
                if not os.path.isdir(file_path):
                    self.log.debug("Removing file %s" % file_path)
                    try:
                        os.unlink(file_path)
                    except:
                        pass  # ignore error
            # Doing the files first
            for l in filemetadata[::-1]:
                file_path = "%s%s" % (self._siteroot, '%s' % l[0])
                if os.path.isdir(file_path):
                    if os.path.islink(file_path):
                        self.log.debug("Removing link %s" % file_path)
                        os.unlink(file_path)
                    else:
                        self.log.debug("Removing dir %s" % file_path)
                        file_list = os.listdir(file_path)
                        if len(file_list) > 0:
                            self.log.debug("Dir %s is not empty" %
                                           file_path)
                        else:
                            os.rmdir(file_path)
        else:
            self.log.info("Running in just database mode."
                          "The files are not deleted")
        # Now removing the package metadata
        self._localDB.removePackage(package.toDmPackage())

    # Package update
    # ############################################################################
    def update(self, rpms_list, dry_run=False, justdb=False, nodeps=True):
        """
        Updates to the required version the rpms

        :param rpms_list: The list of rpms (tuple format - name, version
                          release) to be updated
        """
        for rpm in rpms_list:
            # Convert from None to latest version and release
            tmp = self.remoteFindPackage(rpm[0], rpm[1], rpm[2])[0]
            package = (tmp.name, tmp.version, tmp.release)

            local_packages = self.localFindPackages(package[0],
                                                    None,
                                                    None)
            for local_package in local_packages:
                if local_package.name == package[0]:
                    cmpVers = VersionedObject.cmpStandardVersion(
                        VersionedObject.getStandardVersion(package[1]),
                        VersionedObject.getStandardVersion(
                            local_package.version))

                    if (cmpVers < 0 or
                        (cmpVers == 0 and
                         (package[2] < local_package.release))):
                        raise Exception('You are downgrading! Please remove '
                                        'first the existing version! The '
                                        'script needs to install %s-%s-%s, but'
                                        ' the package %s-%s-%s is already '
                                        'installed' % (package[0],
                                                       package[1],
                                                       package[2],
                                                       local_package.name,
                                                       local_package.version,
                                                       local_package.release))
                    if (cmpVers == 0 and (
                            package[2] == local_package.release)):
                        raise Exception('Please use reinstall! The script '
                                        'needs to install %s-%s-%s, but the '
                                        'package %s-%s-%s is already '
                                        'installed' % (package[0],
                                                       package[1],
                                                       package[2],
                                                       local_package.name,
                                                       local_package.version,
                                                       local_package.release))
        self._updateOrReinstall(rpms_list, dry_run=dry_run, justdb=justdb,
                                nodeps=nodeps)

    def display_missing_deps(self, missing_deps):
        for missing in missing_deps:
            req = missing['dependency']
            p = missing['package']
            self.log.error("%s-%s-%s dependency of %s-%s-%s "
                           "cannot be satisfied" % (req.name,
                                                    req.version,
                                                    req.release,
                                                    p.name,
                                                    p.version,
                                                    p.release))

        raise Exception("Not all dependencies were fulfilled")

    def reinstall(self, rpms_list, dry_run=False, justdb=False, nodeps=True):
        """
        Reinstall to the required version the rpms

        :param rpms_list: The list of rpms (tuple format - name, version
                          release) to be reinstalled
        """
        for rpm in rpms_list:
            # Convert from None to latest version and release
            tmp = self.remoteFindPackage(rpm[0], rpm[1], rpm[2])[0]
            package = (tmp.name, tmp.version, tmp.release)

            local_packages = self.localFindPackages(package[0],
                                                    None,
                                                    None)
            for local_package in local_packages:
                if local_package.name == package[0]:
                    cmpVers = VersionedObject.cmpStandardVersion(
                        VersionedObject.getStandardVersion(package[1]),
                        VersionedObject.getStandardVersion(
                            local_package.version))
                    if (cmpVers < 0 or
                        (cmpVers == 0 and
                         (package[2] < local_package.release))):
                        raise Exception('You are downgrading! Please remove '
                                        'first the existing version! The '
                                        'script needs to install %s-%s-%s, but'
                                        ' the package %s-%s-%s is already '
                                        'installed' % (package[0],
                                                       package[1],
                                                       package[2],
                                                       local_package.name,
                                                       local_package.version,
                                                       local_package.release))
                    if (cmpVers > 0 or
                        (cmpVers == 0 and
                         (package[2] > local_package.release))):
                        raise Exception('Please use upgrading! The script '
                                        'needs to install %s-%s-%s, but the '
                                        'package %s-%s-%s is already '
                                        'installed' % (package[0],
                                                       package[1],
                                                       package[2],
                                                       local_package.name,
                                                       local_package.version,
                                                       local_package.release))
        self._updateOrReinstall(rpms_list, dry_run=dry_run, justdb=justdb,
                                nodeps=nodeps)

    def _updateOrReinstall(self, rpms_list, dry_run=False, justdb=False,
                           nodeps=True):
        install_graph = None
        packagelist = self.getPackageListFromTuples(rpms_list)
        rpms_to_remove = []
        ignoredInstalledList = []
        missing_deps = []
        for p in packagelist:
            install_graph, missing_deps_tmp = self._getPackagesToInstall(
                p, ignoreInstalled=True,
                packagelist=packagelist,
                install_graph=install_graph)
            missing_deps.extend(missing_deps_tmp)
        if len(missing_deps) != 0:
            self.display_missing_deps(missing_deps)
        packages_graph = install_graph.getPackageOrder()
        import copy
        ignoredInstalledList = copy.copy(packages_graph)
        for package in packages_graph:
            local_packages = self.localFindPackages(package.name,
                                                    None,
                                                    None,
                                                    True)

            if len(local_packages):
                local_package = local_packages[0]
                if (local_package.version < package.version or (
                     local_package.version == package.version and
                     local_package.release < package.release)):
                    if not nodeps:
                        rpms_to_remove.append((package.name, None, None))
                        # Updateing a req to the latest version
                        rpms_list.append((package.name, package.version,
                                         package.release))
                    ignoredInstalledList.remove(package)
            else:
                ignoredInstalledList.remove(package)
        if nodeps:
            for rpm_name, _, _ in rpms_list:
                rpms_to_remove.append((rpm_name, None, None))
        try:
            self.remove(rpms_to_remove, force=True, dry_run=dry_run,
                        justdb=justdb,
                        nodeps=True)
        except Exception as e:
            self.log.error("Error removing file %s when updating\n" %
                           rpms_to_remove)
            raise e
        nodeps_update = True
        if not nodeps:
            nodeps_update = False
        self.install(rpms_list, dry_run=dry_run,
                     ignoreInstalled=True,
                     nodeps_update=nodeps_update,
                     overwrite=True, justdb=justdb,
                     ignoredInstalledList=ignoredInstalledList)

    # Package query
    # ############################################################################
    def queryPackages(self, nameregexp=None,
                      versionregexp=None,
                      releaseregexp=None):
        ''' Implement the listing of packages

        :param nameRegexp: Regex for the name of the package
        :param versionRegexp: Regex for the version of the package
        :param releaseRegexp: Regex for the release of the package
        '''
        for l in sorted(list(self.remoteListPackages(nameregexp,
                                                     versionregexp,
                                                     releaseregexp))):
            print(l.rpmName())

    # Providers query
    # ############################################################################
    def queryProviders(self, nameregexp=None,
                       versionregexp=None,
                       releaseregexp=None):
        ''' Implement the listing of provides

        :param nameRegexp: Regex for the name of the package
        :param versionRegexp: Regex for the version of the package
        :param releaseRegexp: Regex for the release of the package
        '''
        allpackages = set()
        for l in sorted(list(self.remoteListProvides(nameregexp))):
            for p in self.remoteFindPackage(l.name,
                                            l.version,
                                            l.release):
                allpackages.add(p)
        for l in sorted(allpackages):
            print(l.rpmName())

    def checkPackgesFromTuples(self, rpms_to_verify):
        ''' Implement the verifiy method of packages

        :param rpms_to_verify: the list of rpms to be verified
        '''
        packagelist = self.getPackageListFromTuples(rpms_to_verify,
                                                    local=True)
        self.checkPackages(packagelist)

    def listInstalledPackages(self, nameregexp=None,
                              versionregexp=None, releaseregexp=None):
        ''' Implement the listing of packages

        :param nameRegexp: Regex for the name of the package
        :param versionRegexp: Regex for the version of the package
        :param releaseRegexp: Regex for the release of the package
        '''
        allpackages = list(self.localListPackages(nameregexp,
                                                  versionregexp,
                                                  releaseregexp))
        # Make the display look nicer
        max_len_n = 0
        max_len_v = 0
        max_len_r = 0
        for n, v, r, _ in allpackages:
            max_len_n = len(n) if len(n) > max_len_n else max_len_n
            max_len_v = len(v) if len(v) > max_len_v else max_len_v
            max_len_r = len(r) if len(r) > max_len_r else max_len_r

        # Sort first by the location ( local or remote path) and then by name
        for n, v, r, source in sorted(allpackages, key=lambda x: (x[3], x[0])):
            name = "%s" % n + ' '*(max_len_n - len(n))
            version = "%s" % v + ' '*(max_len_v - len(v))
            release = "%s" % r + ' '*(max_len_r - len(r))
            print("%s\t%s\t%s\t%s" % (name, version, release, source))
