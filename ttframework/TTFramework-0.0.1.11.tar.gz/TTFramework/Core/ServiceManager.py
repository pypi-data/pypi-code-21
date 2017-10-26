import multiprocessing
import os
import sys
import threading
import time
from .Configer import ConstConfiger
from .FuncHelper import FuncHelper
from .DatetimePlus import DatetimePlus
from .Base import Base
from .InstanceFactory import InstanceFactory


class ServiceManager(Base):
    __modules = []
    __threading_pool = []
    __connections = []
    __thread_check_modules_alive = None
    __thread_recv_modules_alive = None
    __process_recv_alive = __process_send_alive = None

    def __init__(self, configer, logger):
        super().__init__()
        self.configer = configer
        self.logger = logger
        self.__process_recv_alive, self.__process_send_alive = multiprocessing.Pipe(False)


    def start(self):
        self.bingding_service()
        self.start_service()

        self.__thread_check_modules_alive = threading.Thread(target=self.check_modules_alive, args=())
        self.__thread_check_modules_alive.daemon = True
        self.__thread_check_modules_alive.start()

        self.__thread_recv_modules_alive = threading.Thread(target=self.recv_modules_alive, args=())
        self.__thread_recv_modules_alive.daemon = True
        self.__thread_recv_modules_alive.start()



    def recv_modules_alive(self):
        while True:
            _name = self.__process_recv_alive.recv()
            for _ in self.__threading_pool:
                if _.name == _name:
                    _.last_alive_time = DatetimePlus.get_now_datetime()
                    break

    def check_modules_alive(self):
        while True:
            time.sleep(60)
            try:
                for _p in self.__threading_pool:
                    if (_p.is_alive() == False) or (_p.exitcode != None):
                        self.logger.info('服务[' + _p.name + ']进程已退出 重启中...')
                        self.start_module_by_module_name(_p.name)
            except Exception as e:
                pass
            try:
                for _p in self.__threading_pool:
                    if DatetimePlus.get_diff_minutes(DatetimePlus.get_now_datetime(),_p.last_alive_time) > self.configer.check_service_alive_time:
                        self.logger.info('服务[' + _p.name + ']长时间未响应 重启中...')
                        self.start_module_by_module_name(_p.name)
            except Exception as e:
                pass

    def get_connection_by_module_name(self, module_name):
        for _ in self.__connections:
            if _[0] == module_name:
                return _[1]
        _connection = self.create_module_connection(module_name)
        self.__connections.append((module_name, _connection))
        return _connection

    def create_module_connection(self, module_name):
        return InstanceFactory.create_postgres_connection(True,module_name)

    def get_module_path(self, module_name=''):
        path = self.configer.get_module_path_by_module_name(True, module_name)
        if path == '':
            path = FuncHelper.get_curr_path() + '/Services/' + module_name
        return path

    def create_module_instace(self, module_path, module_name):
        sys.path.append(module_path)
        module = __import__(module_name)
        _module_instance = getattr(module, module_name)()
        _module_instance.connection = self.get_connection_by_module_name(module_name)
        _module_instance.logger = self.logger
        _module_instance.DataPath = self.configer.data_path + module_name + '/'
        _module_instance.configer = self.configer.service_modules[module_name]
        _module_instance.name = module_name
        _module_instance.loopTime = float(self.configer.service_modules[module_name][ConstConfiger.SERVICE_LOOP_TIME])
        queue = multiprocessing.Queue()
        _module_instance.queue = queue
        _module_instance.pipe_send_alive = self.__process_send_alive
        _module_instance.init()
        return queue, _module_instance

    def bingding_service(self):
        for _name in self.configer.service_modules:
            path = self.get_module_path(_name)
            if not os.path.exists(path):
                self.logger.info('服务[' + _name + ']路径' + path + '不存在！')
                continue
            if not self.configer.get_module_is_enable_by_module_name(True, _name):
                continue
            _queue, _module_instance = self.create_module_instace(path, _name)
            self.__modules.append((_module_instance, _name, _queue))

    def start_service(self):
        for instance in self.__modules:
            _p = multiprocessing.Process(target=instance[0].processMain, args=())
            _p.daemon = True
            _p.queue = instance[2]
            _p.name = instance[1]
            _p.last_alive_time = DatetimePlus.get_now_datetime()
            self.__threading_pool.append(_p)
            _p.start()
            self.logger.info('服务模块[' + instance[1] + '] 启动...')

    def stop(self):
        self.logger.info('接收到退出命令,请等待各模块退出...')
        for _p in self.__threading_pool:
            _p.queue.put('end')
            _p.terminate()

        # for _p in self.__threadingPool:
        #     # try:
        #     #     result = os.kill(pr.pid,signal.SIGKILL)
        #     # except Exception as e:
        #     #     #无进程
        #     #     pass
        try:
            for _p in self.__threading_pool:
                cmd = 'kill -9 ' + str(_p.pid)
                os.system(cmd)
        except Exception as e:
            # 无进程
            pass

    def start_module_by_module_name(self, module_name):
        try:
            self.stop_module_by_module_name(module_name)
            path = self.get_module_path(module_name)
            if not os.path.exists(path):
                self.logger.info('服务[' + module_name + ']路径' + path + '不存在！')
                return False
            _queue, _module_instance = self.create_module_instace(path, module_name)
            self.__modules.append((_module_instance, module_name, _queue))
            _p = multiprocessing.Process(target=_module_instance.processMain, args=())
            _p.daemon = True
            _p.queue = _queue
            _p.name = module_name
            _p.last_alive_time = DatetimePlus.get_now_datetime()
            self.__threading_pool.append(_p)
            _p.start()
            self.logger.info('服务模块[' + module_name + '] 启动...')
            return True
        except Exception as e:
            self.logger.error('服务模块[' + module_name + '] 启动失败:' + str(e))
            return False

    def stop_module_by_module_name(self, module_name):
        for _process in self.__threading_pool:
            if _process.name == module_name:
                _tmp_process = _process
                try:
                    cmd = 'kill -9 ' + str(_process.pid)
                    os.system(cmd)
                except Exception as e:
                    # 无进程
                    pass
                self.__threading_pool.remove(_tmp_process)
                break

        for _module in self.__modules:
            if _module[1] == module_name:
                self.__modules.remove(_module)
                break

        for _ in self.__connections:
            if _[0] == module_name:
                self.__connections.remove(_)
                break
        self.logger.info('服务模块[' + module_name + '] 停止...')
        return True

    def check_is_run_by_module_name(self,module_name):
        for _process in self.__threading_pool:
            if _process.name == module_name:
                return True
        return False

    def get_module_state(self):
        _result_arr = []
        for _n in self.configer.service_modules.keys():
            _ = {}
            _['name'] = _n
            _['is_run'] = self.check_is_run_by_module_name(_n)
            _result_arr.append(_)
        return _result_arr