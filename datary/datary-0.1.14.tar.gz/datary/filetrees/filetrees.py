# -*- coding: utf-8 -*-
"""
Datary sdk Filetrees File
"""
import os

from urllib.parse import urljoin
from datary.repos import DataryRepos
from scrapbag import force_list, add_element

import structlog


logger = structlog.getLogger(__name__)


class DataryFiletrees(DataryRepos):
    """
      Datary Filetrees module class
    """
    def get_commit_filetree(self, repo_uuid, commit_sha1):
        """
        ==============  =============   ====================================
        Parameter       Type            Description
        ==============  =============   ====================================
        repo_uuid       int             repository id
        commit_sha1     str             filetree sha1
        ==============  =============   ====================================

        Returns:
            filetree of all commits done in a repo.

        """
        url = urljoin(self.URL_BASE,
                      "commits/{}/filetree".format(commit_sha1))
        params = {'namespace': repo_uuid}
        response = self.request(
            url, 'GET', **{'headers': self.headers, 'params': params})

        return response.json() if response else {}

    def get_wdir_filetree(self, wdir_uuid):
        """
        ==============  =============   ====================================
        Parameter       Type            Description
        ==============  =============   ====================================
        wdir_uuid       str             working directory id
        ==============  =============   ====================================

        Returns:
            filetree of a repo workdir.

        """
        url = urljoin(self.URL_BASE,
                      "workdirs/{}/filetree".format(wdir_uuid))
        response = self.request(url, 'GET', **{'headers': self.headers})

        return response.json() if response else {}

    def get_wdir_changes(self, wdir_uuid=None, **kwargs):
        """
        ================  =============   ====================================
        Parameter         Type            Description
        ================  =============   ====================================
        wdir_uuid         str              working directory id
        ================  =============   ====================================

        Returns:
            (dict) changes in workdir.
        """

        # try to take wdir_uuid with kwargs
        if not wdir_uuid:
            wdir_uuid = self.get_describerepo(
                **kwargs).get('workdir', {}).get('uuid')

        url = urljoin(self.URL_BASE,
                      "workdirs/{}/changes".format(wdir_uuid))
        response = self.request(url, 'GET', **{'headers': self.headers})

        return response.json() if response else {}

    def format_wdir_changes(self, wdir_changes_tree):
        """
        ==================  =============   ==================================
        Parameter           Type            Description
        ==================  =============   ==================================
        wdir_changes_tree   list            working changes tree
        ==================  =============   ==================================

        Returns:
            (dict) changes in workdir formatting as filetree format.
        """
        result = {}

        for sublist in list(wdir_changes_tree):
            for item in force_list(sublist):
                add_element(
                    result,
                    os.path.join(item.get('dirname', ''),
                                 item.get('basename', '')),
                    item.get('inode', 'unkwown_dataset_uuid')
                )

        return result
