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

:author: Stefan-Gabriel Chitic
'''
import logging
import os
import traceback
from os.path import abspath
import shutil
import stat
import json

from lbinstall.Model import IGNORED_PACKAGES
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


class YumChecker(object):
    '''
    LHCb Software checker.
    This class can be used to query the remote YUM database,
    and to checker packages on disk.


    :param siteroot: The folder where checker will use tmp data
    :param config: The configuration used by checker
    :param localRPMcache: A local folder to used instead of downloading the
                          rpms
    :param disableYumCheck: Disables the YUM check
    :param tmp_dir: A custom directory to be used a tmp instead of
                    <siteroot>/tmp/
    :param pool_size: The pool size of the download thread pool
    :param stric: Flag used to stop an action if a dependency is not satisfied
    '''

    def __init__(self, siteroot, config=None,
                 localRPMcache=None, disableYumCheck=False,
                 strict=True, simple_output=True):
        '''Class to checker a set of packages to a specific area
        '''

        self.log = logging.getLogger(__name__)
        self._siteroot = os.path.abspath(siteroot)
        self._lcgDir = os.path.join(self._siteroot, "lcg")
        if config is None:
            from lbinstall.LHCbConfig import Config
            config = Config()
        self._config = config
        # Creating the install area and getting the relevant info
        self.__installArea = InstallArea(self._config, self._siteroot)
        self._lbYumClient = self.__installArea \
                                .createYumClient(not disableYumCheck)
        self._localRPMcache = []
        self.simple_output = simple_output
        if localRPMcache is not None:
            self._localRPMcache = localRPMcache
        self.strict = strict

    # Various utilities to query the yum database
    # ############################################################################

    def getPackageListFromTuples(self, tuplesList, force_local=False):
        """Transforms a list of tuples to a list of packages

        :param tuplesList: A list of tuples (name, version, release) to be
                           transformed into list of packages

        :returns: a list of database packages
        """
        packagelist = []
        for rpmname, version, release in tuplesList:
            packagelist.extend(self.remoteFindPackage(rpmname,
                                                      version,
                                                      release,
                                                      force_local=force_local))
        return packagelist

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

    def remoteFindPackage(self, name, version=None, release=None,
                          force_local=False):
        """
        Finds the remote package (from YUM repo) based on name, version
        and release

        :param name: the name of the package
        :param version: (optional) the version of the package
        :param release: (optional) the release of the package

        :returns: the remote package
        """
        req = Requires(name, version, release, None, "EQ", None)
        pack = self._lbYumClient.findLatestMatchingRequire(
            req, force_local=force_local)

        res = [pack] if pack is not None else []
        return res

    def displayDependenciesGraph(self, rpms, filename="output",
                                 tree_mode=False,
                                 force_local=False):
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
                p, packagelist=packagelist,
                install_graph=install_graph,
                force_local=force_local)
            missing_deps.extend(missing_deps_tmp)
        if len(missing_deps) != 0:
            self.display_missing_deps(missing_deps)
        install_graph.generate_dot(
            tree_mode=tree_mode,
            filename=filename)

    def getMissingPackgesFromTuples(self, rpms_to_install,
                                    force_local=False):
        """
        Gets the package list that will be installed including (optional) their
        dependencies

        :param packagelist: the package list of files to install

        :returns: the list of packages that will be installed including
                  (optional) their dependencies

        """
        packagelist = self.getPackageListFromTuples(rpms_to_install,
                                                    force_local=force_local)
        if not packagelist:
            raise Exception("Please specify one or more packages")

        # Looking for the files to install
        rpmtoinstall = list()
        install_graph = None
        missing_deps = []
        for p in packagelist:
            install_graph, missing_deps_tmp = self._getPackagesToInstall(
                p, packagelist=packagelist,
                extrapackages=set(),
                install_graph=install_graph,
                force_local=force_local)
            missing_deps.extend(missing_deps_tmp)
        return missing_deps

    def checkPackgesFromTuples(self, rpms_to_install, csv_name=None,
                               force_json=False):
        """
        Gets the package list that will be installed including (optional) their
        dependencies

        :param packagelist: the package list of files to install

        :returns: the list of packages that will be installed including
                  (optional) their dependencies

        """
        missing_deps = self.getMissingPackgesFromTuples(rpms_to_install)
        self.display_missing_deps(missing_deps, export_file=csv_name,
                                  force_json=force_json)

    def _getPackagesToInstall(self, p,
                              extrapackages=set(),
                              packagelist=None,
                              install_graph=None,
                              force_local=False):
        '''
        Proper single package installation method

        :param p: the package that will be installed
        :param extrapackages: the list of packages that will be installed
        :param packagelist: the list of packages to be installed

        :returns: the graph of packages to install
        '''
        if install_graph is None:
            install_graph = Graph()
        extrapackages.add(p)
        # Iterating though the reuired packages, first checking
        # what's already on the local filesystem...
        nothing_added = True
        missing_deps = []
        for req in p.requires:
            if req.name in IGNORED_PACKAGES:
                continue
            # Ok lets find in from YUM now...
            match = self._lbYumClient.findLatestMatchingRequire(
                req, force_local=force_local)
            if match:
                nothing_added = False
                install_graph.add_edge([p, match])
                if match not in extrapackages:
                    install_graph, missing_tmp = self._getPackagesToInstall(
                        match, extrapackages,
                        packagelist=packagelist,
                        install_graph=install_graph,
                        force_local=force_local)
                    missing_deps.extend(missing_tmp)
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

    def display_missing_deps(self, missing_deps, export_file=None,
                             force_json=False):
        if force_json:
            new_data = {}
            for missing in missing_deps:
                req = missing['dependency']
                req_name = "%s.%s.%s" % (req.name,
                                         req.version,
                                         req.release)
                p = missing['package']
                p_name = "%s.%s.%s" % (p.name,
                                       p.version,
                                       p.release)
                if not new_data.get(p_name, None):
                    new_data[p_name] = []
                new_data[p_name].append(req_name)
            with open(export_file, 'w') as outfile:
                json.dump(new_data, outfile)
            export_file = None
        if len(missing_deps) == 0:
            print("All dependencies are OK.")
            return
        if self.simple_output:
            self._display_simple_mode(missing_deps, export_file=export_file)
        else:
            self._display_full_mode(missing_deps, export_file=export_file)

    def _display_simple_mode(self, missing_deps, export_file=None):
        # Make the display look nicer
        print("Missing dependencies of packages")
        already_seen = []
        for missing in missing_deps:
            req = missing['dependency']
            if req.name in already_seen:
                continue
            already_seen.append(req.name)
        already_seen = sorted(already_seen)
        text = "\n".join(already_seen)
        if not export_file:
            print(text)
        else:
            try:
                f = open(export_file, 'w')
                f.write(text)
            except Exception as e:
                self.log.error(str(e))

    def _display_full_mode(self, missing_deps, export_file=None):
        # Make the display look nicer
        max_len_n = len("Dependecy Name ")
        max_len_v = len("Dependecy Version ")
        max_len_r = len("Dependecy Relesae ")
        max_len_n2 = len("Package Name ")
        max_len_v2 = len("Package Version ")
        max_len_r2 = len("Package Relesae ")

        for missing in missing_deps:
            req = missing['dependency']
            p = missing['package']
            n = req.name if req.name is not None else "None"
            v = req.version if req.version is not None else "None"
            r = req.release if req.release is not None else "None"
            max_len_n = len(n) if len(n) > max_len_n else max_len_n
            max_len_v = len(v) if len(v) > max_len_v else max_len_v
            max_len_r = len(r) if len(r) > max_len_r else max_len_r

            n = p.name if p.name is not None else "None"
            v = p.version if p.version is not None else "None"
            r = p.release if p.release is not None else "None"
            max_len_n2 = len(n) if len(n) > max_len_n2 else max_len_n2
            max_len_v2 = len(v) if len(v) > max_len_v2 else max_len_v2
            max_len_r2 = len(r) if len(r) > max_len_r2 else max_len_r2
        export_text = ""
        print("Missing dependencies of packages")
        n = "Dependecy Name"
        v = "Dependecy Version "
        r = "Dependecy Relesae"
        name = "%s" % n + ' ' * (max_len_n - len(n))
        version = "%s" % v + ' ' * (max_len_v - len(v))
        release = "%s" % r + ' ' * (max_len_r - len(r))

        n = "Package Name"
        v = "Package Version "
        r = "Package Relesae"
        name2 = "%s" % n + ' ' * (max_len_n2 - len(n))
        version2 = "%s" % v + ' ' * (max_len_v2 - len(v))
        release2 = "%s" % r + ' ' * (max_len_r2 - len(r))
        if not export_file:
            print("%s\t|%s\t|%s\t|%s\t|%s\t|%s" % (name, version, release,
                                                   name2, version2, release2))
        export_text += '%s, %s, %s, %s, %s, %s\n' % (
            name.strip(), version.strip(), release.strip(), name2.strip(),
            version2.strip(),
            release2.strip())
        already_printed = []
        for missing in missing_deps:
            req = missing['dependency']
            p = missing['package']
            n = req.name if req.name is not None else "None"
            v = req.version if req.version is not None else "None"
            r = req.release if req.release is not None else "None"
            name = "%s" % n + ' '*(max_len_n - len(n))
            version = "%s" % v + ' '*(max_len_v - len(v))
            release = "%s" % r + ' '*(max_len_r - len(r))

            n = p.name if p.name is not None else "None"
            v = p.version if p.version is not None else "None"
            r = p.release if p.release is not None else "None"
            name2 = "%s" % n + ' ' * (max_len_n2 - len(n))
            version2 = "%s" % v + ' ' * (max_len_v2 - len(v))
            release2 = "%s" % r + ' ' * (max_len_r2 - len(r))

            if not export_file:
                tmp = ("%s\t|%s\t|%s\t|%s\t|%s\t|%s" % (name, version, release,
                                                        name2, version2,
                                                        release2))
                if tmp not in already_printed:
                    print(tmp)
                    already_printed.append(tmp)
            export_text += '%s, %s, %s, %s, %s, %s\n' % (
                name.strip(), version.strip(), release.strip(), name2.strip(),
                version2.strip(),
                release2.strip())
            if export_file:
                try:
                    f = open(export_file, 'w')
                    f.write(export_text)
                except Exception as e:
                    self.log.error(str(e))

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

    def addDirToRPMCache(self, cachedir):
        ''' Add a directory to the list of dirs that will be scanned
        to look for RPM files before scanning them

        :param cachedir: the path to the cache directory
        '''
        self._localRPMcache.append(cachedir)

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
        to_return_packages_list = []
        for l in sorted(list(self.remoteListPackages(nameregexp,
                                                     versionregexp,
                                                     releaseregexp))):
            to_return_packages_list.append((l.name, l.version, l.release))
        return to_return_packages_list
