
# -*- coding: utf-8 -*-
"""
Datary sdk clean Operations File
"""

from datary.repos import DataryRepos
from datary.filetrees import DataryFiletrees
from datary.operations.remove import DataryRemoveOperation
from datary.operations.limits import DataryOperationLimits
from scrapbag import flatten

import structlog

logger = structlog.getLogger(__name__)


class DataryCleanOperation(DataryRemoveOperation, DataryFiletrees,
                           DataryOperationLimits):
    """
    Datary clean operation class
    """
    def clean_repo(self, repo_uuid, **kwargs):
        """
        Clean repo data from datary & algolia.

        ================  =============   ====================================
        Parameter         Type            Description
        ================  =============   ====================================
        repo_uuid         str             repository uuid
        ================  =============   ====================================
        """
        repo = DataryRepos.get_describerepo(repo_uuid=repo_uuid, **kwargs)

        if repo:
            wdir_uuid = repo.get('workdir', {}).get('uuid')

            # clear changes
            self.clear_index(wdir_uuid)

            # get filetree
            filetree = self.get_wdir_filetree(wdir_uuid)

            # flatten filetree to list
            flatten_filetree = flatten(filetree, sep='/')

            filetree_keys = [
                x for x in flatten_filetree.keys() if '__self' not in x]

            # Delete files
            for path in filetree_keys:
                element_data = {
                    'path': "/".join(path.split('/')[:-1]),
                    'basename': path.split('/')[-1]
                }

                self.delete_file(wdir_uuid, element_data)
                logger.info(
                    'cleaning remove of {}'.format(path),
                    element_data=element_data)

        else:
            logger.error('Fail to clean_repo, repo not found in datary.')
