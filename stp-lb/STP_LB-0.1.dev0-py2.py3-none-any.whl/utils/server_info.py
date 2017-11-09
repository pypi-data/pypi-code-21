#!/usr/bin/env python
#coding: utf-8

import time
import psutil
import threading
from threading import Timer
import logging

class ServerInfoUtil:
    def __init__(self):
        #self._refresh_interval = interval
        self._logger = logging.getLogger('sts_master')

    def get_info(self):
        cpu = psutil.cpu_times_percent()
        mem = psutil.virtual_memory()
        net = psutil.net_io_counters()
        return (cpu, mem, net)

    def refresh(self, interval, func):
        def get_server_stat():
            cpu = psutil.cpu_times_percent()
            mem = psutil.virtual_memory()
            net = psutil.net_io_counters()
            func(cpu, mem, net)
            global server_stat_timer
            server_stat_timer = Timer(interval, get_server_stat)
            server_stat_timer.start()

        server_stat_timer = Timer(interval, get_server_stat)
        server_stat_timer.start()

    def refresh_noblock(self, interval, func):
        self._logger.debug("begin")
        thread = threading.Thread(target=self.refresh, args=(interval, func))
        thread.start()

if __name__ == '__main__':
    u = ServerInfoUtil()
    def dis(cpu, mem, net):
        print(cpu)
        print(mem)
        print(net)
    u.refresh(2, dis)
    print('hello')
    pass
