#!/usr/bin/env python
#coding: utf-8

import os
import sys
import uuid
import json
import random
import time
import psutil
import importlib
import threading
import logging
from threading import Timer
#import pickle
try:
    import cPickle as pickle
except ImportError:
    import pickle
try:
    from Queue import PriorityQueue
except Exception as e:
    from queue import PriorityQueue

from .task import Task
from .sts_manager import StsManager 
from ..utils.ip_util import IpUtil
from ..utils.multicast import MulticastUtil
from ..utils.server_info import ServerInfoUtil
from ..utils.server_communicate_util import ServerCommunicateUtil
from ..web.api import ApiServer


class StsMaster:
    __logger = logging.getLogger('sts_master')
    def __init__(self, srt, task_ip, task_port, task_auth, ip, port, mcgrp, mcport, mttl, apiip, apiport):
        self.dispatched_local_tasks = PriorityQueue()
        self.finished_local_tasks = PriorityQueue()
        self.__tasks_map = {}
        self.__apiip = apiip
        self.__apiport = apiport
        self.__apiserver = ApiServer(apiip, apiport)
        self.__stat_refresh_interval = srt
        self.__task_ip = task_ip
        self.__task_port = task_port
        self.__task_auth = task_auth
        self.__multicast_agent = MulticastUtil(ip, port, mcgrp, mcport, mttl)
        self.__server_stat_agent = ServerInfoUtil()
        self.__util_ip = ip
        self.__util_port = port
        self.__server_comm_util = ServerCommunicateUtil()
        self.__slavers = []
        self.__threads = []
        self.__processor_modules = {}
        StsManager.register('get_dispatched_local_tasks', callable=lambda:self.dispatched_local_tasks)
        StsManager.register('get_finished_local_tasks', callable=lambda:self.finished_local_tasks)
        self.__manager = StsManager(address=(self.__task_ip, self.__task_port), authkey=self.__task_auth, serializer="xmlrpclib")
        self.__manager.start()

    def get_processor_modules(self):
        sys.path.append('%s/..' % os.path.dirname(__file__))
        for processor in os.listdir(os.path.dirname(__file__)+'/../tasks/processor'):
            if '__init__.py' in processor or '__pycache__' in processor:
                continue
            module_name = 'tasks.processor.%s.processor' % processor
            module = importlib.import_module(module_name)
            #print("========processors=======")
            #print(module.Processor.description)
            #print("========processors=======")
            self.__processor_modules[processor] = module
        return {k: {
                    'version': v.Processor.version.strip(),
                    'desc': v.Processor.description.strip(),
                    'submit_format': v.Processor.submit_format.strip(),
                    'response_format': v.Processor.response_format.strip(),
                   }  for k, v in self.__processor_modules.items()}

    def serve_remote_msg(self):
        pass

    def serve_probe(self):
        def process_msg(data, addr):
            StsMaster.__logger.debug('multicast recv: %s ip: %s port: %s' % (data, addr[0], addr[1]))
            StsMaster.__logger.debug('task_ip: %s, task_port: %s' % (self.__task_ip, self.__task_port))
            print('data:[%s]' % data.decode('utf-8'))
            if 'slaver-probe' in data.decode('utf-8'):
                print("-----slaver-probe-----")
                try:
                    task_ip = IpUtil.get_ip_by_if('em1')
                except Exception as e:
                    task_ip = IpUtil.get_ip_by_if('eth0')

                self.__server_comm_util.call('notify', addr[0], addr[1], task_ip,  self.__task_port)
                self.__slavers.append(addr)
            elif data == 'master-probe':
                pass
            else:
                print('the data is %s' % data)
            #print('=====addr=====')
            #print(addr)
            #print('=====addr=====')
            #self.__server_comm_util.call('ping', addr[0], addr[1])

        #StsMaster.__logger.debug("before call multicast agent")
        thread = threading.Thread(target=self.__multicast_agent.serve, args=(process_msg,))
        #self.__multicast_agent.serve_noblock(process_msg)
        thread.start()
        self.__threads.append(thread)
        #StsMaster.__logger.debug("after call multicast agent")

    def server_info_update(self):
        def process_info(cpu, mem, net):
            StsMaster.__logger.debug(cpu)
            StsMaster.__logger.debug(mem)
            StsMaster.__logger.debug(net)
            StsMaster.__logger.debug(self.__slavers)
        thread = threading.Thread(target=self.__server_stat_agent.refresh, args=(self.__stat_refresh_interval, process_info))
        thread.start()
        self.__threads.append(thread)
        #self.__server_stat_agent.refresh_noblock(self.__stat_refresh_interval, process_info)

    def serve_tasks_noblock(self):
        thread = threading.Thread(target=self.serve_tasks, args=())
        thread.start()
        self.__threads.append(thread)

    def add_task(self, task_type, data):
        task_id = uuid.uuid1().hex
        task = Task(task_id, random.randint(1, 100), task_type, data)
        dispatched_local_tasks = self.__manager.get_dispatched_local_tasks()
        StsMaster.__logger.debug("Dispatch local task: %s" % task_id)
        try:
            taskstr = pickle.dumps(task)
            print('master dumps put: ')
            print(type(taskstr))
            dispatched_local_tasks.put(taskstr if sys.version_info > (3,) else taskstr.encode('utf-8'))
            self.__tasks_map[task_id] = task
        except Exception as e:
            self.__manager.shutdown()
            StsMaster.__logger.error(e)
        return task

    def get_task(self, task_id):
        task = self.__tasks_map.get(task_id, None)
        if task is not None:
            task = json.dumps(task, default=lambda obj:obj.__dict__, sort_keys=True) 
        return task

    def get_all_task(self):
        return {k: json.dumps(v, default=lambda obj:obj.__dict__, sort_keys=True) for k, v in self.__tasks_map.items()}

    def serve_tasks(self):
        dispatched_local_tasks = self.__manager.get_dispatched_local_tasks()
        finished_local_tasks = self.__manager.get_finished_local_tasks()

        task_id = 0

        try:
            while True:
                #while not dispatched_local_tasks.empty():
                    #task = finished_local_tasks.get(True)
                    #StsMaster.__logger.debug("Finished local task: %s" % task.task_id)
                time.sleep(2)
        except Exception as e:
            self.__manager.shutdown()
            StsMaster.__logger.error(e.message)

    def serve_api(self):
        thread = threading.Thread(target=self.__apiserver.serve, args=(self,))
        thread.start()
        self.__threads.append(thread)

    def start(self):
        self.get_processor_modules()
        self.serve_probe()
        self.serve_tasks_noblock()
        #self.server_info_update()
        self.serve_api()
        StsMaster.__logger.debug('wait to join threads in main thread!')

        for thread in self.__threads:
            thread.join()
        
        
if __name__ == '__main__':
    #master = StsMaster('0.0.0.0', 8888, 'mykey', '0.0.0.0', 8889, 'myrkey')
    #master.start()
    #master.server_stat_refresh()
    pass
