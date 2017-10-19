# coding=utf-8
import json
from ..backend_mixin import BackendMixin
from .base_metadata_db import BaseMetadataDB


class BackendMetadataDB(BackendMixin, BaseMetadataDB):
    def __init__(self, connection, config, handle_api):
        super(BackendMetadataDB, self).__init__(connection, config, handle_api)

    def _create_table(self):
        pass

    def _query_head_data(self, sha_list):
        with self._connection.get_cursor() as session:
            url = 'data_volumes/%s/metadata/head' % self._volume_id
            msg = {
                'sha': sha_list,
            }

            result = self._handle_api(self._config, session.post, url, msg)

            for data_json in result.get('metadata_json', []):
                yield json.loads(data_json)

    def _add_missing_columns(self, data_object):
        raise NotImplementedError(self._add_missing_columns)

    def get_data_for_commit(self, sha, commit_sha):
        raise NotImplementedError(self.get_data_for_commit)

    def _add_data(self, flatten_data_list):
        raise NotImplementedError(self._add_data)

    def commit(self, commit_sha, tree_id):
        raise NotImplementedError(self.commit)

    def _query(self, sql_vars, select_fields, where):
        raise NotImplementedError(self._query)

    def get_all_data(self, sha):
        raise NotImplementedError(self.get_all_data)
