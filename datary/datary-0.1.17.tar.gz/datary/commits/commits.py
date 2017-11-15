
# -*- coding: utf-8 -*-
"""
Datary sdk Commits File
"""
import os

from datetime import datetime
from urllib.parse import urljoin
from datary.operations import DataryOperations
from scrapbag import nested_dict_to_list

import structlog

logger = structlog.getLogger(__name__)


class DataryCommits(DataryOperations):
    """
    Datary Commits class.
    """
    COMMIT_ACTIONS = {'add': '+', 'update': 'm', 'delete': '-'}

    def commit(self, repo_uuid, commit_message):
        """
        Commits changes.

        ================  =============   ====================================
        Parameter         Type            Description
        ================  =============   ====================================
        repo_uuid         int             repository uuid
        commit_message    str             message commit description
        ================  =============   ====================================

        """
        logger.info("Commiting changes...")

        url = urljoin(self.URL_BASE,
                      "repos/{}/commits".format(repo_uuid))

        response = self.request(
            url,
            'POST',
            **{'data': {'message': commit_message}, 'headers': self.headers})
        if response:
            logger.info("Changes commited", commit_message=commit_message)

    def recollect_last_commit(self, repo=None):
        """
        Parameter:
            (dict) repo

        Raises:
            - No repo found with given uuid.
            - No sha1 in repo.
            - No filetree in repo.
            - Fail retrieving last commit.

        Returns:
            Last commit in list with the path, basename, sha1.

        """
        if repo is None:
            repo = {}

        ftree = {}
        last_commit = []
        filetree_matrix = []

        try:

            # retrieve last filetree commited
            ftree = self.get_last_commit_filetree(repo)

            # List of Path | basename | Sha1
            filetree_matrix = nested_dict_to_list("", ftree)

            # Take metadata to retrieve sha-1 and compare with
            for path, basename, dataset_uuid in filetree_matrix:
                metadata = self.get_metadata(
                    repo_uuid=repo.get('uuid'),
                    dataset_uuid=dataset_uuid)

                # append format path | basename | data (not required) | sha1
                last_commit.append(
                    (path, basename, None, metadata.get("sha1")))
        except Exception:
            logger.warning(
                "Fail recollecting last commit",
                repo=repo,
                ftree={},
                last_commit=[])

        return last_commit

    def get_last_commit_filetree(self, repo=None):
        """
        Datary get_last_commit_filetree
        """
        if repo is None:
            repo = {}
        ftree = {}

        try:
            # check if have the repo.
            if 'apex' not in repo:
                repo.update(self.get_describerepo(repo.get('uuid')))

            if not repo:
                logger.info('No repo found with this uuid', repo=repo)
                raise Exception(
                    "No repo found with uuid {}".format(repo.get('uuid')))

            last_sha1 = repo.get("apex", {}).get("commit")

            if not last_sha1:
                logger.info('Repo hasnt any sha1 in apex', repo=repo)
                raise Exception(
                    'Repo hasnt any sha1 in apex {}'.format(repo))

            ftree = self.get_commit_filetree(
                repo.get('uuid'), last_sha1)

            if not ftree:
                logger.info('No ftree found with repo_uuid',
                            repo=repo, sha1=last_sha1)
                raise Exception(
                    "No ftree found with repo_uuid {} , last_sha1 {}".
                    format(repo.get('uuid'), last_sha1))

        except Exception as ex:
            logger.warning(
                "Fail getting last commit - {}".format(ex), repo=repo)

        return ftree

    @classmethod
    def make_index(cls, lista):
        """
        Transforms commit list into an index using path + basename as key
        and sha1 as value.

        ================  =============   ====================================
        Parameter         Type            Description
        ================  =============   ====================================
        lista             list            list of commits
        ================  =============   ====================================

        """
        result = {}
        for path, basename, data, sha1 in lista:
            result[os.path.join(path, basename)] = {'path': path,
                                                    'basename': basename,
                                                    'data': data,
                                                    'sha1': sha1}
        return result

    def compare_commits(self, last_commit, actual_commit,
                        strict=True, **kwargs):
        """
        Compare two commits and retrieve hot elements to change
        and the action to do.

        ================  =============   ====================================
        Parameter         Type            Description
        ================  =============   ====================================
        last_commit       list            [path|basename|sha1]
        actual_commit     list            [path|basename|sha1]
        strict            Boolean         Default is True
        ================  =============   ====================================

        Returns:
            Difference between both commits.

        Raises:
            Fail comparing commits.

        """
        difference = {'update': [], 'delete': [], 'add': []}

        try:
            # make index
            last_index = self.make_index(last_commit)
            actual_index = self.make_index(actual_commit)

            last_index_keys = list(last_index.keys())

            for key, value in actual_index.items():

                # Update
                if key in last_index_keys:
                    last_index_sha1 = last_index.get(key, {}).get('sha1')
                    # sha1 values don't match
                    if value.get('sha1') != last_index_sha1:
                        difference['update'].append(value)

                    # Pop last inspected key
                    last_index_keys.remove(key)

                # Add
                else:
                    difference['add'].append(value)

            # Remove elements when stay in last_commit and not in actual if
            # stric is enabled else omit this
            difference['delete'] = [last_index.get(
                key, {}) for key in last_index_keys if strict]

        except Exception as ex:
            logger.error(
                'Fail comparing commits - {}'.format(ex),
                last_commit=last_commit, actual_commit=actual_commit)

        return difference

    def operation_commit(
            self, wdir_uuid, last_commit, actual_commit, **kwargs):
        """
        Given the last commit and actual commit,
        takes hot elements to ADD, UPDATE or DELETE.

        ================  =============   =======================
        Parameter         Type            Description
        ================  =============   =======================
        wdir_uuid         str             working directory uuid
        last_commit       list            [path|basename|sha1]
        actual_commit     list            [path|basename|sha1]
        ================  =============   =======================

        """
        # compares commits and retrieves hot elements -> new, modified, deleted
        hot_elements = self.compare_commits(
            last_commit, actual_commit, strict=kwargs.get('strict', False))

        logger.info(
            "There are hot elements to commit ({} add; {} update; {} delete;"
            .format(
                len(hot_elements.get('add')),
                len(hot_elements.get('update')),
                len(hot_elements.get('delete'))))

        for element in hot_elements.get('add', []):
            super(DataryCommits, self).add_file(
                wdir_uuid, element)

        for element in hot_elements.get('update', []):
            super(DataryCommits, self).modify_file(
                wdir_uuid, element, **kwargs)

        for element in hot_elements.get('delete', []):
            super(DataryCommits, self).delete_file(
                wdir_uuid, element)

    def commit_diff_tostring(self, difference):
        """
        Turn commit comparation done to visual print format.

        Returns:
            (str) result: ([+|u|-] filepath/basename)

        Raises:
            Fail translating commit differences to string

        """
        result = ""

        if difference:
            try:
                result = "Changes at {}\n".format(
                    datetime.now().strftime("%d/%m/%Y-%H:%M"))
                for action in sorted(list(self.COMMIT_ACTIONS.keys())):
                    result += "{}\n*****************\n".format(action.upper())
                    for commit_data in difference.get(action, []):
                        result += "{}  {}/{}\n".format(
                            self.COMMIT_ACTIONS.get(action, '?'),
                            commit_data.get('path'),
                            commit_data.get('basename'))
            except Exception as ex:
                msg = 'Fail translating commit differences to string - {}'
                logger.error(msg.format(ex))

        return result
