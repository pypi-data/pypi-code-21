# -*- coding: utf-8 -*-
"""
Datary sdk Remove Operations File
"""
import os

from urllib.parse import urljoin
from datary.auth import DataryAuth
from datary.operations.limits import DataryOperationLimits

import structlog

logger = structlog.getLogger(__name__)


class DataryRemoveOperation(DataryAuth, DataryOperationLimits):
    """
    Datary RemoveOperation module class
    """

    def delete_dir(self, wdir_uuid, path, basename):
        """
        Delete directory.
        -- NOT IN USE --

        ================  =============   ====================================
        Parameter         Type            Description
        ================  =============   ====================================
        wdir_uuid         str             working directory uuid
        path              str             path to directory
        basename           str             directory name
        ================  =============   ====================================

        """
        logger.info(
            "Delete directory in workdir.",
            wdir_uuid=wdir_uuid,
            basename=basename,
            path=os.path.join(path, basename))

        url = urljoin(self.URL_BASE,
                      "workdirs/{}/changes".format(wdir_uuid))

        payload = {"action": "delete",
                   "filemode": 40000,
                   "basename": path,
                   "basename": basename}

        response = self.request(
            url, 'GET', **{'data': payload, 'headers': self.headers})

        if response:
            logger.info(
                "Directory has been deleted in workdir",
                wdir_uuid=wdir_uuid,
                url=url,
                basename=basename,
                path=path,
                payload=payload)

    def delete_file(self, wdir_uuid, element):
        """
        Delete file.

        ================  =============   ====================================
        Parameter         Type            Description
        ================  =============   ====================================
        wdir_uuid         str             working directory uuid
        element           Dic             element with path & basename
        ================  =============   ====================================

        """
        logger.info(
            "Delete file in workdir.",
            element=element,
            wdir_uuid=wdir_uuid)

        url = urljoin(self.URL_BASE,
                      "workdirs/{}/changes".format(wdir_uuid))

        payload = {
            "action": "remove",
            "filemode": 100644,
            "basename": element.get('path'),
            "basename": element.get('basename')
        }

        response = self.request(
            url, 'POST', **{'data': payload, 'headers': self.headers})
        if response:
            logger.info("File has been deleted.")

    def delete_inode(self, wdir_uuid, inode):
        """
        Delete using inode.

        ================  =============   ====================================
        Parameter         Type            Description
        ================  =============   ====================================
        wdir_uuid         str             working directory uuid
        inode             str             directory or file inode.
        ================  =============   ====================================
        """
        logger.info("Delete by inode.", wdir_uuid=wdir_uuid, inode=inode)

        url = urljoin(self.URL_BASE,
                      "workdirs/{}/changes".format(wdir_uuid))

        payload = {"action": "remove", "inode": inode}

        response = self.request(
            url, 'POST', **{'data': payload, 'headers': self.headers})

        if response:
            logger.info("Element has been deleted using inode.")

    def clear_index(self, wdir_uuid):
        """
        Clear changes in repo.

        ================  =============   ====================================
        Parameter         Type            Description
        ================  =============   ====================================
        wdir_uuid         str             working directory uuid
        ================  =============   ====================================
        """

        url = urljoin(self.URL_BASE,
                      "workdirs/{}/changes".format(wdir_uuid))

        response = self.request(url, 'DELETE', **{'headers': self.headers})
        if response:
            logger.info("Repo index has been cleared.")
            return True

        return False
