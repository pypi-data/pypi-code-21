import os
import sys
import time,signal
import multiprocessing
from .FuncHelper import FuncHelper
from .InstanceFactory import InstanceFactory
from .SessionManager import SessionManager
from .Base import Base


def myHandler(signum='', frame=''):
    time.sleep(3)
    os.kill(multiprocessing.current_process().pid,signal.SIGINT)

def ExitApplication(request):
    # t = threading.Thread(target=myHandler,args=())
    # t.start()
    return request.Response(text='exit')

class IntefaceManager(Base):
    __instances = {}
    __connections = []
    __session_manager = None

    def read_static_file(self,request,filePath=''):
        if not os.path.exists(filePath):
            return request.Response(code=404, text='Not Found')
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
        self.__statistics.send_bytes_count = sys.getsizeof(result)
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
        return self.__session_manager.get_session(request)


    def binding_transfer_method(self, method):
        def processMethod(request):
            if '*' in self.__configer.white_list_ips:
                pass
            else:
                if (not self.__configer.IsDebug) and (not request.remote_addr in self.__configer.UnLimitedIP):
                    self.logger.info('非法连接 ,IP:' + request.remote_addr + ' Path:' + request.path)
                    return request.Response(code=403,text='Forbidden')
            errorCode = 0
            try:
                self.__statistics.set_module_visitors(FuncHelper.get_module_name_by_path(request.path))
                self.__statistics.recv_bytes_count = sys.getsizeof(request)
                result = method(request)
                self.__statistics.send_bytes_count = sys.getsizeof(result)
                self.logger.info('IP:' + request.remote_addr + ' Path:' + request.path + ' 正常访问')
            except Exception as e:
                self.logger.info('IP:' + request.remote_addr + ' Path:' + request.path + ' 访问出错')
                result = str(e)
                self.logger.error(request.path + '出错：' + str(e))
                errorCode = 1
            if errorCode == 1:
                return request.Response(text='error:' + result)
            else:
                return result
        return processMethod

    def binding_setting(self,module_instance,module_config):
        module_instance.configer = module_config

    def create_module_connection(self,module_name):
        return InstanceFactory.create_postgres_connection(False, module_name)
        

    def binding_method(self,module_name,sub_mouduleName,module_path):
        module = __import__(sub_mouduleName)
        moduleInstance = getattr(module, sub_mouduleName)()
        methods = dir(moduleInstance)
        moduleInstance.path = module_path
        moduleInstance.logger = self.logger
        moduleInstance.connection = self.get_connection_by_module_name(module_name)
        moduleInstance.DataPath = self.__configer.data_path + module_name + '/'
        self.__instances[sub_mouduleName] = moduleInstance
        moduleInstance.allModules = self.__instances
        self.binding_setting(moduleInstance,self.__configer.interface_modules[module_name])
        if module_name == 'TTAdmin':
            moduleInstance.Configer = self.__configer
            moduleInstance.Statistics = self.__statistics
            moduleInstance.ServiceManager = self.__service_manager
            moduleInstance.InterfaceManager = self
        for methodName in methods:
            if (methodName.startswith('__') or
                methodName.startswith('_')):
                pass
            else:
                method = getattr(moduleInstance,methodName)
                methodPath = '/' + module_name.replace(self.__configer.module_name_prefix,'') + '/' + methodName
                if methodPath in self.__router_paths:
                    self.logger.info('方法[' + methodPath + ']重复')
                    continue
                self.__router_paths.append(methodPath)
                self.__router.add_route(methodPath, self.binding_transfer_method(method))

                if self.__configer.is_debug and (module_name != 'TTAdmin'):
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
        path = self.__configer.get_module_path_by_module_name(False,module_name)
        if path == '':
            path = FuncHelper.get_curr_path() + '/Interfaces/' + module_name
        return path

    def binding_modules(self):
        '''
        根据配置加载模块
        '''
        modules = self.__configer.interface_modules
        for _name in modules:
            if not self.__configer.get_module_is_enable_by_module_name(False, _name):
                continue
            if not self.__configer.get_module_is_enable_by_module_name(False,_name):
                continue
            modulePath = self.get_module_path(_name)
            _list = self.get_sub_moudule_list(_name,modulePath)
            self.__router_paths = []
            for _sub_name in _list:
                self.binding_method(_name,_sub_name,modulePath)
            self.__router_paths = []
            self.binding_static_directory(_name)
            if _name != 'TTAdmin':
                self.logger.info('接口模块[' + _name + ']启动完成！')

    def unbinding_module_by_module_name(self,module_name=''):
        '''
        根据模块名 删除模块:
        '''
        if module_name == '':
            return False
        while True:
            _haveChange = False
            _module_name = module_name.replace(self.__configer.module_name_prefix,'')
            for i,_ in enumerate(self.__router._routes):
                if _.pattern.startswith('/' + _module_name + '/'):
                    del self.__router._routes[i]
                    _haveChange = True
            if not _haveChange:
                break
        vaue = self.__router.get_matcher().match_request
        print(dir(vaue))

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


    def get_connection_by_module_name(self,module_name):
        for _ in self.__connections:
            if _[0] == module_name:
                return _[1]
        _connection = self.create_module_connection(module_name)
        self.__connections.append((module_name,_connection))
        return _connection


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
            self.__router.add_route('/static/{p1}', self.binding_transfer_method(self.download_static_file))
            self.__router.add_route('/static/{p1}/{p2}', self.binding_transfer_method(self.download_static_file))
            self.__router.add_route('/static/{p1}/{p2}/{p3}', self.binding_transfer_method(self.download_static_file))
        else:
            self.__router.add_route('/' + moudle_name.replace(self.__configer.module_name_prefix,'') + '/static/{p1}', self.binding_transfer_method(self.download_static_file_by_moudle_name))
            self.__router.add_route('/' + moudle_name.replace(self.__configer.module_name_prefix,'') + '/static/{p1}/{p2}', self.binding_transfer_method(self.download_static_file_by_moudle_name))
            self.__router.add_route('/' + moudle_name.replace(self.__configer.module_name_prefix,'') + '/static/{p1}/{p2}/{p3}', self.binding_transfer_method(self.download_static_file_by_moudle_name))


    def __init__(self,router,configer,logger,japronto,statistics,service_manager):
        super().__init__()
        self.__router = router
        self.__configer = configer
        self.__statistics = statistics
        self.__service_manager = service_manager

        self.logger = logger
        self.__session_manager = SessionManager()
        self.__japronto = japronto
        self.__japronto.extend_request(self.session, property=True) #, property=True

    def start(self):
        self.binding_modules()
        self.binding_static_directory()
        # self.__router.add_route('/exit/' + self.__configer.exit_code, ExitApplication)

    def check_is_run_by_module_name(self,module_name):
        return self.__instances.get(module_name,None) != None

    def get_module_state(self):
        _result_arr = []
        for _n in self.__configer.interface_modules.keys():
            _ = {}
            _['name'] = _n
            _['is_run'] = self.check_is_run_by_module_name(_n)
            _result_arr.append(_)
        return _result_arr




if __name__ == '__main__':
    filelist = os.listdir('/root/work/AutoTest/Interfaces/SDLCJenkins')

