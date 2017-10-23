from TTFramework.Core.DatetimePlus import *
from TTFramework.Core.ServiceManager import *
from TTFramework.Core.Logger import *
from TTFramework.Core.Configer import *
from TTFramework.Core.ConnectionPostgres import *
from TTFramework.Core.ServiceBase import *
from TTFramework.Core.HttpTesterBase import *
from TTFramework.Core.FileManager import *
from TTFramework.Core.FuncHelper import *
from TTFramework.Core.InterfaceBase import *
from TTFramework.Core.InterfaceManager import *
from TTFramework.Core.Permissions import *
from TTFramework.Core.Statistics import *
from TTFramework.Core.InstanceFactory import *
from japronto import Application as japronto_application
from sys import argv

class TTApplication(object):
    _configer = None
    _interface_manager = None
    _service_manager = None
    _logger = None
    _japronto = None
    _statistics = None

    def __init__(self):
        '''
        处理命令行传递进来的参数
        '''
        self._params = {}
        self._proc_argv()

    def start(self):
        self._japronto = japronto_application()
        self._configer = Configer(self._params.get('config_file_path',''))

        # self._configer.create_new_interface_node(
        #     '','SDLCTester',True,'/download/SDLCTester',False,'','','','127.0.0.1',5432,'sdlc007','postgres','postgres',30
        # )
        # self._configer.create_new_service_node('SDLCServiceTester',True,'/download/SDLCServiceTester',False,'','','',5,'127.0.0.1',5432,'sdlc007',
        #                                        'postgres','postgres',30)
        # self._configer.write_config_file()
        self._statistics = Statistics()
        self._logger = Logger(self._configer)
        InstanceFactory.configer = self._configer
        InstanceFactory.logger = self._logger
        self._service_manager = ServiceManager(self._configer,self._logger)
        self._service_manager.start()
        self._interface_manager = IntefaceManager(self._japronto.router,self._configer,self._logger,self._japronto,self._statistics,self._service_manager)
        self._interface_manager.start()


        port = self._params.get('port',0)
        if port == 0:
            port = self._configer.japronto_port
        self._japronto.run(debug=self._configer.is_debug,
                            host=self._configer.japronto_listen_addrees,
                            port=port,
                            worker_num=self._configer.japronto_thread_count)
        self._japronto.exec_reloader()
        self._service_manager.stop()

    def _proc_argv(self):
        _argv_count = len(argv)
        if _argv_count > 1:
            for i in range(1,_argv_count):
                _argv = argv[i].lower()
                if _argv.startswith('-h'):
                    self.console_print_help()
                elif _argv.startswith('-p'):
                    self.params_port(argv[i][2:])
                elif _argv.startswith('-c'):
                    self.params_config_file_path(argv[i][2:])

    def console_print_help(self):
        print('''
        TTFramwork Version 1.00 beta
        Usage:
          -h  help
          -p  port            example -p8080
          -c  config file     example -c/home/root/app.config
        ''')
        quit(0)

    @staticmethod
    def get_connection_by_module_name(is_service,module_name):
        if is_service:
            return TTApplication.app._service_manager.get_connection_by_module_name(module_name)
        else:
            return TTApplication.app._interface_manager.get_connection_by_module_name(module_name)

    def params_port(self,port):
        try:
            self._params['port'] = int(port)
        except:
            self._params['port'] = 0

    def params_config_file_path(self,path):
        self._params['config_file_path'] = path

    @staticmethod
    def main():
        TTApplication.app = TTApplication()
        TTApplication.app.start()
