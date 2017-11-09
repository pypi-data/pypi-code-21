#!/usr/bin/env python
#coding: utf-8

import time
import logging
import pickle
import os
import sys
import importlib
import threading
from threading import Timer
from multiprocessing import Process
#import pickle
try:
        import cPickle as pickle
except ImportError:
        import pickle

try:
    from Queue import Queue
except Exception as e:
    from queue import Queue

from .task import Task
from .sts_manager import StsManager
from ..utils.server_info import ServerInfoUtil
from ..utils.multicast import MulticastUtil
from ..utils.server_communicate_util import ServerCommunicateUtil


class StsSlaver:
    threads = []
    processor_modules = {}
    __logger = logging.getLogger('sts_slaver')
    def __init__(self, lip, lport, rip, rport, auth, mcgrp, mcport, mttl):
        self.dispached_tasks = Queue() 
        self.finished_tasks = Queue()
        self.__server_stat_agent = ServerInfoUtil()
        self.__ip = lip
        self.__port = lport
        self.__server_ip = rip
        self.__server_port = rport
        self.__auth = auth
        self.__mcgrp = mcgrp
        self.__mcport = mcport
        self.__mttl = mttl
        self.__server_comm_util = ServerCommunicateUtil()

    def get_processor_modules(self):
        sys.path.append('%s/..' % os.path.dirname(__file__))
        for processor in os.listdir(os.path.dirname(__file__)+'/../tasks/processor'):
            if '__init__.py' in processor or '__pycache__' in processor:
                continue
            module_name = 'tasks.processor.%s.processor' % processor
            module = importlib.import_module(module_name)
            #print("========processors=======")
            #print(module.Processor.description)
            version = module.Processor.version
            name = module.Processor.name
            #print("========processors=======")
            StsSlaver.processor_modules[name+'-'+version] = module

    def probe_server(self):
        multicast = MulticastUtil(self.__ip, self.__port, self.__mcgrp, self.__mcport, self.__mttl)
        msg = "slaver-probe"
        multicast.send(msg)

    def serve_remote_msg(self):

        class SlaverHandler:
            def __init__(temp, tauth):
                temp.__auth= tauth

            def ping(temp):
                return 'ping ok!!!'

            def get_server_stat(temp):
                self.__server_stat_agent.get_info()

            def notify(temp, ip, port):
                print("notify(ip:%s, port:%d)" % (ip, port))
                StsSlaver.serve_master_task_noblock(ip, port, temp.__auth)
                return 'notify ok'

        handler = SlaverHandler(self.__auth)
        StsSlaver.__logger.debug('thrift server ip: %s, port: %s' % (self.__ip, self.__port))
        self.__server_comm_util.serve(self.__ip, self.__port, handler)

    @staticmethod
    def serve_master_task_noblock(ip, port, auth):
        thread = threading.Thread(target=StsSlaver.serve_master_task, args=(ip, port, auth))
        thread.start()
        StsSlaver.threads.append(thread)

    @staticmethod
    def serve_master_task(ip, port, auth):
        processes = Queue()

        def join_task_processes_refresh(interval):
            def join_task_processes():
                while not processes.empty():
                    p = processes.get(True)
                    p.join()
                    StsSlaver.__logger.debug("join task process: %s" % p.pid)
                global processes_join_timer
                processes_join_timer = Timer(interval, join_task_processes)
                processes_join_timer.start()
            processes_join_timer = Timer(interval, join_task_processes)
            processes_join_timer.start()

        join_task_processes_refresh(5)

        StsManager.register('get_dispatched_local_tasks')
        StsManager.register('get_finished_local_tasks')

        StsSlaver.__logger.debug('Connect to server %s...' % ip)
        manager = StsManager(address=(ip, port), authkey=auth, serializer="xmlrpclib")
        manager.connect()

        dispatched_local_tasks = manager.get_dispatched_local_tasks()
        finished_local_tasks = manager.get_finished_local_tasks()

        while True:
            taskstr = dispatched_local_tasks.get(True)
            print(type(taskstr))
            task = pickle.loads(taskstr if sys.version_info < (3,) else taskstr.encode('utf-8'))
            task_type = task.type  #name-version
            if task_type in StsSlaver.processor_modules:
                func = StsSlaver.processor_modules[task_type].Processor.proc
                StsSlaver.__logger.debug('Run task: %s(priority: %d)' % (task.task_id, task.priority))
                process = Process(target=lambda:task.call(func), args=())
                process.start()
                processes.put(process)
            else:
                StsSlaver.__logger.debug('no such task type!!!')
            #process.join()
            #task.call(func)
            time.sleep(1)
            #finished_local_tasks.put(task)

    def start(self):
        self.get_processor_modules()
        thread = threading.Thread(target=self.serve_remote_msg, args=())
        thread.start()
        time.sleep(3)
        if self.__server_ip is None or self.__server_port is None:
            self.probe_server()
        else:
            self.serve_master_task_noblock(self.__server_ip, self.__server_port, self.__auth)
        StsSlaver.threads.append(thread)

        for thread in StsSlaver.threads:
            thread.join()


if __name__ == '__main__':
    slave = StsSlaver('127.0.0.1', 8888, 'mykey')
    slave.start()

