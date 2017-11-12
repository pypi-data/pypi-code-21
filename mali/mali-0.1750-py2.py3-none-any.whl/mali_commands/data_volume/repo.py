# coding=utf-8
import logging
import os

import requests

from mali_commands.legit.dulwich import objects
from mali_commands.legit.dulwich.repo import Repo
from mali_commands.commons import handle_api
from mali_commands.data_volume_config import DataVolumeConfig
from mali_commands.legit import MySqlConnection, SqliteConnection, SpannerConnection, BigQueryConnection, \
    DatastoreConnection, BackendConnection
from mali_commands.legit import GCSObjectStore, NullObjectStore, BackendGCSObjectStore
from mali_commands.legit import SqliteMLIndex, MySqlMLIndex, SpannerMLIndex, BigQueryMLIndex, BackendMLIndex
from mali_commands.legit import BackendMetadataDB, SqliteMetadataDB, MySqlMetadataDB, SpannerMetadataDB, BigQueryMetadataDB
from mali_commands.legit import MySqlRefsContainer, SpannerRefContainer, DatastoreRefContainer, \
    BackendRefContainer


class MLIgnoreFilterManager(object):
    def is_ignored(self, relpath):
        return False


DEFAULT_ENCODING = 'utf-8'


def make_bytes(c):
    if not isinstance(c, bytes):
        return c.encode(DEFAULT_ENCODING)

    return c


class MlRepo(Repo):
    def __init__(self, config, repo_root, read_only=False):
        self.__data_volume_config = DataVolumeConfig(repo_root)

        self.__in_transactions = False
        self.__config = config
        self.__connections = {}
        self.__read_only = read_only
        self.__metadata = None

        super(MlRepo, self).__init__(repo_root, self.data_volume_config.data_path)

    @property
    def _config(self):
        return self.__config

    def close(self):
        for connection in self.__connections.values():
            connection.close()

        super(MlRepo, self).close()

    __connection_class_mapping = {
        'sqlite': SqliteConnection,
        'mysql': MySqlConnection,
        'spanner': SpannerConnection,
        'bq': BigQueryConnection,
        'datastore': DatastoreConnection,
    }

    def __create_connection(self, name, **kwargs):
        kwargs.update(self.data_volume_config.db_config)
        kwargs['read_only'] = self.__read_only
        kwargs['data_volume_config'] = self.data_volume_config
        kwargs['user_id'] = self._config.user_id if self._config is not None else None

        connection_class = self.__connection_class_mapping.get(self.data_volume_config.db_type, BackendConnection)

        return connection_class(**kwargs)

    def start_transactions(self):
        for connection in self.__connections.values():
            connection.start_transactions()

        self.__in_transactions = True

    def end_transactions(self):
        for connection in self.__connections.values():
            connection.end_transactions()

        self.__in_transactions = False

    def rollback_transactions(self):
        for connection in self.__connections.values():
            connection.rollback_transactions()

        self.__in_transactions = False

    def _connection_by_name(self, name, **kwargs):
        if name not in self.__connections:
            connection = self.__create_connection(name, **kwargs)

            if self.__in_transactions:
                connection.start_transactions()

            self.__connections[name] = connection

        return self.__connections[name]

    def __create_metadata(self):
        if self.data_volume_config.db_type == 'sqlite':
            metadata_path = os.path.join(self.repo_root, 'metadata.db')
            return SqliteMetadataDB(self._connection_by_name('metadata', path=metadata_path))
        elif self.data_volume_config.db_type == 'mysql':
            return MySqlMetadataDB(self._connection_by_name('main'))
        elif self.data_volume_config.db_type == 'spanner':
            return SpannerMetadataDB(self._connection_by_name('main'))
        elif self.data_volume_config.db_type == 'bq':
            return BigQueryMetadataDB(self._connection_by_name('metadata'))

        return BackendMetadataDB(self._connection_by_name('metadata'), self._config, handle_api)

    @property
    def metadata(self):
        if self.__metadata is None:
            self.__metadata = self.__create_metadata()

        return self.__metadata

    @property
    def data_volume_config(self):
        return self.__data_volume_config

    def open_index(self):
        if self.data_volume_config.db_type == 'sqlite':
            index_file_name = self.index_path()

            pre, ext = os.path.splitext(index_file_name)

            index_file_name = pre + '.db'

            return SqliteMLIndex(self._connection_by_name('index', path=index_file_name))

        if self.data_volume_config.db_type == 'mysql':
            return MySqlMLIndex(self._connection_by_name('main'))

        if self.data_volume_config.db_type == 'spanner':
            return SpannerMLIndex(self._connection_by_name('main'))

        if self.data_volume_config.db_type == 'bq':
            return BigQueryMLIndex(self._connection_by_name('main'))

        return BackendMLIndex(self._connection_by_name('main'), self._config, handle_api)

    def create_ref_container(self):
        if self.data_volume_config.object_store_type == 'disk':
            return super(MlRepo, self).create_ref_container()

        if self.data_volume_config.db_type == 'mysql':
            MySqlRefsContainer(self._connection_by_name('main'))

        if self.data_volume_config.db_type == 'spanner':
            return SpannerRefContainer(self._connection_by_name('main'))

        if self.data_volume_config.db_type == 'bq':
            return DatastoreRefContainer(self._connection_by_name('datastore'))

        return BackendRefContainer(self._connection_by_name('main'), self._config, handle_api)

    def create_object_store(self):
        if self.data_volume_config.object_store_type == 'disk':
            return super(MlRepo, self).create_object_store()

        if self.data_volume_config.object_store_type == 'null':
            return NullObjectStore()

        bucket_name = self.data_volume_config.object_store_config.get('bucket_name')

        processes = self.data_volume_config.object_store_config.get('processes', -1)

        if bucket_name is None:
            return BackendGCSObjectStore(
                self._connection_by_name('backend'), self._config, handle_api, processes=processes)

        return GCSObjectStore(self._connection_by_name('gcs'), processes=processes)

    def get_config_stack(self):
        return DataVolumeConfig(self.repo_root)

    def get_ignore_filter_manager(self):
        return MLIgnoreFilterManager()

    def _get_user_identity(self):
        import jwt

        data = jwt.decode(self._config.id_token, verify=False) if self.__config.id_token else {}

        return '{name} <{email}>'.format(**data).encode('utf8')

    def has_change_set(self, ref='HEAD'):
        ref = ref.encode('ascii')

        try:
            ref_sha = self.refs[ref]

            head_tree_sha = self[ref_sha].tree
        except KeyError:  # in case of empty tree
            head_tree_sha = objects.Tree().id

        index = self.open_index()

        commit_id = index.get_commit_id()

        return None if commit_id == head_tree_sha else commit_id

    def remote_commit(self, message):
        msg = {
            'message': message,
        }

        url = "data_volumes/{volume_id}/commit".format(volume_id=self.data_volume_config.volume_id)

        return handle_api(self._config, requests.post, url, msg)

    def local_commit(self, message):
        tree_id = self.has_change_set()

        if not tree_id:
            return

        self.start_transactions()
        try:
            commit_hash = self.do_commit(message=make_bytes(message), tree=tree_id).decode('ascii')

            self.metadata.commit(commit_hash, tree_id)

            self.end_transactions()
        except Exception:
            logging.exception('failure doing commit, preforming rollback')
            self.rollback_transactions()
            raise

    def commit(self, message):
        if self.data_volume_config.is_local:
            return self.local_commit(message)

        return self.remote_commit(message)
