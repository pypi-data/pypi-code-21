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

ChainedDBManager is a class that manages the all the chained databases links
throw all the life cycle of an installation area.

:author: Stefan-Gabriel Chitic
'''

import os
import json


class ChainedConfigManager(object):
    """
    Manager for chained db paths

    :param siteroot: the installation area top directory
    """

    def __init__(self, siteroot):
        self.chainedDbList = []
        self.configFilePath = "%s/etc/chainedDBs.json" \
                              % siteroot

        # Initialize the file if it doesn't exist.
        if not os.path.exists(self.configFilePath):
            with open(self.configFilePath, 'a') as ftmp:
                ftmp.close()

    def addDb(self, path):
        '''
        Add a new path to the configuration file

        :param path: the path to be added for a new remote database
        '''
        if path is None:
            return
        if not self._checkPath(path):
            # If the file does not exist, raise an error
            raise Exception("Trying to add a non existing path as chained "
                            "install area")
        data = self._getDbs()
        # If the path exists in the configuration file, do not add it
        if path not in data:
            data.append(path)
            with open(self.configFilePath, 'wb') as f:
                try:
                    data = bytes(json.dumps(data), 'utf-8')
                except:
                    data = bytes(json.dumps(data))
                f.write(data)
            # Add the new path into the singleton path list in memory
            self.chainedDbList = data

    def _checkPath(self, path):
        """
        Checks if a path exists
        """
        return os.path.exists(path)

    def _getDbs(self):
        """
        For internal use, it gets all the paths from the memory and it
        loads the memory form the configuration file if empty or if force
        refreshed

        :returns: the list of chained databases
        """
        with open(self.configFilePath, 'rb') as ftmp:
            try:
                data = json.loads(ftmp.read().decode('utf-8'))
            except:
                # if the file is empty, json could not decode empty
                data = []
            ftmp.close()
            self.chainedDbList = data
        return self.chainedDbList

    def getDbs(self):
        """
        Returns a filtered list of the paths, excluding those non accessible at
        the runtime

        :returns: the list of chained databases
        """
        return [x for x in self._getDbs() if self._checkPath(x)]
