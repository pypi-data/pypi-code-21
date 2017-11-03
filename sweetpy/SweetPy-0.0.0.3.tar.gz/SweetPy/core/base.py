from abc import abstractmethod,ABCMeta
import multiprocessing,threading
import types
import inspect
from ..common.logger import Logger
from ..common.configer import Configer
from .global_share import GlobalShareValue
from ..connection.connection_manager import ConnectionManager
from .plugin_manager import PluginManager

class InterProcessBase(object, metaclass=ABCMeta):
    def __init__(self):
        self._pipe_exec, self._pipe_result = multiprocessing.Pipe(True)
        self.__thread_exec = threading.Thread(target=self.exec_from_pipe, args=())
        self.__thread_exec.daemon = True
        self.__thread_exec.start()

    def exec_from_pipe(self):
        while True:
            _command = self._pipe_exec.recv()
            cmd = _command[0]
            value = _command[1]
            try:
                _ = self.exec_command_in(cmd,value)
            except Exception as e:
                _ = None
            self._pipe_exec.send(_)


    def exec_command_in(self,cmd,params_value):
        if params_value == None:
            return getattr(self, cmd)()
        else:
            _func = getattr(self,cmd)
            _func_info = inspect.signature(_func)
            _params = _func_info.parameters
            if len(_params.keys()) > 1:
                return self.exec_command(cmd,params_value)
            else:
                return getattr(self, cmd)(params_value)

    @abstractmethod
    def exec_command(self,cmd,params_value):
        return None

    def send_pipe_command(self,params):
        self._pipe_result.send(params)
        return self._pipe_result.recv()


def decorator_all_function(func):
    def process_context(self,request):
        if hasattr(request, 'context'):
            pass
        else:
            pass
        return func(self,request)
    return process_context


class DecoratorMetaClass(type):
    def __new__(cls, clsname, bases, dct):
        ndict = {}
        for name, val in dct.items():
            if isinstance(val,types.FunctionType):
                ndict[name] = decorator_all_function(dct[name])
            else:
                ndict[name] = dct[name]
        return super(DecoratorMetaClass, cls).__new__(cls, clsname, bases, ndict)

connection_manager = None

class ModuleExtend(object):
    def get_connection_session(self,config_file_path,module_name):
        global connection_manager
        try:
            if not connection_manager:
                connection_manager = ConnectionManager(config_file_path)
            _configer = Configer(config_file_path)
            _data_option = _configer.get_module_database_option_by_name(module_name)
            connection = connection_manager.get_connection_by_db_info(DriverName=_data_option.get('DriverName','postgres'),
                                                                  ServerIP=_data_option['ServerIP'],
                                                                  Port=_data_option['Port'],
                                                                  DBName=_data_option['DBName'],
                                                                  UserName=_data_option['UserName'],
                                                                  Password=_data_option['Password'],
                                                                  PoolSize=_data_option['PoolSize'])
        except Exception as e:
            logger = Logger()
            logger.error('模块' + module_name + '数据库连接失败.' + str(e))
            connection = None
        return connection

    def get_plugin_by_name(self,plugin_name):
        return PluginManager.get_instance_by_plugin_name(plugin_name)

    @staticmethod
    def get_plugin_by_names(names=()):
        def get_func(func):
            def process_context(self,request,*args):
                if names:
                    plugin = type('plugin', (), {})
                    is_have_session = False
                    try:
                        _interface_extent = ModuleExtend()
                        _configer_file_path = GlobalShareValue.get_configer_file_path()
                        for _n in names:
                            if _n == 'connection':
                                connection = _interface_extent.get_connection_session(_configer_file_path,self.name)
                                if connection:
                                    session = connection.session()
                                    setattr(plugin,_n,session)
                                    is_have_session = True
                                else:
                                    setattr(plugin, _n, None)
                            elif _n == 'configer':
                                configer = Configer(GlobalShareValue.get_configer_file_path())
                                setattr(plugin, _n, configer)
                            elif _n == 'logger':
                                logger = Logger()
                                setattr(plugin, _n, logger)
                            else:
                                try:
                                    _instance = _interface_extent.get_plugin_by_name(_n)
                                except Exception as e:
                                    logger = Logger()
                                    logger.error('插件' + _n + '生成失败:' + str(e))
                                    _instance = None
                                setattr(plugin, _n,_instance)
                        result = func(self,request,plugin)
                    finally:
                        if is_have_session:
                            session.close()
                else:
                    result = func(self, request)
                return result
            return process_context
        return get_func