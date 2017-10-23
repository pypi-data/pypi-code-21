from .FastDfsManager import FastDfsManager
from .ConnectionPostgres import PostgresConnection
from .LDAPManager import LDAPManager
from .Configer import ConstConfiger

class InstanceFactory(object):
    configer = None
    logger = None
    def __init__(self):
        pass

    @staticmethod
    def create_postgres_connection(is_service,module_name):
        _connection = None
        _database_option = InstanceFactory.configer.get_module_database_option_by_name(is_service, module_name)
        if _database_option[ConstConfiger.DATABASE_DB_NAME] == '':
            return _connection
        try:
            _connection = PostgresConnection(_database_option[ConstConfiger.DATABASE_USER_NAME],
                                             _database_option[ConstConfiger.DATABASE_PASSWORD],
                                             _database_option[ConstConfiger.DATABASE_SERVER_IP],
                                             _database_option[ConstConfiger.DATABASE_PORT],
                                             _database_option[ConstConfiger.DATABASE_DB_NAME], InstanceFactory.configer.is_debug,
                                             _database_option[ConstConfiger.DATABASE_POOL_SIZE])
        except Exception as e:
            InstanceFactory.logger.error('创建模块[' + module_name + ']数据连接失败：' + str(e))
        return _connection

    @staticmethod
    def create_fastdfs():
        _fastdfs = None
        if InstanceFactory.configer.fastdfs_conf_path == '':
            return _fastdfs
        try:
            _fastdfs = FastDfsManager(InstanceFactory.configer.fastdfs_conf_path)
        except Exception as e:
            pass
        return _fastdfs

    @staticmethod
    def create_ldap():
        _ldap = None
        if InstanceFactory.configer.ldap_ip == '':
            return _ldap
        try:
            _ldap = LDAPManager(InstanceFactory.configer.ldap_ip,
                           InstanceFactory.configer.ldap_base_dn,
                           InstanceFactory.configer.ldap_prefix
                           )
        except Exception as e:
            pass
        return _ldap
