#! /usr/bin/env python
# coding: utf-8

import os
import logging
from logging.handlers import TimedRotatingFileHandler
from JYAliYun import DATETIME_FORMAT, LOG_MSG_FORMAT, DEFAULT_LOGGER_NAME, HOSTNAME
from JYAliYun.Tools import ConfigManager, ConvertObject, ali_headers, get_environ
from JYAliYun.AliYunAccount import RAMAccount

__author__ = 'ZhouHeng'


# logging.basicConfig(level=logging.DEBUG, format=LOG_MSG_FORMAT, datefmt=DATETIME_FORMAT)


class ObjectManager(object):
    PRODUCT = ""

    def __init__(self, *args, **kwargs):
        if "cfg" in kwargs:
            if isinstance(kwargs["cfg"], ConfigManager):
                self.cfg = kwargs["cfg"]
        else:
            self.cfg = ConfigManager(product=self.PRODUCT, **kwargs)
        self.server_url = None
        self.access_key_id = ""
        self.access_key_secret = ""
        self.is_internal = False
        self.ram_account = None
        self.disabled_log = False
        if "ram_account" in kwargs:
            ram_account = kwargs["ram_account"]
            assert isinstance(ram_account, RAMAccount)
            self.ram_account = ram_account
        else:
            self.ram_account = RAMAccount(conf_path=self.cfg.conf_path)
        if "disabled_log" in kwargs:
            self.disabled_log = kwargs["disabled_log"]
            assert isinstance(self.disabled_log, bool)
        if len(args) > 0:
            ram_account = args[0]
            if isinstance(ram_account, RAMAccount):
                self.ram_account = ram_account
        if self.ram_account is not None:
            self.ram_account.assign_account_info(self)

        self.env = self.cfg.get("env", "")
        current_env = get_environ("ENV")
        if current_env is None:
            current_env = HOSTNAME
        if self.env == "":
            self.env = current_env
        else:
            self.env = "%s_%s" % (current_env, self.env)
        self.logger_name = DEFAULT_LOGGER_NAME
        if "logger_name" in kwargs:
            self.logger_name = kwargs["logger_name"]
        self.logger = logging.getLogger(self.logger_name)
        self.init_logging()

    def init_logging(self):
        if self.disabled_log is True:
            return
        logging_dir = self.cfg.get("logging_dir", "")
        logging_name = self.cfg.get("logging_name", self.logger_name.lower())
        filename = os.path.join(logging_dir, logging_name)
        try:
            fmt = logging.Formatter(LOG_MSG_FORMAT, DATETIME_FORMAT)
            log = TimedRotatingFileHandler(filename=filename, when='W0', interval=4)
            log.setLevel(logging.INFO)
            log.suffix = "%Y%m%d_%H%M.log"
            log.setFormatter(fmt)
            self.logger.addHandler(log)
        except Exception as e:
            self.logger.error(e.message)

    def set_server_url(self, server_url):
        self.server_url = server_url

    def set_access_key_id(self, access_key_id):
        self.access_key_id = access_key_id

    def set_access_key_secret(self, access_key_secret):
        self.access_key_secret = access_key_secret

    def set_is_internal(self, is_internal):
        self.is_internal = is_internal

    def set_env(self, env):
        self.env = env

    @staticmethod
    def _join_array_str(a, join_str):
        r_a = ""
        if isinstance(a, tuple) or isinstance(a, list):
            for item in a:
                r_a += ObjectManager._join_array_str(item, join_str) + join_str
        else:
            r_a += ConvertObject.decode(a)
        return r_a

    @staticmethod
    def _handler_log_msg(message, *args):
        message = ObjectManager._join_array_str(message, " ")
        if len(args) >= 0:
            message += "\n" + ObjectManager._join_array_str(args, "\n")
        return message

    def error_info(self, message, *args):
        message = self._handler_log_msg(message, *args)
        self.logger.error(message)

    def waring_log(self, message, *args):
        message = self._handler_log_msg(message, *args)
        self.logger.warning(message)

    def info_log(self, message, *args):
        message = self._handler_log_msg(message, *args)
        self.logger.info(message)

    def ali_headers(self, request_method, resource, headers=None, content_md5=None, content_type=None, **kwargs):
        return ali_headers(self.access_key_id, self.access_key_secret, request_method, content_md5, content_type,
                           headers, resource, product=self.PRODUCT, **kwargs)
