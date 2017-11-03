import multiprocessing
import os
import signal
import sys
import time

from japronto import RouteNotFoundException
from ..common.func_helper import FuncHelper
from ..common.session import SessionManager
from .base import InterProcessBase
from .interface_base import APIResponse, create_response
from .plugin_manager import PluginManager
from ..common.configer import Configer
from japronto import Application as japronto_application
from ..common.statistics import Statistics
from ..common.logger import Logger


def myHandler(signum='', frame=''):
    time.sleep(3)
    os.kill(multiprocessing.current_process().pid,signal.SIGINT)

def ExitApplication(request):
    # t = threading.Thread(target=myHandler,args=())
    # t.start()
    return request.Response(text='exit')

def handle_not_found(request, exception):
    return create_response(APIResponse.NOT_FOUND)

class IntefaceManager(object):
    __instances = {}
    __connections = []
    session_manager = None

    def read_static_file(self,request,filePath=''):
        if not os.path.exists(filePath):
            return create_response(APIResponse.NOT_FOUND)
        extName = FuncHelper.get_file_extname(filePath)
        extName = extName.lower()
        if extName == 'jpg':
            mimeTypeStr = 'image/jpeg'
        elif extName == 'html':
            mimeTypeStr = 'text/html'
        elif extName == 'htm':
            mimeTypeStr = 'text/html'
        elif extName == 'txt':
            mimeTypeStr = 'text/html'
        elif extName == 'gif':
            mimeTypeStr = 'image/gif'
        elif extName == 'png':
            mimeTypeStr = 'image/png'
        elif extName == 'js':
            mimeTypeStr = 'text/javascript'
        elif extName == 'css':
            mimeTypeStr = 'text/css'
        else:
            mimeTypeStr = 'application/octet-stream'

        with open(filePath, 'rb')  as f:
            txt = f.read()
        result = request.Response(body=txt, mime_type=mimeTypeStr,
                         headers={"Accept-Ranges": "bytes", "Access-Control-Allow-Origin": "*"})
        self.statistics.send_bytes_count = sys.getsizeof(result)
        return result


    def download_static_file_by_moudle_name(self, request):
        path = request.path
        module_name = FuncHelper.get_module_name_by_path(request.path)
        path = path.replace( '/' + module_name + '/','/',1)
        fileName = self.__instances[module_name].path + path
        return self.read_static_file(request,fileName)

    def download_static_file(self, request):
        path = request.path
        fileName = FuncHelper.get_curr_path() + path
        return self.read_static_file(request,fileName)

    def session(self,request):
        return self.session_manager.get_session(request)

    def binding_transfer_method(self, method):
        def processMethod(request):
            if '*' in self.white_list_ips:
                pass
            else:
                if (not self.is_debug) and (not request.remote_addr in self.white_list_ips):
                    self.logger.info('非法连接 ,IP:' + request.remote_addr + ' Path:' + request.path)
                    return create_response(APIResponse.UNAUTHORIZED_SERVICE_INVOKER)
            try:
                self.statistics.set_module_visitors(FuncHelper.get_module_name_by_path(request.path))
                self.statistics.recv_bytes_count = sys.getsizeof(request)
                result = method(request)
                self.statistics.send_bytes_count = sys.getsizeof(result)
            except Exception as e:
                result =  create_response(APIResponse.FAIL,message=str(e))
                self.logger.error(request.path + '出错：' + str(e))
            return result
        return processMethod

    def binding_method(self,_module_name,_classname,_unit_name,_path):
        sys.path.append(_path)
        module = __import__(_unit_name)
        moduleInstance = getattr(module, _classname)()
        methods = dir(moduleInstance)
        moduleInstance.path = _path
        moduleInstance.statistics = self.statistics
        _configer = Configer(self.config_file_path)
        moduleInstance.DataPath = _configer.data_path + _module_name + '/'
        self.__instances[_unit_name] = moduleInstance
        moduleInstance.name = _module_name
        for methodName in methods:
            if (methodName.startswith('__') or
                methodName.startswith('_')):
                pass
            else:
                method = getattr(moduleInstance,methodName)
                methodPath = '/' + _module_name.replace(_configer.module_name_prefix,'') + '/' + methodName
                if methodPath in self.__router_paths:
                    self.logger.info('方法[' + methodPath + ']重复')
                    continue
                self.__router_paths.append(methodPath)
                self.japronto.router.add_route(methodPath, self.binding_transfer_method(method))

                if _configer.is_debug and (_module_name != 'TTAdmin'):
                    print(methodPath)

    def get_sub_moudule_list(self,module_name,module_path=''):
        '''
        检查模块目录所有的模块单元文件 动态加载时提供模块所在目录 支持从任意目录加载
        '''
        _sub_moudules = []
        filePath = module_path
        if not os.path.isdir(filePath):
            self.logger.info('模块[' + module_name + ']路径不正确！')
            return _sub_moudules
        sys.path.append(filePath)
        filelist = os.listdir(filePath)
        for f in filelist:
            if f.startswith(module_name) and f.endswith('.py'):
                _sub_moudules.append(f[:f.find('.')])
        return _sub_moudules

    def get_module_path(self,module_name=''):
        _configer = Configer(self.config_file_path)
        path = _configer.get_module_path_by_module_name(False,module_name)
        if path == '':
            path = FuncHelper.get_curr_path() + '/Interfaces/' + module_name
        return path

    def binding_modules(self,interfaces):
        '''
        加载模块
        '''
        for _interface in interfaces:
            _module_name = _interface[1]
            _path = _interface[2]
            self.__router_paths = []
            for _ in _interface[0]:
                _classname = _[0]
                _unit_name = _[1]
                self.binding_method(_module_name,_classname,_unit_name,_path)
            self.binding_static_directory(_module_name)
            if _module_name != 'TTAdmin':
                self.logger.info('接口模块[' + _module_name + ']启动完成！')

    def unbinding_module_by_module_name(self,module_name=''):
        '''
        根据模块名 删除模块:
        '''
        if module_name == '':
            return False
        while True:
            _haveChange = False
            _module_name = module_name.replace(self.module_name_prefix,'')
            for i,_ in enumerate(self.__router._routes):
                if _.pattern.startswith('/' + _module_name + '/'):
                    del self.__router._routes[i]
                    _haveChange = True
            if not _haveChange:
                break

        _name_arr = []
        for _ in self.__instances.keys():
            if _.startswith(module_name):
                _name_arr.append(_)
        for _ in _name_arr:
            self.__instances.pop(_)

        for _ in self.__connections:
            if _[0] == module_name:
                self.__connections.remove(_)
                break
        self.logger.info('接口模块[' + module_name + ']卸载完成！')
        return True


    def binding_module_by_module_name(self,module_name=''):
        '''
        根据模块名 启动一个模块 启动前把模块的东西卸载一遍 防止重复
        '''
        if module_name == '':
            return
        self.unbinding_module_by_module_name(module_name)
        _module_path = self.get_module_path(module_name)
        _list = self.get_sub_moudule_list(module_name,_module_path)
        self.__router_paths = []
        for sm in _list:
            self.binding_method(module_name, sm,_module_path)
        self.__router_paths = []
        self.binding_static_directory(module_name)
        self.logger.info('接口模块[' + module_name + ']启动完成！')

    def binding_static_directory(self,moudle_name=''):
        if moudle_name == '':
            self.japronto.router.add_route('/static/{p1}', self.binding_transfer_method(self.download_static_file))
            self.japronto.router.add_route('/static/{p1}/{p2}', self.binding_transfer_method(self.download_static_file))
            self.japronto.router.add_route('/static/{p1}/{p2}/{p3}', self.binding_transfer_method(self.download_static_file))
        else:
            self.japronto.router.add_route('/' + moudle_name.replace(self.module_name_prefix,'') + '/static/{p1}', self.binding_transfer_method(self.download_static_file_by_moudle_name))
            self.japronto.router.add_route('/' + moudle_name.replace(self.module_name_prefix,'') + '/static/{p1}/{p2}', self.binding_transfer_method(self.download_static_file_by_moudle_name))
            self.japronto.router.add_route('/' + moudle_name.replace(self.module_name_prefix,'') + '/static/{p1}/{p2}/{p3}', self.binding_transfer_method(self.download_static_file_by_moudle_name))


    def __init__(self,config_file_path):
        super().__init__()
        self.japronto = japronto_application()
        self.config_file_path = config_file_path
        self.session_manager = SessionManager()

        self.japronto.extend_request(self.session, property=True)
        self.japronto.add_error_handler(RouteNotFoundException, handle_not_found)

        self.logger = Logger()

        _configer = Configer(self.config_file_path)
        self.module_name_prefix = _configer.module_name_prefix
        self.white_list_ips = _configer.white_list_ips
        self.is_debug = _configer.is_debug

    def start(self):
        self.binding_modules()
        self.binding_static_directory()


    def check_is_run_by_module_name(self,module_name):
        return self.__instances.get(module_name,None) != None

    def get_module_state(self):
        _result_arr = []

        for _n in self.__instances.keys():
            _ = {}
            _['name'] = _n
            _['is_run'] = True
            _result_arr.append(_)
        return _result_arr




if __name__ == '__main__':
    filelist = os.listdir('/root/work/AutoTest/Interfaces/SDLCJenkins')

