# Copyright (C) 2015 tCell.io, Inc. - All Rights Reserved

from __future__ import unicode_literals
from __future__ import print_function

import logging
import logging.handlers
import threading

import os
import errno

from tcell_agent.tcell_log_formatter import TCellLogFormatter


def mkdir_p(path):
    """http://stackoverflow.com/a/600612/190597 (tzot)"""
    try:
        os.makedirs(path, exist_ok=True)  # Python>3.2
    except TypeError:
        try:
            os.makedirs(path)
        except OSError as exc:  # Python >2.5
            if exc.errno == errno.EEXIST and os.path.isdir(path):
                pass
            else:
                raise


def get_level_from_string(level_string):
    if level_string == "DEBUG":
        return logging.DEBUG
    if level_string == "INFO":
        return logging.INFO
    if level_string == "WARNING":
        return logging.WARNING
    if level_string == "ERROR":
        return logging.ERROR
    if level_string == "CRITICAL":
        return logging.CRITICAL


base_app_firewall_logger = None
base_app_firewall_logger_lock = threading.Lock()


def get_app_firewall_payloads_logger():
    global base_app_firewall_logger

    if not base_app_firewall_logger:
        base_app_firewall_logger_lock.acquire()
        try:
            from tcell_agent.config import CONFIGURATION

            new_logger = logging.getLogger("app_firewall_payloads_logger")
            formatter = logging.Formatter('%(asctime)s - [%(levelname)s]: %(message)s')

            log_filename = CONFIGURATION.app_firewall_payloads_log_filename

            file_handle = logging.handlers.RotatingFileHandler(log_filename, maxBytes=10 * 1024 * 1024, backupCount=5)
            file_handle.setFormatter(formatter)
            new_logger.addHandler(file_handle)

            new_logger.setLevel(logging.INFO)

            base_app_firewall_logger = new_logger
        finally:
            base_app_firewall_logger_lock.release()

    return base_app_firewall_logger


def get_logger():
    from tcell_agent.config import CONFIGURATION
    logging_options = CONFIGURATION.logging_options
    new_logger = logging.getLogger("tcell_agent")
    formatter = TCellLogFormatter(
        fmt='%(asctime)s - %(name)s - [%(tcell_version)s] - %(levelname)s[%(thread_pid)s]: %(message)s')
    new_logger.setLevel(get_level_from_string(logging_options.get("level", "INFO")))

    if logging_options is None or logging_options.get("enabled", True) is False:
        return None

    log_filename = CONFIGURATION.log_filename

    file_handle = logging.handlers.RotatingFileHandler(log_filename, maxBytes=10 * 1024 * 1024, backupCount=5)

    file_handle.setFormatter(formatter)

    new_logger.setLevel(get_level_from_string(logging_options.get("level", "INFO")))
    new_logger.addHandler(file_handle)

    return new_logger


try:
    base_logger
except:
    base_logger = get_logger()
