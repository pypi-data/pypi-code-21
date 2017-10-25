import os
from .FuncHelper import FuncHelper
from .DatetimePlus import DatetimePlus
import copy
from .Base import Base

def Singleton(cls):
    __instance = {}
    def getInstance(*args,**kwargs):
        if cls not in __instance:
            __instance[cls] = cls(*args,**kwargs)
        return __instance[cls]
    return getInstance

class ConstConfiger:
    cRootNode = ''
    SERVICE_MODULES = 'ServiceModules'
    INTERFACE_MODULES = 'InterfaceModules'

    OPTIONS = 'Options'
    OPTIONS_FILE_SIZE = 'FileSize'
    OPTIONS_DATA_PATH = 'FilePath'
    OPTIONS_FASTDFS_CONFIG_FILE = 'fastDFSConfigFilePath'
    OPTIONS_PORT = 'Port'
    OPTIONS_DEBUG = 'Debug'
    OPTIONS_HOST = 'Host'
    OPTIONS_THREAD_COUNT = 'ThreadCount'
    OPTIONS_WHITE_LIST_IPS = 'WhiteListIP'
    OPTIONS_SUPPER_USER_NAME = 'SupperUserName'
    OPTIONS_SUPPER_PASSWORD = 'SupperPassword'
    OPTIONS_LDAP_IP = 'LDAPUrl'         #10.86.87.52
    OPTIONS_LDAP_PREFIX = 'LDAPPrefix'   #geely\\
    OPTIONS_LDAP_BASE_DN = 'LDAPBaseDN'   #OU=GeelyStaff,dc=geely,dc=auto
    OPTIONS_MODULE_PREFIX = 'ModulePrefix'        #SDLC
    OPTIONS_MODULE_ALIVE_TIME = 'CheckModuleAliveTimeMinute'
    OPTIONS_ENCRYPTION_KEY = 'EncryptorKey'
    OPTIONS_HOME_PAGE_MODULE_NAME = 'HomePageModuleName'

    DATABASE = 'Database'
    DATABASE_SERVER_IP = 'ServerIP'
    DATABASE_PORT = 'Port'
    DATABASE_DB_NAME = 'DBName'
    DATABASE_USER_NAME = 'UserName'
    DATABASE_PASSWORD = 'Password'
    DATABASE_POOL_SIZE = 'PoolSize'

    LOGGER = 'Logger'
    LOGGER_LEVEL = 'Level'

    SERVICE_FILE_PATH = 'ServiceFilePath'
    SERVICE_ENABLE = 'Enable'
    SERVICE_IS_REGISTER_ZOOKEEPER = 'IsRegisterZookeeper'
    SERVICE_LOOP_TIME = 'LoopTime'
    SERVICE_OTHER_PARAMS = 'OtherParams'

    REISTER_GIT_URL = 'GitUrl'
    REISTER_GIT_USER_NAME = 'GitUserName'
    REISTER_GIT_PASSWORD = 'GitPasswd'
    REISTER_SWAGGER_URL = 'SwaggerUrl'

@Singleton
class Configer(Base):
    _configer_dict = {}

    def create_new_configer(self):
        '''
        创建一个新的配置文件
        '''
        _serviceModules = {}
        _interfaceModules = {}
        _options = {}
        _database = {}
        _logger = {}


        self._configer_dict[ConstConfiger.SERVICE_MODULES] = _serviceModules
        self._configer_dict[ConstConfiger.INTERFACE_MODULES] = _interfaceModules
        self._configer_dict[ConstConfiger.OPTIONS] = _options

        _options[ConstConfiger.LOGGER] = _logger
        _logger[ConstConfiger.LOGGER_LEVEL] = 0

        _options[ConstConfiger.OPTIONS_DEBUG] = True
        _options[ConstConfiger.OPTIONS_DATA_PATH] = '/data/'
        _options[ConstConfiger.OPTIONS_FILE_SIZE] = 2048
        _options[ConstConfiger.OPTIONS_HOST] = '0.0.0.0'
        _options[ConstConfiger.OPTIONS_PORT] = 80
        _options[ConstConfiger.OPTIONS_THREAD_COUNT] = 1
        _options[ConstConfiger.OPTIONS_FASTDFS_CONFIG_FILE] = ''
        _options[ConstConfiger.OPTIONS_MODULE_PREFIX] = 'SDLC'
        _options[ConstConfiger.OPTIONS_WHITE_LIST_IPS] = ['*']
        _options[ConstConfiger.OPTIONS_SUPPER_USER_NAME] = 'admin'
        _options[ConstConfiger.OPTIONS_SUPPER_PASSWORD] = '123456'
        _options[ConstConfiger.OPTIONS_LDAP_BASE_DN] = 'OU=GeelyStaff,dc=geely,dc=auto'
        _options[ConstConfiger.OPTIONS_LDAP_PREFIX] = 'geely\\'
        _options[ConstConfiger.OPTIONS_LDAP_IP] = '10.86.87.52'
        _options[ConstConfiger.OPTIONS_MODULE_ALIVE_TIME] = 10
        _options[ConstConfiger.OPTIONS_ENCRYPTION_KEY] = 'TTFrameworkerXXX'
        _options[ConstConfiger.OPTIONS_HOME_PAGE_MODULE_NAME] = ''


        _options[ConstConfiger.DATABASE] = _database
        _database[ConstConfiger.DATABASE_SERVER_IP] = ''
        _database[ConstConfiger.DATABASE_PORT] = 0
        _database[ConstConfiger.DATABASE_DB_NAME] = ''
        _database[ConstConfiger.DATABASE_USER_NAME] = ''
        _database[ConstConfiger.DATABASE_PASSWORD] = ''
        _database[ConstConfiger.DATABASE_POOL_SIZE] = 30

    def create_new_service_node(self,service_name,service_enable,service_file_path,is_register_zookeeper,git_url,git_username,git_passwd,loop_time,
                                database_ip,databse_port,database_db_name,database_user_name,database_passwd,database_pool_size,other_params):
        _node = {}
        _node[ConstConfiger.SERVICE_FILE_PATH] = service_file_path
        _node[ConstConfiger.SERVICE_ENABLE] = service_enable
        _node[ConstConfiger.SERVICE_IS_REGISTER_ZOOKEEPER] = is_register_zookeeper
        _node[ConstConfiger.REISTER_GIT_URL] = git_url
        _node[ConstConfiger.REISTER_GIT_USER_NAME] = git_username
        _node[ConstConfiger.REISTER_GIT_PASSWORD] = git_passwd
        _node[ConstConfiger.SERVICE_LOOP_TIME] = loop_time
        _node[ConstConfiger.SERVICE_OTHER_PARAMS] = other_params
        _database = {}
        _database[ConstConfiger.DATABASE_SERVER_IP] = database_ip
        _database[ConstConfiger.DATABASE_PORT] = databse_port
        _database[ConstConfiger.DATABASE_DB_NAME] = database_db_name
        _database[ConstConfiger.DATABASE_USER_NAME] = database_user_name
        _database[ConstConfiger.DATABASE_PASSWORD] = database_passwd
        _database[ConstConfiger.DATABASE_POOL_SIZE] = database_pool_size
        _node[ConstConfiger.DATABASE] = _database
        self._configer_dict[ConstConfiger.SERVICE_MODULES][service_name] = _node
        return True

    def create_new_options_node(self,debug,data_path,file_size,host,port,thread_count,white_list_ip,supper_user_name,supper_passwd,
                                ldap_base_dn,ldap_prefix,ldap_url,fastdfs_config_file_path,module_prefix,check_service_alive_time,
                                encryptor_key,home_page_module_name,logger_level,
                                database_ip, databse_port, database_db_name, database_user_name, database_passwd,database_pool_size):
        _options = {}
        _options[ConstConfiger.OPTIONS_DEBUG] = debug
        _options[ConstConfiger.OPTIONS_DATA_PATH] = data_path
        _options[ConstConfiger.OPTIONS_FILE_SIZE] = file_size
        _options[ConstConfiger.OPTIONS_HOST] = host
        _options[ConstConfiger.OPTIONS_PORT] = port
        _options[ConstConfiger.OPTIONS_THREAD_COUNT] = thread_count
        _options[ConstConfiger.OPTIONS_FASTDFS_CONFIG_FILE] = fastdfs_config_file_path
        _options[ConstConfiger.OPTIONS_MODULE_PREFIX] = module_prefix
        _options[ConstConfiger.OPTIONS_WHITE_LIST_IPS] = white_list_ip
        _options[ConstConfiger.OPTIONS_SUPPER_USER_NAME] = supper_user_name
        _options[ConstConfiger.OPTIONS_SUPPER_PASSWORD] = supper_passwd
        _options[ConstConfiger.OPTIONS_LDAP_BASE_DN] = ldap_base_dn
        _options[ConstConfiger.OPTIONS_LDAP_PREFIX] = ldap_prefix
        _options[ConstConfiger.OPTIONS_LDAP_IP] = ldap_url
        _options[ConstConfiger.OPTIONS_MODULE_ALIVE_TIME] = check_service_alive_time
        _options[ConstConfiger.OPTIONS_ENCRYPTION_KEY] = encryptor_key
        _options[ConstConfiger.OPTIONS_HOME_PAGE_MODULE_NAME] = home_page_module_name
        _database = {}
        _options[ConstConfiger.DATABASE] = _database
        _database[ConstConfiger.DATABASE_SERVER_IP] = database_ip
        _database[ConstConfiger.DATABASE_PORT] = databse_port
        _database[ConstConfiger.DATABASE_DB_NAME] = database_db_name
        _database[ConstConfiger.DATABASE_USER_NAME] = database_user_name
        _database[ConstConfiger.DATABASE_PASSWORD] = database_passwd
        _database[ConstConfiger.DATABASE_POOL_SIZE] = database_pool_size
        _logger = {}
        _options[ConstConfiger.LOGGER] = _logger
        _logger[ConstConfiger.LOGGER_LEVEL] = logger_level
        self._configer_dict[ConstConfiger.OPTIONS] = _options

    def create_new_interface_node(self,swagger_url,interface_name,interface_enable,interface_file_path,is_register_zookeeper,git_url,git_username,git_passwd,
                                  database_ip, databse_port, database_db_name, database_user_name, database_passwd,
                                  database_pool_size, other_params):
        _node = {}
        _node[ConstConfiger.REISTER_SWAGGER_URL] = swagger_url
        _node[ConstConfiger.SERVICE_FILE_PATH] = interface_file_path
        _node[ConstConfiger.SERVICE_ENABLE] = interface_enable
        _node[ConstConfiger.SERVICE_IS_REGISTER_ZOOKEEPER] = is_register_zookeeper
        _node[ConstConfiger.REISTER_GIT_URL] = git_url
        _node[ConstConfiger.REISTER_GIT_USER_NAME] = git_username
        _node[ConstConfiger.REISTER_GIT_PASSWORD] = git_passwd
        _node[ConstConfiger.SERVICE_OTHER_PARAMS] = other_params
        _database = {}
        _database[ConstConfiger.DATABASE_SERVER_IP] = database_ip
        _database[ConstConfiger.DATABASE_PORT] = databse_port
        _database[ConstConfiger.DATABASE_DB_NAME] = database_db_name
        _database[ConstConfiger.DATABASE_USER_NAME] = database_user_name
        _database[ConstConfiger.DATABASE_PASSWORD] = database_passwd
        _database[ConstConfiger.DATABASE_POOL_SIZE] = database_pool_size
        _node[ConstConfiger.DATABASE] = _database
        self._configer_dict[ConstConfiger.INTERFACE_MODULES][interface_name] = _node
        return True

    def create_new_logger_node(self,level):
        _logger = {}
        _logger[ConstConfiger.LOGGER_LEVEL] = level
        self._configer_dict[ConstConfiger.OPTIONS][ConstConfiger.LOGGER] = _logger

    def __init__(self,*args,**kwargs):
        super().__init__()
        self.__fileName = args[0]
        if self.__fileName == '':
            self.__fileName = 'Config.json'
        if not os.path.exists(self.__fileName):
            self.create_new_configer()
            self.write_config_file()
        self.read_config_file()

        admin_path = FuncHelper.get_file_path_by_full_path(__file__)
        admin_path = admin_path.replace('/Core','') + '/TTAdmin'
        self.create_new_interface_node(
            '','TTAdmin',True,admin_path,False,'','','','',0,'','','',0,{}
        )

    def exec_command(self,cmd,params_value):
        if cmd == 'delete_module_by_module_name':
            return self.delete_module_by_module_name(params_value[0],params_value[1])
        elif cmd == 'create_new_service_node':
            service_name, service_enable, service_file_path, is_register_zookeeper,\
             git_url, git_username, git_passwd, loop_time,\
             database_ip, databse_port, database_db_name, database_user_name, database_passwd, database_pool_size,\
             other_params = params_value
            return self.create_new_service_node(service_name,service_enable,service_file_path,is_register_zookeeper,
                                                      git_url,git_username,git_passwd,loop_time,
                                                      database_ip,databse_port,database_db_name,database_user_name,database_passwd,database_pool_size,
                                                      other_params)
        elif cmd == 'module_count':
            return self.module_count
        elif cmd == 'supper_user_password':
            return self.supper_user_password
        elif cmd == 'supper_user_name':
            return self.supper_user_name
        elif cmd == 'get_module_option_by_module_name':
            return self.get_module_option_by_module_name(params_value[0],params_value[1])
        elif cmd == 'create_new_interface_node':
            swagger_url, interface_name, interface_enable, interface_file_path, is_register_zookeeper, git_url, git_username, git_passwd,\
            database_ip, databse_port, database_db_name, database_user_name, database_passwd,\
            database_pool_size, other_params = params_value
            return self.create_new_interface_node(swagger_url, interface_name, interface_enable, interface_file_path, is_register_zookeeper,\
                                                  git_url, git_username, git_passwd,\
                                                  database_ip, databse_port, database_db_name, database_user_name, database_passwd,\
                                                  database_pool_size, other_params)
        else:
            if params_value == None:
                return getattr(self, cmd)()
            else:
                return getattr(self, cmd)(params_value)

    def __writeLog(self, log):
        print(log)

    def read_config_file(self):
        with open(self.__fileName, 'r') as f:
            jsonStr = f.read()
            json = FuncHelper.json_to_dict(jsonStr)
        self._configer_dict = json
        self.instance = FuncHelper.dict_to_instance(self._configer_dict)
        return self._configer_dict

    def write_config_file(self):
        with open(self.__fileName, 'w') as f:
            f.write(FuncHelper.dict_to_json(self._configer_dict))


    @property
    def Root(self):
        return self._configer_dict

    @property
    def exit_code(self):
        return self._configer_dict[ConstConfiger.OPTIONS][ConstConfiger.OPTIONS_SUPPER_PASSWORD]

    @property
    def db_option(self):
        return self._configer_dict[ConstConfiger.OPTIONS][ConstConfiger.DATABASE]

    @property
    def white_list_ips(self):
        return self._configer_dict[ConstConfiger.OPTIONS][ConstConfiger.OPTIONS_WHITE_LIST_IPS]

    @property
    def data_path(self):
        return self._configer_dict[ConstConfiger.OPTIONS][ConstConfiger.OPTIONS_DATA_PATH]

    @property
    def service_modules(self):
        return self._configer_dict[ConstConfiger.SERVICE_MODULES]

    @property
    def interface_modules(self):
        return self._configer_dict[ConstConfiger.INTERFACE_MODULES]

    @property
    def is_debug(self):
        return self._configer_dict[ConstConfiger.OPTIONS][ConstConfiger.OPTIONS_DEBUG]

    @property
    def japronto_port(self):
        return self._configer_dict[ConstConfiger.OPTIONS][ConstConfiger.OPTIONS_PORT]

    @property
    def japronto_listen_addrees(self):
        return self._configer_dict[ConstConfiger.OPTIONS][ConstConfiger.OPTIONS_HOST]

    @property
    def japronto_thread_count(self):
        return self._configer_dict[ConstConfiger.OPTIONS][ConstConfiger.OPTIONS_THREAD_COUNT]

    @property
    def logger_level(self):
        return self._configer_dict[ConstConfiger.OPTIONS][ConstConfiger.LOGGER][ConstConfiger.LOGGER_LEVEL]

    @property
    def module_name_prefix(self):
        return self._configer_dict[ConstConfiger.OPTIONS][ConstConfiger.OPTIONS_MODULE_PREFIX]

    @property
    def check_service_alive_time(self):
        return self._configer_dict[ConstConfiger.OPTIONS][ConstConfiger.OPTIONS_MODULE_ALIVE_TIME]

    @property
    def supper_user_name(self):
        return self._configer_dict[ConstConfiger.OPTIONS][ConstConfiger.OPTIONS_SUPPER_USER_NAME]

    @property
    def supper_user_password(self):
        return self._configer_dict[ConstConfiger.OPTIONS][ConstConfiger.OPTIONS_SUPPER_PASSWORD]

    @property
    def module_count(self):
        return len(self.interface_modules),len(self.service_modules)

    @property
    def ldap_base_dn(self):
        return self._configer_dict[ConstConfiger.OPTIONS][ConstConfiger.OPTIONS_LDAP_BASE_DN]

    @property
    def ldap_ip(self):
        return self._configer_dict[ConstConfiger.OPTIONS][ConstConfiger.OPTIONS_LDAP_IP]

    @property
    def ldap_prefix(self):
        return self._configer_dict[ConstConfiger.OPTIONS][ConstConfiger.OPTIONS_LDAP_PREFIX]

    @property
    def fastdfs_conf_path(self):
        return self._configer_dict[ConstConfiger.OPTIONS][ConstConfiger.OPTIONS_FASTDFS_CONFIG_FILE]

    def get_module_path_by_module_name(self,is_service,module_name):
        result = ''
        if is_service:
            modules = self.service_modules
        else:
            modules = self.interface_modules
        for _ in modules:
            if _ == module_name:
                result = modules[_].get(ConstConfiger.SERVICE_FILE_PATH, '')
                break
        return result

    def get_module_database_option_by_name(self,is_service,module_name):
        if is_service:
            modules = self.service_modules[module_name]
        else:
            modules = self.interface_modules[module_name]
        return modules[ConstConfiger.DATABASE]

    def get_module_is_enable_by_module_name(self,is_service,module_name):
        if is_service:
            modules = self.service_modules[module_name]
        else:
            modules = self.interface_modules[module_name]
        return modules[ConstConfiger.SERVICE_ENABLE]

    def get_module_option_by_module_name(self,is_service,module_name):
        if is_service:
            _module_option = copy.deepcopy(self.service_modules[module_name])
            result = {}
            result['service_file_path'] = _module_option.get(ConstConfiger.SERVICE_FILE_PATH, '')
            result['git_url'] = _module_option.get(ConstConfiger.REISTER_GIT_URL, '')
            result['git_username'] = _module_option.get(ConstConfiger.REISTER_GIT_USER_NAME, '')
            result['git_passwd'] = _module_option.get(ConstConfiger.REISTER_GIT_PASSWORD, '')
            result['database_ip'] = _module_option[ConstConfiger.DATABASE].get(ConstConfiger.DATABASE_SERVER_IP, '')
            result['databse_port'] = int(_module_option[ConstConfiger.DATABASE].get(ConstConfiger.DATABASE_PORT, 0))
            result['database_db_name'] = _module_option[ConstConfiger.DATABASE].get(ConstConfiger.DATABASE_DB_NAME, '')
            result['database_user_name'] = _module_option[ConstConfiger.DATABASE].get(ConstConfiger.DATABASE_USER_NAME, '')
            result['database_passwd'] = _module_option[ConstConfiger.DATABASE].get(ConstConfiger.DATABASE_PASSWORD, '')
            result['database_pool_size'] = int(_module_option[ConstConfiger.DATABASE].get(ConstConfiger.DATABASE_POOL_SIZE, 20))
            result['loop_time'] = _module_option.get(ConstConfiger.SERVICE_LOOP_TIME, 5)
            result['other_params'] = FuncHelper.dict_to_json(_module_option.get(ConstConfiger.SERVICE_OTHER_PARAMS, {}))
            result['service_enable'] = _module_option.get(ConstConfiger.SERVICE_ENABLE, True)
            result['is_register_zookeeper'] = _module_option.get(ConstConfiger.SERVICE_IS_REGISTER_ZOOKEEPER, False)
        else:
            _module_option = copy.deepcopy(self.interface_modules[module_name])
            result = {}
            result['interface_file_path'] = _module_option.get(ConstConfiger.SERVICE_FILE_PATH, '')
            result['swagger_url'] = _module_option.get(ConstConfiger.REISTER_SWAGGER_URL, '')
            result['git_url'] = _module_option.get(ConstConfiger.REISTER_GIT_URL, '')
            result['git_username'] = _module_option.get(ConstConfiger.REISTER_GIT_USER_NAME, '')
            result['git_passwd'] = _module_option.get(ConstConfiger.REISTER_GIT_PASSWORD, '')
            result['database_ip'] = _module_option[ConstConfiger.DATABASE].get(ConstConfiger.DATABASE_SERVER_IP, '')
            result['databse_port'] = int(_module_option[ConstConfiger.DATABASE].get(ConstConfiger.DATABASE_PORT, 0))
            result['database_db_name'] = _module_option[ConstConfiger.DATABASE].get(ConstConfiger.DATABASE_DB_NAME, '')
            result['database_user_name'] = _module_option[ConstConfiger.DATABASE].get(ConstConfiger.DATABASE_USER_NAME,'')
            result['database_passwd'] = _module_option[ConstConfiger.DATABASE].get(ConstConfiger.DATABASE_PASSWORD, '')
            result['database_pool_size'] = int(
                _module_option[ConstConfiger.DATABASE].get(ConstConfiger.DATABASE_POOL_SIZE, 20))
            result['other_params'] = FuncHelper.dict_to_json(_module_option.get(ConstConfiger.SERVICE_OTHER_PARAMS, {}))
            result['interface_enable'] = _module_option.get(ConstConfiger.SERVICE_ENABLE, True)
            result['is_register_zookeeper'] = _module_option.get(ConstConfiger.SERVICE_IS_REGISTER_ZOOKEEPER, False)
        return result

    def delete_module_by_module_name(self,is_service,module_name):
        if is_service:
            _ = self._configer_dict[ConstConfiger.SERVICE_MODULES].pop(module_name,None)
        else:
            _ = self._configer_dict[ConstConfiger.INTERFACE_MODULES].pop(module_name, None)

        self.write_config_file()
        return True

    def get_system_option(self):
        _module_option = copy.deepcopy(self._configer_dict[ConstConfiger.OPTIONS])
        result = {}
        result['debug'] = _module_option.get(ConstConfiger.OPTIONS_DEBUG, True)
        result['data_path'] = _module_option.get(ConstConfiger.OPTIONS_DATA_PATH, '')
        result['file_size'] = _module_option.get(ConstConfiger.OPTIONS_FILE_SIZE, 2048)
        result['host'] = _module_option.get(ConstConfiger.OPTIONS_HOST, '0.0.0.0')
        result['port'] = _module_option.get(ConstConfiger.OPTIONS_PORT, 80)
        result['thread_count'] = _module_option.get(ConstConfiger.OPTIONS_THREAD_COUNT, 1)
        result['fastdfs_config_file_path'] = _module_option.get(ConstConfiger.OPTIONS_FASTDFS_CONFIG_FILE, '')
        result['module_prefix'] = _module_option.get(ConstConfiger.OPTIONS_MODULE_PREFIX, 'SDLC')
        result['white_list_ip'] = _module_option.get(ConstConfiger.OPTIONS_WHITE_LIST_IPS, ['*'])
        result['supper_user_name'] = _module_option.get(ConstConfiger.OPTIONS_SUPPER_USER_NAME, 'admin')
        result['supper_passwd'] = _module_option.get(ConstConfiger.OPTIONS_SUPPER_PASSWORD, '123456')
        result['ldap_base_dn'] = _module_option.get(ConstConfiger.OPTIONS_LDAP_BASE_DN, 'OU=GeelyStaff,dc=geely,dc=auto')
        result['ldap_prefix'] = _module_option.get(ConstConfiger.OPTIONS_LDAP_PREFIX, 'geely\\')
        result['ldap_url'] = _module_option.get(ConstConfiger.OPTIONS_LDAP_IP, '10.86.87.52')
        result['check_service_alive_time'] = _module_option.get(ConstConfiger.OPTIONS_MODULE_ALIVE_TIME, 60)
        result['encryptor_key'] = _module_option.get(ConstConfiger.OPTIONS_ENCRYPTION_KEY, 'TTFrameworkerXXX')
        result['home_page_module_name'] = _module_option.get(ConstConfiger.OPTIONS_HOME_PAGE_MODULE_NAME, '')
        result['database_ip'] = _module_option[ConstConfiger.DATABASE].get(ConstConfiger.DATABASE_SERVER_IP, '')
        result['databse_port'] = int(_module_option[ConstConfiger.DATABASE].get(ConstConfiger.DATABASE_PORT, 0))
        result['database_db_name'] = _module_option[ConstConfiger.DATABASE].get(ConstConfiger.DATABASE_DB_NAME, '')
        result['database_user_name'] = _module_option[ConstConfiger.DATABASE].get(ConstConfiger.DATABASE_USER_NAME, '')
        result['database_passwd'] = _module_option[ConstConfiger.DATABASE].get(ConstConfiger.DATABASE_PASSWORD, '')
        result['database_pool_size'] = int(
            _module_option[ConstConfiger.DATABASE].get(ConstConfiger.DATABASE_POOL_SIZE, 20))
        result['logger_level'] = _module_option[ConstConfiger.LOGGER].get(ConstConfiger.LOGGER_LEVEL, 0)
        return result




