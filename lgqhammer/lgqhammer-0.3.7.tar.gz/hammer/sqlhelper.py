# -*- coding=utf-8 -*-

import logging
import pymysql

from hammer.pymysqlpool import ConnectionPool

logger = logging.getLogger('sqlhelper')


# db_config_temp
# db_config = {
#     'pool_name': 'test',
#     'host': 'localhost',
#     'port': 3306,
#     'user': 'root',
#     'password': '123456',
#     'database': 'test',
#     'pool_resize_boundary': 2,
#     'enable_auto_resize': True,
#     'max_pool_size': 1
# }

class SqlHelper(object):
    def __init__(self, **db_config):
        self._pool = self._conn_pool(**db_config)
        self.db_config = db_config
        self.db_name = db_config.get('database', None)

    def _conn_pool(self, **db_config):
        pool = ConnectionPool(**db_config)
        return pool

    def create_db(self, db_name):
        try:
            command = 'CREATE DATABASE IF NOT EXISTS %s DEFAULT CHARACTER SET \'utf8\' ' % db_name
            with self._pool.connection() as conn:
                conn.cursor().execute(command)
                conn.commit()
            return True
        except Exception as e:
            logger.exception('sql helper create_database exception:%s' % str(e))
            return False

    def create_table(self, command):
        try:
            with self._pool.connection() as conn:
                conn.cursor().execute(command)
                conn.commit()
            return True
        except Exception as e:
            logger.exception('sql helper create_table exception:%s' % str(e))
            return False

    def insert_data(self, command, data, commit = False):
        try:
            with self._pool.connection() as conn:
                conn.cursor().execute(command, data)
                if commit:
                    conn.commit()
            return True
        except Exception as e:
            logger.exception('sql helper insert_data exception msg:%s' % e, logging.WARNING)
            return False

    def insert_json(self, data = {}, table_name = None, commit = False):
        try:
            keys = []
            vals = []
            for k, v in data.items():
                keys.append(k)
                vals.append(v)
            val_str = ','.join(['%s'] * len(vals))
            key_str = ','.join(keys)

            command = "INSERT IGNORE INTO {table} ({keys}) VALUES({values})". \
                format(keys = key_str, values = val_str, table = table_name)
            with self._pool.connection() as conn:
                conn.cursor().execute(command, tuple(vals))
                if commit:
                    conn.commit()
            return True
        except Exception as e:
            logger.exception('sql helper insert_json exception msg:%s' % e)
            return False

    def insert_json_list(self, datas, table_name = None, commit = False):
        try:
            if len(datas) < 0:
                return
            data = datas[0]
            keys = list(data.keys())
            values = [list(data.values()) for data in datas]

            return self.insert_list(keys, values, table_name, commit)
        except Exception as e:
            logger.exception('sql helper insert_json_list exception msg:%s' % e)
            return False

    # keys = ['name', 'age'] values = [('liu', 10), ('guang', 20'), ('quan', 30)]
    def insert_list(self, keys, values, table_name = None, commit = False):
        try:
            key_param = ','.join(keys)
            val_param = ','.join(['%s'] * len(keys))

            command = "INSERT IGNORE INTO {table_name} ({keys}) values({val})". \
                format(table_name = table_name, keys = key_param, val = val_param)
            with self._pool.connection() as conn:
                conn.cursor().executemany(command, values)
                if commit:
                    conn.commit()
        except Exception as e:
            logger.exception('sql helper insert_json exception msg:%s' % e)
            return False

    def insert_data_list(self, keys, datas, table_name = None, commit = False):
        if len(keys) <= 0 or len(datas) <= 0:
            return False

        try:
            val_param = ''
            for i, d in enumerate(datas):
                value = '('
                for j, k in enumerate(keys):
                    v = d.get(k, None)
                    if v is not None:
                        value = value + '\'' + str(v) + '\''
                    else:
                        value = value + 'NULL'
                    if j < len(keys) - 1:
                        value = value + ','
                if i < len(datas) - 1:
                    value = value + '),'
                else:
                    value = value + ');'

                val_param = val_param + value

            key_param = ','.join(keys)
            command = "INSERT IGNORE INTO {table_name} ({keys}) values {val}". \
                format(table_name = table_name, keys = key_param, val = val_param)

            with self._pool.connection() as conn:
                conn.cursor().execute(command)
                if commit:
                    conn.commit()
            return True
        except Exception as e:
            logger.exception('sql helper insert_data_list exception msg:%s' % e)
            return False

    def update_json(self, datas, condition, table_name = None, commit = False, ):
        try:
            fields = ''
            for i, (key, val) in enumerate(datas.items()):
                fields += '{key}=\'{val}\''.format(key = key, val = val)
                if i < len(datas.items()) - 1:
                    fields += ','

            cond_str = ''
            for i, (key, val) in enumerate(condition.items()):
                cond_str = '{key}={val}'.format(key = key, val = val)
                if i < len(condition.items()) - 1:
                    cond_str += ' and '

            command = '''UPDATE {table_name} SET {fields} WHERE {condition};'''.format(
                table_name = table_name, fields = fields, condition = cond_str)

            with self._pool.connection() as conn:
                conn.cursor().execute(command)
                if commit:
                    conn.commit()
        except Exception as e:
            logging.exception('sql helper update_json exception msg:%s' % e)

    def select_db(self, db_name):
        self._pool.select_db(db_name)
        self.db_name = db_name

    def commit(self):
        for conn in self._pool:
            conn.commit()

    def close(self):
        self._pool.close()

    def execute(self, command, commit = True):
        try:
            with self._pool.connection() as conn:
                conn.cursor().execute(command)
                if commit:
                    conn.commit()
            return True
        except Exception as e:
            logger.exception('sql helper execute exception msg:%s' % str(e))
            return False

    def query(self, command, commit = False, cursor_type = 'tuple'):
        try:
            with self._pool.connection() as conn:
                cursor = conn.cursor()
                cursor.execute(command)
                data = cursor.fetchall()
                if commit:
                    conn.commit()
                return data
        except Exception as e:
            logger.exception('sql helper execute exception msg:%s' % str(e))
            return None

    def query_one(self, command, commit = False, cursor_type = 'tuple'):
        try:
            with self._pool.connection() as conn:
                cursor = conn.cursor()
                cursor.execute(command)
                data = cursor.fetchone()
                if commit:
                    conn.commit()
                return data
        except Exception as e:
            logger.exception('sql helper execute exception msg:%s' % str(e))
            return None
            # 在整个 mysql 中查找

    def is_exists(self, table_name):
        try:
            command = "SHOW TABLES LIKE '%s'" % table_name
            with self._pool.connection() as conn:
                res = conn.cursor().execute(command)
                return True if res == 1 else False
        except Exception as e:
            logger.exception('sql helper is_exists exception msg:%s' % e)
            return False

    def check_table_exists(self, table_name, db_name = None):
        if db_name is None:
            db_name = self.db_name

        command = """SELECT COUNT(*) FROM information_schema.tables WHERE table_schema = '{db_name}' AND table_name = '{table_name}'""".format(
            db_name = db_name, table_name = table_name)
        try:
            with self._pool.connection() as conn:
                cursor = conn.cursor()
                cursor.execute(command)
                if cursor.fetchone()[0] == 1:
                    return True
        except:
            return False
