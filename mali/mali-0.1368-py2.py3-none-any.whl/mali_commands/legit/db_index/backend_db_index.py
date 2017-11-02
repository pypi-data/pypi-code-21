# coding=utf-8
from .base_db_index import BaseMLIndex
from ..backend_mixin import BackendMixin


class BackendMLIndex(BackendMixin, BaseMLIndex):
    def __init__(self, connection, config, handle_api):
        super(BackendMLIndex, self).__init__(connection, config, handle_api)

    def _create_table_if_needed(self):
        pass

    def set_entries(self, entries):
        if not entries:
            return

        rows = []
        for name, sha, ctime, mtime, mode, uid, gid, size, url in self._decode_entries(entries):
            row = {
                'name': name,
                'sha': sha,
                'ctime': ctime,
                'mtime': mtime,
                'mode': mode,
                'uid': uid,
                'gid': gid,
                'size': size,
                'url': url
            }

            rows.append(row)

        with self._connection.get_cursor() as session:
            url = 'data_volumes/%s/index/stage' % self._volume_id
            msg = {
                'entries': rows,
            }

            self._handle_api(self._config, session.post, url, msg)

    def get_commit_id(self):
        with self._connection.get_cursor() as session:
            url = 'data_volumes/%s/index/stage/commit_id' % self._volume_id
            result = self._handle_api(self._config, session.get, url)

            return result['commit_id']

    def begin_commit(self, tree_id):
        raise NotImplementedError(self.begin_commit)

    def end_commit(self):
        raise NotImplementedError(self.end_commit)
