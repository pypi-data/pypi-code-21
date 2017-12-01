import os
import sys
import signal
import random
import logging
import traceback

from redis import Redis
from itertools import repeat
from argparse import ArgumentParser

from .logger import Logger
from .settings import SettingsWrapper
from .daemon_ctl import common_stop_start_control

__all__ = ["ParallelMonitor", "LoggingMonitor"]


class ParallelMonitor(object):
    """
    支持多线程多进程统一管理
    """
    alive = True
    name = "parallel_monitor"
    children = []
    int_signal_count = 1

    def __init__(self):
        self.open()

    def set_logger(self, logger=None):
        if not logger:
            self.logger = logging.getLogger(self.name)
            self.logger.setLevel(10)
            self.logger.addHandler(logging.StreamHandler(sys.stdout))
        else:
            self.logger = logger
            self.name = logger.name

    def stop(self, *args):
        if self.int_signal_count > 1:
            self.logger.info("force to terminate...")
            for th in self.children[:]:
                self.stop_child(th)
            pid = os.getpid()
            os.kill(pid, 9)

        else:
            self.alive = False
            self.logger.info("close process %s..." % self.name)
            self.int_signal_count += 1

    def open(self):
        signal.signal(signal.SIGINT, self.stop)
        signal.signal(signal.SIGTERM, self.stop)

    def stop_child(self, child):
        pass


class LoggingMonitor(object):
    """
    内建Logger和Settings的ParallelMonitor
    """
    name = "logging_monitor"
    wrapper = SettingsWrapper()
    _logger = None

    def __init__(self, settings):
        if isinstance(settings, dict):
            self.settings = settings
        else:
            self.settings = self.wrapper.load(default=settings)

    def set_logger(self, logger=None):
        self._logger = logger

    @property
    def logger(self):
        if not self._logger:
            self._logger = Logger.init_logger(self.settings, self.name)
        return self._logger

    def log_err(self, func_name, *args):
        self.logger.error("Error in %s: %s. "%(func_name, "".join(traceback.format_exception(*args))))
        return True


class Service(LoggingMonitor, ParallelMonitor):
    """
        可执行程序，支持守护进程启动
    """
    name = "Service"
    parser = None

    def __init__(self):
        self.args = self.parse_args()
        super(Service, self).__init__(self.args.settings)

    def enrich_parser_arguments(self):
        self.parser.add_argument("-d", "--daemon", help="Run backend. ")
        self.parser.add_argument("-s", "--settings", help="Settings. ", default="settings.py")

    def parse_args(self, daemon_log_path='/dev/null'):
        self.parser = ArgumentParser(conflict_handler="resolve")
        self.enrich_parser_arguments()
        return common_stop_start_control(self.parser, daemon_log_path, 2)


class ProxyPool(LoggingMonitor):
    """
        Redis代理池
    """
    def __init__(self, settings):
        """
        proxy_sets指定多个redis set,随机选取proxy
        proxy
        :param settings:
        """
        super(ProxyPool, self).__init__(settings)
        self.protocols = self.settings.get("PROTOCOLS", "http,https").split(",")
        self.redis_conn = Redis(self.settings.get("REDIS_HOST"), self.settings.get_int("REDIS_PORT", 6379))
        self.proxy_sets = self.settings.get("PROXY_SETS", "proxy_set").split(",")
        self.account_password = self.settings.get("PROXY_ACCOUNT_PASSWORD")
        self.proxy = {}

    def proxy_choice(self):
        """
        顺序循环选取代理
        :return: 代理
        """
        proxy = self.redis_conn.srandmember(random.choice(self.proxy_sets))
        if proxy:
            proxy_str = "http://%s%s"%(self.account_password+"@"if self.account_password else "", proxy.decode())
            self.proxy = dict(zip(self.protocols, repeat(proxy_str)))
        return self.proxy
