###############################################################################
# (c) Copyright 2012-2017 CERN                                                #
#                                                                             #
# This software is distributed under the terms of the GNU General Public      #
# Licence version 3 (GPL Version 3), copied verbatim in the file "COPYING".   #
#                                                                             #
# In applying this licence, CERN does not waive the privileges and immunities #
# granted to it by virtue of its status as an Intergovernmental Organization  #
# or submit itself to any jurisdiction.                                       #
###############################################################################
'''

Utilities to sync the local software DB with an existing Install area

'''
import logging
import os
import re

from os.path import join, isdir
from os import listdir

try:
    from LbConfiguration.Platform import extra_binary_list, binary_list
    # do0 are missing in lbconfiguration Platform
    tmp = extra_binary_list + binary_list
    allplatforms = set()
    for p in tmp:
        if "dbg" in p:
            allplatforms.add(p.replace("dbg", "do0"))
        allplatforms.add(p)

    import LbConfiguration.Package as Package
    import LbConfiguration.Project as Project
except Exception as e:
    logging.error(e)
    raise Exception("Could not load LbConfiguration module")


class InstallAreaTool(object):

    """
    Install area helper

    :params installAreaDir: the location of the install area
    """
    def __init__(self, installAreaDir=None):

        if installAreaDir is None:
            self._installAreaDir = os.environ["LHCBRELEASES"]
        else:
            self._installAreaDir = installAreaDir

        # Loading the list of projects and datapackages
        self._projects_installed = self._findProjectsFromConfig()
        self._datapacks_installed = self._findDataPackages()

    def getProjectList(self):
        '''
        returns a list of triplets (Project_name, version, platformlist)
        for all installed projects.

        :returns: the list of installed installed projects in the install area
        '''
        return self._projects_installed

    def getDatapackageList(self):
        '''
        returns a list of  (Project_hat_name, version)
        for all installed data packages.

        :returns: the list of database packages
        '''
        return self._datapacks_installed

    def _findProjectsFromConfig(self):
        '''
        Get list of projects from config and return the list of versions
        '''
        # Looking for projects in the Install area directory structure
        allprojects = []
        for p in Project.getProjectList():
            projdir = join(self._installAreaDir, p.NAME())
            allprojects += self._findProjectVersions(projdir)
        return allprojects

    def _findProjectVersions(self, projdir):
        '''
        Return the list of versions for a given project...
        '''
        # Now looking for versions with name matching PROJECT_vErsion
        allpvs = []
        name = os.path.basename(projdir)
        try:
            for v in listdir(projdir):
                m = re.match('^%s_(.*)$' % name, v)
                if m is not None:
                    # This really is a project
                    # Now looking for platforms
                    ia = join(projdir, v, "InstallArea")
                    platforms = []
                    for pdir in listdir(ia):
                        if pdir in allplatforms:
                            platforms.append(pdir)
                    allpvs.append((name, v.replace(name + "_", ""), platforms))
        except Exception as e:
            logging.error("problem with %s:" % projdir, e)
        return allpvs

    def _findProjectsFromDisk(self):
        '''
        Trawl though directory to find list of installed projects
        '''
        # Looking for projects in the Install area directory structure
        allprojects = []
        for d in listdir(self._installAreaDir):
            if isdir(join(self._installAreaDir, d)):
                # Project directories should be in upper case
                if d.upper() == d:
                    projdir = join(self._installAreaDir, d)
                    allprojects += self._findProjectVersions(projdir)
        return allprojects

    def _findDataPackages(self):
        '''
        Look for installed data packages
        '''
        allpacks = []
        for p in Package.getPackageList():
            try:
                packdir = join(self._installAreaDir, p.releasePrefix())
                for ver in listdir(packdir):
                    allpacks.append((p.tarBallName(), ver))
            except Exception as e:
                loggin.error("No package for %s" % p.tarBallName(), e)
        return allpacks


def lookupRPMsForProject(installer, name, version, platforms):
    '''
    Return a list of packages to be installed to have the
    project version and platforms requested...

    :param name: the name of the package
    :param version: the version of the package
    :param platforms: the platforms to look up

    :returns: list of packages to be installed
    '''
    tmpl = "%s_%s" % (name, version)
    logging.info("Looking for packages related to: %s" % tmpl)
    # cmtconfigs feature in RPM names with the - replaced by a _
    allcmtconfigs = [c.replace("-", "_") for c in allplatforms]
    mycmtconfigs = [c.replace("-", "_") for c in platforms]
    allpacks = set(installer.remoteListPackages("%s" % tmpl))

    # getnames = lambda l : [p.rpmName() for p in l]

    # We differentiate the packages by the fact the binary ones
    # have the CMTCONFIG in their name
    # We keeps all source RPMs and just the binary ones we need
    allbinpacks = set()
    for p in allpacks:
        for config in allcmtconfigs:
            if config in p.rpmName():
                    allbinpacks.add(p)

    # The source packages are just not binary ones
    sourcepacks = allpacks - allbinpacks
    binpacks = set()
    for p in allbinpacks:
        for config in mycmtconfigs:
            if config in p.rpmName():
                binpacks.add(p)

    return (binpacks | sourcepacks)


if __name__ == "__main__":
    iat = InstallAreaTool()
