'''
  模块管理类
'''
from ..common.func_helper import FuncHelper
from ..common.configer import Configer
from .service_actuator import ServiceManager
from .interface_actuator import IntefaceManager
from ..connection.connection_manager import ConnectionManager
from ..common.statistics import Statistics


class ModuleManger(object):

    def __init__(self,params):
        self.configer_file_path = params.get('config_file_path', '')
        self.interface_port = params.get('port',0)
        self.work_directory = params.get('work_directory', '')
        if self.work_directory == '':
            self.work_directory = FuncHelper.get_curr_path()
        if not self.work_directory.endswith('/'):
            self.work_directory = self.work_directory + '/'
        self.statistics = Statistics(self.configer_file_path)


    def exec_modules(self):
        self.scan_module_directory();
        _configer = Configer(self.configer_file_path)
        _module_names = _configer.modules.keys()
        _all_services = []
        _all_interfaces = []
        for _name in _module_names:
            if not _configer.get_module_enable_by_module_name(_name):
                continue
            _path = _configer.get_module_path_by_module_name(_name)
            _services,_interfaces  = self.scan_exec_unit_by_module_name(_name,_path)
            if _services:
                _all_services.append(_services)
            if _interfaces:
                _all_interfaces.append(_interfaces)
        self.statistics.service_count,self.statistics.interface_count = len(_all_services),len(_all_interfaces)
        self.exec_service(_all_services)
        self.exec_interface(_all_interfaces)
        self.service_manager.stop()

    def scan_module_directory(self):
        '''
        扫描所有的模块列表
        '''
        _dirs = FuncHelper.get_dirs_name_by_path(self.work_directory + '/modules')
        _configer = Configer(self.configer_file_path)
        _module_names = _configer.modules.keys()
        for _name in _dirs:
            if _name not in _module_names:
                _configer.create_new_module_node(module_name = _name,
                                                 enable= True,
                                                 swagger_url = '',
                                                 file_path = '',
                                                 is_register_zookeeper = False,
                                                 git_url = '',
                                                 git_username = '',
                                                 git_passwd = '',
                                                 loop_time = 5,
                                                 database_driver_name = 'postgres',
                                                 database_ip = '',
                                                 databse_port = 5432,
                                                 database_db_name = '',
                                                 database_user_name = '',
                                                 database_passwd = '',
                                                 database_pool_size = 5,
                                                 other_params = {})
        _configer.write_config_file()

        return True


    def scan_exec_unit_by_module_name(self,module_name,path):
        '''
        根据模块名扫描模块内所有执行模块
        '''
        result = []
        if path == '':
            _path = self.work_directory + 'modules/' + module_name + '/'
        else:
            _path = path
            if not path.endswith('/'):
                _path = _path + '/'

        _all_files = FuncHelper.get_files_name_by_path(_path)
        _files = []
        for _ in _all_files:
            if _.startswith(module_name) and _.endswith('.py'):
                _files.append(_)
        #权限注册单元
        #提取服务类
        _services = []
        for _name in _files:
            _classname = FuncHelper.get_all_classname_by_file_path_name(_path + _name,'ServiceBase')
            if _classname:
                _unit_name = _name[:_name.find('.py')]
                _services.append((_classname[0],_unit_name))
        result_service = None
        if _services:
            result_service =(_services,module_name, _path)
        #提取接口类
        _interfaces = []
        for _name in _files:
            _classname = FuncHelper.get_all_classname_by_file_path_name(_path + _name,'InterfaceBase')
            if _classname:
                _unit_name = _name[:_name.find('.py')]
                _interfaces.append((_classname[0],_unit_name))
        result_interface = None
        if _interfaces:
            result_interface = (_interfaces,module_name, _path)

        return result_service,result_interface

    def exec_interface(self,interfaces):
        '''
        启动接口
        '''
        self.interface_manager = IntefaceManager(self.configer_file_path)
        self.statistics.get_interface_module_state_by_source = self.interface_manager.get_module_state
        self.interface_manager.statistics = self.statistics
        self.interface_manager.binding_modules(interfaces)
        self.interface_manager.binding_static_directory()

        _configer = Configer(self.configer_file_path)
        if self.interface_port == 0:
            self.interface_port = _configer.japronto_port
        from .global_share import GlobalShareValue
        GlobalShareValue.set_configer_file_path(self.configer_file_path)
        self.interface_manager.japronto.run(debug=_configer.is_debug,
                                            host=_configer.japronto_listen_addrees,
                                            port=self.interface_port,
                                            worker_num=_configer.japronto_thread_count)

    def exec_service(self,services):
        '''
        启动服务
        '''
        self.service_manager = ServiceManager(self.configer_file_path)
        self.statistics.get_service_module_state_by_source = self.service_manager.get_module_state
        self.service_manager.bingding_service(services)
        self.service_manager.start_service()
        self.service_manager.start_check_module_alive_thread()

    def get_connection_by_module_name(self,module_name):
        _configer = Configer(self.configer_file_path)
        _data_option = _configer.get_module_database_option_by_name(module_name)
        _connection_manager = ConnectionManager(self.configer_file_path)
        _connection = _connection_manager.get_connection_by_db_info(
            DriverName=_data_option.get('DriverName', 'postgres'),
            ServerIP=_data_option['ServerIP'],
            Port=_data_option['Port'],
            DBName=_data_option['DBName'],
            UserName=_data_option['UserName'],
            Password=_data_option['Password'],
            PoolSize=_data_option['PoolSize'])
        return _connection


