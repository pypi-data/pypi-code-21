import json
import os, sys
import pymysql
current_path = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, current_path + '/../')
from messagingdispatcher.db.basedb import BaseDB
import config

class RelationalDB(BaseDB):
    def __init__(self,
                 table_name,
                 allowed_type,
                 host_name=config.relationaldb_host,
                 database_name=config.relationaldb_dbname,
                 username=config.relationaldb_username,
                 password=config.relationaldb_password):
        self._connection = pymysql.connect(host=host_name,
                                           user=username,
                                           password=password,
                                           db=database_name,
                                           cursorclass=pymysql.cursors.DictCursor)

        self._table = table_name
        self._allowed_type = allowed_type

    def add(self, item):
        if isinstance(item, self._allowed_type):
            try:
                sql = "INSERT INTO {} ({}) VALUES('{}')".format(self._table,
                                                                ",".join(item.to_dict().keys()),
                                                                "', '".join(str(value) for value in item.to_dict().values()))

                self._connection.cursor().execute(sql)
                self._connection.commit()
            except Exception as exception:
                raise exception
        else:
            raise TypeError('Invalid argument. {} object is expected'.format(self._allowed_type))
        
    def add_batch(self, items):
        pass
        
    def get(self, key, value):
        pass
        
    def get_all(self, filter_key=None, filter_value=None, partial_match=False):
        pass

    def update(self, key, value, update_key, update_value):
        pass

    def delete(self, key, value):
        pass

    def purge(self):
        pass
