from sys import argv

from .common.permissions import *
from .common.configer import *
from .common.datetime_plus import *
from .common.compressor import *
from .common.func_helper import *
from .common.logger import *
from .common.statistics import *
from .core.interface_actuator import *
from .core.interface_base import *
from .core.module_manager import *
from .core.plugin_manager import *
from .core.service_actuator import *
from .core.service_base import *
from .plugin.http_tester_base import *
from .core.global_share import *


class TTApplication(object):

    def __init__(self):
        '''
        处理命令行传递进来的参数
        '''
        self._params = {}
        self._proc_argv()

    def start(self):
        GlobalShareValue.set_configer_file_path(self._params.get('config_file_path',''))
        self.module_manager = ModuleManger(self._params)
        self.module_manager.exec_modules()


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
                elif _argv.startswith('-w'):
                    self.params_work_directory(argv[i][2:])

    def console_print_help(self):
        print('''
        TTFramwork Version 1.00 beta
        Usage:
          -h  help
          -p  port            example -p8080
          -c  config file     example -c/home/root/app.config
          -w  work directory  example -w/home/root/project
        ''')
        quit(0)

    @staticmethod
    def get_connection_by_module_name(module_name):
        return TTApplication.app.module_manager.get_connection_by_module_name(module_name)

    def params_work_directory(self,dir):
        if FuncHelper.check_directory_exists(dir):
            self._params['work_directory'] = dir
        else:
            print('work directory is not found')
            quit(0)

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
