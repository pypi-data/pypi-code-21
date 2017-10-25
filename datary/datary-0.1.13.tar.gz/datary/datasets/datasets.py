# -*- coding: utf-8 -*-
"""
Datary sdk Datasets File
"""
import os

from urllib.parse import urljoin
from datary.filetrees import DataryFiletrees
from scrapbag import exclude_empty_values, get_element

import structlog

logger = structlog.getLogger(__name__)


class DataryDatasets(DataryFiletrees):
    """
    Datary Datasets module
    """

    headers = {}

    def get_kern(self, dataset_uuid, repo_uuid='', wdir_uuid='', scope=''):
        """
        ================  =============   ====================================
        Parameter         Type            Description
        ================  =============   ====================================
        repo_uuid         int             repository id
        dataset_uuid      str
        ================  =============   ====================================

        Returns:
            (dict) dataset kern

        """
        return self.get_original(
            dataset_uuid, repo_uuid, wdir_uuid, 'kern', scope)

    def get_metadata(self, dataset_uuid, repo_uuid='', wdir_uuid='', scope=''):
        """
        ================  =============   ====================================
        Parameter         Type            Description
        ================  =============   ====================================
        repo_uuid         int             repository id
        dataset_uuid      str
        ================  =============   ====================================

        Returns:
            (dict) dataset metadata

        """
        return self.get_original(
            dataset_uuid, repo_uuid, wdir_uuid, 'meta', scope)

    def get_original(self, dataset_uuid, repo_uuid='', wdir_uuid='',
                     section_edge='original', scope=''):
        """
        ================  =============   ====================================
        Parameter         Type            Description
        ================  =============   ====================================
        dataset_uuid      str             dataset uuid
        repo_uuid         str             repository uuid
        wdir_uuid         str             workingdir uuid
        ================  =============   ====================================

        Returns:
            (dict) dataset original data
        """
        response = None

        if (repo_uuid or wdir_uuid) and dataset_uuid:
            url = urljoin(
                self.URL_BASE,
                "datasets/{}/{}".format(dataset_uuid, section_edge))

            # look in changes or namespace only if not wdir_uuid
            if scope != 'repo':
                params = exclude_empty_values(
                    {'namespace': repo_uuid, 'scope': wdir_uuid})
                response = self.request(
                    url, 'GET', **{'headers': self.headers, 'params': params})

            if not response or not response.json():
                logger.error(
                    "Not original retrieved from wdir scope",
                    namespace=repo_uuid,
                    scope=wdir_uuid,
                    dataset_uuid=dataset_uuid)

                params = exclude_empty_values(
                    {'namespace': repo_uuid, 'scope': repo_uuid})
                response = self.request(
                    url, 'GET', **{'headers': self.headers, 'params': params})
                if not response:
                    logger.error(
                        "Not original retrieved from repo scope",
                        namespace=repo_uuid,
                        scope=repo_uuid,
                        dataset_uuid=dataset_uuid)

        return response.json() if response else {}

    def get_dataset_uuid(self, wdir_uuid, path='', basename=''):
        """
        ================  =============   ====================================
        Parameter         Type            Description
        ================  =============   ====================================
        wdir_uuid         str             workdir uuid
        path              str             path of dataset
        basename          str             basename of dataset
        ================  =============   ====================================

        Returns:
            (str) uuid of dataset in path introduced in args.
        """
        dataset_uuid = None
        filepath = os.path.join(path, basename)

        if filepath:

            # retrieve wdir filetree
            wdir_filetree = self.get_wdir_filetree(wdir_uuid)

            # retrieve last commit filetree
            wdir_changes_filetree = self.format_wdir_changes(
                self.get_wdir_changes(wdir_uuid).values())

            # retrieve dataset uuid
            dataset_uuid = (get_element(wdir_changes_filetree, filepath)) or (
                get_element(wdir_filetree, filepath)) or None

        return dataset_uuid

    def get_commited_dataset_uuid(self, wdir_uuid, path='', basename=''):
        """
        ================  =============   ====================================
        Parameter         Type            Description
        ================  =============   ====================================
        wdir_uuid         str             wdir uuid.
        path              str             path of the file in Datary.
        basename          str             basename of the file in Datary.
        ================  =============   ====================================

        Returns:
            (string) uuid dataset/s of pathname introduced.
        """
        response = {}
        pathname = os.path.join(path, basename)

        if pathname:
            url = urljoin(self.URL_BASE,
                          "/workdirs/{}/filetree".format(wdir_uuid))
            params = exclude_empty_values({'pathname': pathname})
            response = self.request(
                url, 'GET', **{'headers': self.headers, 'params': params})
            if not response:
                logger.error(
                    "Not response retrieved.")

        return response.json() if response else {}
