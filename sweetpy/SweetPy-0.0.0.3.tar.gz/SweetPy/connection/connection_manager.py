from SweetPy.common.configer import ConstConfiger
from SweetPy.connection.connection_postgres import PostgresConnection

from SweetPy.core.plugin_manager import PluginManager


class ConnectionManager():

    connections = {}
    def __init__(self,configer_file_path):
        self.configer_file_path = configer_file_path

    def get_connection_by_db_info(self,**kwargs):
        driver_name = kwargs[ConstConfiger.DATABASE_DRIVER_NAME]
        ip = kwargs[ConstConfiger.DATABASE_SERVER_IP]
        port = kwargs[ConstConfiger.DATABASE_PORT]
        db_name = kwargs[ConstConfiger.DATABASE_DB_NAME]
        user_name = kwargs[ConstConfiger.DATABASE_USER_NAME]
        user_pwd = kwargs[ConstConfiger.DATABASE_PASSWORD]
        pool_size = kwargs[ConstConfiger.DATABASE_POOL_SIZE]
        key_name = driver_name + ip + str(port) + db_name + user_name + user_pwd
        _connection = self.connections.get(key_name, None)
        if _connection:
            return _connection

        if driver_name.lower() == 'postgres':
            try:
                _connection = PostgresConnection(kwargs[ConstConfiger.DATABASE_USER_NAME],
                                                 kwargs[ConstConfiger.DATABASE_PASSWORD],
                                                 kwargs[ConstConfiger.DATABASE_SERVER_IP],
                                                 kwargs[ConstConfiger.DATABASE_PORT],
                                                 kwargs[ConstConfiger.DATABASE_DB_NAME],
                                                 False,
                                                 kwargs[ConstConfiger.DATABASE_POOL_SIZE])
                self.connections[key_name] = _connection
            except Exception as e:
                _connection = None
            return _connection
        elif driver_name.lower() == 'mysql':
            pass


