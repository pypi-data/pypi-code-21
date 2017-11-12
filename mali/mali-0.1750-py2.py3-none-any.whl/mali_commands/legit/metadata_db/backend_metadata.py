# coding=utf-8
import json
from ..backend_mixin import BackendMixin
from .base_metadata_db import BaseMetadataDB
from six.moves.urllib.parse import urlencode


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

            for data_item in result.get('metadata_json') or []:
                yield json.loads(data_item)

    def _add_missing_columns(self, data_object):
        pass

    def get_data_for_commit(self, sha, commit_sha):
        raise NotImplementedError(self.get_data_for_commit)

    def _add_data(self, flatten_data_list):
        with self._connection.get_cursor() as session:
            url = 'data_volumes/%s/metadata/head/add' % self._volume_id

            items = []
            for flatten_data_item in flatten_data_list:
                del flatten_data_item['@version']
                del flatten_data_item['@commit_sha']

                sha = flatten_data_item['@sha']
                del flatten_data_item['@sha']

                item = {
                    'sha': sha,
                    'metadata_json': json.dumps(flatten_data_item),
                }

                items.append(item)

            msg = {
                'items': items,
            }

            return self._handle_api(self._config, session.post, url, msg)

    def query(self, query_text, max_results, start_index):
        def _iter_data():
            for data_point in result.get('data_points') or []:
                result_data_point = {
                    'path': data_point['path'],
                    'id': data_point['id'],
                    'phase': data_point.get('phase'),
                    'version': data_point['version'],
                }

                for key in data_point['meta']:
                    result_data_point[key['key']] = key.get('val')

                yield result_data_point

        with self._connection.get_cursor() as session:
            version_query = query_text if query_text else 'version:head'

            params = {
                'query': version_query
            }

            if max_results:
                params['max_results'] = max_results

            if start_index:
                params['start_index'] = start_index

            url = 'data_volumes/%s/query/?%s' % (self._volume_id, urlencode(params))

            result = self._handle_api(self._config, session.get, url)

            return _iter_data(), int(result.get('total_data_points', 0))

    def _query(self, sql_vars, select_fields, where, max_results, start_index):
        raise NotImplementedError(self._query)

    def get_all_data(self, sha):
        raise NotImplementedError(self.get_all_data)

    def end_commit(self):
        raise NotImplementedError(self.end_commit)

    def begin_commit(self, commit_sha, tree_id):
        raise NotImplementedError(self.begin_commit)
