# -*- coding: utf-8 -*-
"""
Datary Repos File.
"""
from urllib.parse import urljoin
from datary.auth import DataryAuth
from datary.categories import DataryCategories

import structlog

logger = structlog.getLogger(__name__)


class DataryRepos(DataryAuth):
    """
    Datary repos module class.
    """

    DATARY_REPO_VISIBILITY = ['public', 'private', 'commercial']

    def create_repo(self, repo_name=None, repo_category='other', **kwargs):
        """
        Creates repository using Datary's Api

        ==============  =============   ======================================
        Parameter       Type            Description
        ==============  =============   ======================================
        repo_name       str             repo name,
        repo_category   str             repo category name.
        description     str             repo description info.
        visibility      str             public, private, commercial.
        licenseName     str             repo license.
        amount          int             price of the repo in cents if
                                         commertial.
        currency        str             currency (by default "eur").
        modality        str             "one-time" | "recurring" (by default)
        interval        str             "day" | "week" | "month" | "year" (by
                                         default).
        period          int             number of interval between billing (by
                                         default 1).
        ==============  =============   ======================================

        Returns:
            (dict) created repository's description

        """

        if not kwargs.get('repo_uuid'):
            url = urljoin(self.URL_BASE, "me/repos")
            visibility = kwargs.get('visibility', 'commercial')

            cat_condition = repo_category in DataryCategories.DATARY_CATEGORIES
            visibility_condition = visibility in self.DATARY_REPO_VISIBILITY

            payload = {
                'name': repo_name,
                'category':
                    repo_category if cat_condition else 'other',

                'description': kwargs.get(
                    'description',
                    '{} description'.format(repo_name)),

                'visibility':
                    visibility if visibility_condition else 'commercial',

                'licenseName': kwargs.get('license', 'proprietary'),
                'amount': kwargs.get('amount'),
                'currency':  kwargs.get('currency', 'eur'),
                'modality': kwargs.get('modality', 'recurring'),
                'interval': kwargs.get('interval', 'year'),
                'period': kwargs.get('period', 1),
                # 'defaultInitialization': kwargs.get('initialization', False)
            }

            # Create repo request.
            _response = self.request(
                url, 'POST', **{'data': payload, 'headers': self.headers})

        describe_response = self.get_describerepo(
            repo_name=repo_name, **kwargs)
        return describe_response if describe_response else {}

    def get_describerepo(self, repo_uuid=None, repo_name=None):
        """
        ==============  =============   ====================================
        Parameter       Type            Description
        ==============  =============   ====================================
        repo_uuid       str             repository uuid
        repo_name       str             repository name
        ==============  =============   ====================================

        Returns:
            (list or dict) repository with the given repo_uuid.

        """
        logger.info("Getting Datary user repo and wdir uuids")
        url = urljoin(
            self.URL_BASE,
            "repos/{}".format(repo_uuid) if repo_uuid else "me/repos")

        response = self.request(url, 'GET', **{'headers': self.headers})

        repos_data = response.json() if response else {}
        repo = {}

        if isinstance(repos_data, list) and (repo_uuid or repo_name):
            for repo_data in repos_data:
                if repo_uuid and repo_data.get('uuid') == repo_uuid:
                    repo = repo_data
                    break

                elif repo_name and repo_data.get('name') == repo_name:
                    repo = repo_data
                    break
        else:
            repo = repos_data

        return repo

    def delete_repo(self, repo_uuid=None):
        """
        Deletes repo using Datary's Api

        ==============  =============   ====================================
        Parameter       Type            Description
        ==============  =============   ====================================
        repo_uuid       str              repository uuid
        repo_name       str             repository name
        ==============  =============   ====================================

        Raises:
            No repo id error

        """
        logger.info("Deleting Datary user repo")

        if not repo_uuid:
            raise ValueError('Must pass the repo uuid to delete the repo.')

        url = urljoin(self.URL_BASE, "repos/{}".format(repo_uuid))
        response = self.request(url, 'DELETE', **{'headers': self.headers})

        return response.text if response else None
