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
"""
LbInstall specific config for LHCb

:author: Ben Couturier
"""
import os


class Config:

    """ Default configuration for LHCb

    :param defaultRepoURL: a custom default repository url
    :param skipConfig: if true, this flag allows the config
                       to skip the setup of the default
                       configuration.
    """
    def __init__(self, defaultRepoURL=None, skipConfig=False):
        self.CONFIG_VERSION = 1
        repos = {}

        # For the case when we want to override...
        if skipConfig:
            self.repos = repos
            return

        # Default LHCb URL
        repourl = "http://lhcb-rpm.web.cern.ch/lhcb-rpm/"
        if defaultRepoURL is not None:
            repourl = defaultRepoURL

        # Now adding the LHCb  URLs
        repos["lhcb"] = {"url": repourl + "/lhcb"}
        repos["lhcb2017"] = {"url": repourl + "/lhcb2017"}
        repos["lcg"] = {
            "url": "http://lcgpackages.web.cern.ch/lcgpackages/rpms"}
        repos["lhcbext"] = {"url": repourl + "/lcg"}
        repos["lhcbincubator"] = {"url": repourl + "/incubator"}

        self.repos = repos

    def getRepoConfig(self):
        """ return the configuration

        :returns: The repositories configuration map
        """
        return self.repos

    def getRelocateMap(self, siteroot):
        """
        Returns relocate command to be passed to RPM for the repositories

        :param siteroot: the location of the installation area

        :returns: the default relocation map based on the instalation area
        """
        ret = {'/opt/lcg/external': os.path.join(siteroot, 'lcg', 'external'),
               '/opt/lcg': os.path.join(siteroot, 'lcg', 'releases'),
               '/opt/LHCbSoft': siteroot}
        return ret
