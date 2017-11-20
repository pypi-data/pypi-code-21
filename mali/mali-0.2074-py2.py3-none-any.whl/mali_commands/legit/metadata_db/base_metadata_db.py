# coding=utf-8
import copy
import logging
from abc import ABCMeta, abstractmethod
import six
import sys

from ..connection_mixin import ConnectionMixin
from ..scam import parse_query, tree_to_sql_parts, get_split_vars


class MetadataOperationError(Exception):
    pass


class MetadataTypeNotSupported(MetadataOperationError):
    pass


def unicode_dict_to_str(d):
    if sys.version_info >= (3, 0):
        return d

    for key, val in d.items():
        if not isinstance(val, unicode):
            continue

        d[key] = val.encode('utf8')

    return d


class BaseMetadataDB(ConnectionMixin):
    __metaclass__ = ABCMeta

    STAGING_COMMIT = 'staging'
    DEFAULT_SEED = 1337
    DEFAULT_SPLIT = (('train', 0.6), ('test', 0.2), ('validation', 0.2))

    def __init__(self, connection, **kwargs):
        super(BaseMetadataDB, self).__init__(connection)
        self.__rnd = None
        self.__prev_table_info = None

        self.__create_table_if_needed()

    @abstractmethod
    def _create_table(self):
        """

        :return:
        """

    @abstractmethod
    def _add_missing_columns(self, data_object):
        """

        :param data_object:
        :return:
        """

    @abstractmethod
    def _add_data(self, flatten_data_list):
        """

        :param flatten_data_list:
        :return:
        """

    @abstractmethod
    def get_data_for_commit(self, sha, commit_sha):
        """

        :param sha:
        :param commit_sha:
        :return:
        """

    @abstractmethod
    def get_all_data(self, sha):
        """

        :param sha:
        :return:
        """

    @abstractmethod
    def begin_commit(self, commit_sha, tree_id):
        """

        :param commit_sha:
        :param tree_id:
        :return:
        """

    @abstractmethod
    def end_commit(self):
        """

        :param commit_sha:
        :param tree_id:
        :return:
        """

    @abstractmethod
    def _query(self, sql_vars, select_fields, where, max_results, start_index):
        """

        :param sql_vars:
        :param select_fields:
        :param where:
        :return:
        """

    @abstractmethod
    def _query_head_data(self, sha_list):
        """

        :param sha_list:
        :return: list
        """

        return []

    def __create_table_if_needed(self):
        if self._connection.read_only:
            return

        self._create_table()

    def add_data(self, data):
        if not data:
            logging.debug('no data provided')
            return

        if not isinstance(data, list):
            data = [data]

        logging.debug('add data (total: %s)', len(data))

        data_list = []
        for sha, data_object in data:
            data_object_clone = copy.deepcopy(data_object)

            self._add_missing_columns(data_object)

            data_object_clone['@sha'] = sha
            data_object_clone['@commit_sha'] = self.STAGING_COMMIT
            data_object_clone['@version'] = 2 ** 32 - 1
            data_object_clone['@hash'] = None

            data_list.append(data_object_clone)

        self._add_data(data_list)

    def explicit_query(self, query_text):
        tree = parse_query(query_text)
        sql_vars, _ = tree_to_sql_parts(tree, self._connection.create_sql_helper())

        sql_vars = sql_vars or {}

        if 'seed' not in sql_vars:
            query_text += ' seed:%s' % self.DEFAULT_SEED

        return query_text

    def query(self, query_text, max_results, start_index):
        if query_text is not None and not isinstance(query_text, str):
            query_text = query_text.encode('utf8')

        tree = parse_query(query_text)
        sql_vars, where = tree_to_sql_parts(tree, self._connection.create_sql_helper())

        select_fields = ['*']

        sql_vars = sql_vars or {}

        if 'seed' not in sql_vars:
            sql_vars['seed'] = self.DEFAULT_SEED

        if 'phase_train_start' not in sql_vars:
            sql_vars.update(get_split_vars(self.DEFAULT_SPLIT))

        return self._query(sql_vars, select_fields, where, max_results, start_index)

    @classmethod
    def fill_in_vars(cls, query_sql, sql_vars):
        for var_name, var_value in sql_vars.items():
            query_sql = query_sql.replace('$' + var_name, str(var_value))

        return query_sql

    def get_head_data(self, sha_list):
        if isinstance(sha_list, six.string_types):
            sha_list = [sha_list]

        return self._query_head_data(sha_list)

    def _return_all_result_from_query(self, query_sql, batch_size=1000):
        from flatten_json import unflatten

        with self._connection.get_cursor() as c:
            c.execute(query_sql)

            while True:
                results = c.fetchmany(batch_size)
                if not results:
                    break

                for result in results:
                    yield unflatten(unicode_dict_to_str(result), separator='.')
