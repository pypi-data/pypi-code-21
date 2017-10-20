# -*- coding: utf-8 -*-
"""
Datary sdk Add Operations File
"""
from urllib.parse import urljoin
from datary.auth import DataryAuth
from datary.operations.limits import DataryOperationLimits
import structlog

logger = structlog.getLogger(__name__)


class DataryRenameOperation(DataryAuth, DataryOperationLimits):
    """
    Datary RenameOperation module class
    """

    def rename_file(self, wdir_uuid, element, new_element):
        """
        Rename file filepath.

        ================  =============   ====================================
        Parameter         Type            Description
        ================  =============   ====================================
        wdir_uuid         str             working directory uuid
        element           dict            element with path & basename
        new_element       dict            element with new path & basename
        ================  =============   ====================================

        """
        logger.info(
            "Rename file in workdir.",
            element=element,
            new_element=new_element,
            wdir_uuid=wdir_uuid)

        url = urljoin(self.URL_BASE, "workdirs/{}/changes".format(wdir_uuid))

        new_pathname = "{}/{}".format(
            new_element.get('path', element.get('path')),
            new_element.get('basename', element.get('basename')))

        payload = {
            "action": "rename",
            "dirname": element.get('path'),
            "basename": element.get('basename'),
            "newPathname": new_pathname,
        }

        response = self.request(
            url, 'POST', **{'data': payload, 'headers': self.headers})
        if response:
            logger.info("File has been renamed.", new_path=new_pathname)
