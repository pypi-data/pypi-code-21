# encoding: utf-8

import logging
import logging.config
import os
import platform

APP_NAME = 'DefaultCtecConsumer'
LOG_PATH = '/'
DEBUG = False


def get_logger(app_name=None, log_path=None, debug=None):
    global APP_NAME, LOG_PATH, DEBUG

    APP_NAME = app_name if app_name else APP_NAME
    LOG_PATH = log_path if log_path else LOG_PATH
    DEBUG = debug if debug else DEBUG

    __PREFIX = 'C:\BllLogs' if platform.system() == 'Windows' else '%s/%s/%s' % (
        LOG_PATH.rstrip('/'), APP_NAME.strip('/'), os.getpid())

    # 日志文件路径
    __LOG_PATH_DEBUG = r'%s\debug.log' % __PREFIX if platform.system() == 'Windows' else '%s/debug.log' % __PREFIX
    __LOG_PATH_INFO = r'%s\info.log' % __PREFIX if platform.system() == 'Windows' else '%s/info.log' % __PREFIX
    __LOG_PATH_WARN = r'%s\warn.log' % __PREFIX if platform.system() == 'Windows' else '%s/warn.log' % __PREFIX
    __LOG_PATH_ERROR = r'%s\error.log' % __PREFIX if platform.system() == 'Windows' else '%s/error.log' % __PREFIX

    # 判断目录是否存在，若不存在则创建
    if not os.path.exists(__PREFIX):
        os.makedirs(__PREFIX)

    # 日志配置
    __LOGGING_CONFIG = {
        'version': 1,
        'disable_existing_loggers': True,
        'formatters': {
            'standard': {
                'format': '[%(asctime)s] %(levelname)s::(%(process)d %(thread)d)::%(module)s(%(funcName)s:%(lineno)d): %(message)s'
            },
        },
        'handlers': {
            'error': {
                'class': 'logging.handlers.TimedRotatingFileHandler',
                'level': 'ERROR',
                'formatter': 'standard',
                'filename': __LOG_PATH_ERROR + '_file',
                'when': 'H',
                'interval': 1
            },
            'warn': {
                'class': 'logging.handlers.TimedRotatingFileHandler',
                'level': 'WARN',
                'formatter': 'standard',
                'filename': __LOG_PATH_WARN + '_file',
                'when': 'H',
                'interval': 1
            },
            'info': {
                'class': 'logging.handlers.TimedRotatingFileHandler',
                'level': 'INFO',
                'formatter': 'standard',
                'filename': __LOG_PATH_INFO + '_file',
                'when': 'H',
                'interval': 1
            },
            'debug': {
                'class': 'logging.handlers.TimedRotatingFileHandler',
                'level': 'DEBUG',
                'formatter': 'standard',
                'filename': __LOG_PATH_DEBUG + '_file',
                'when': 'H',
                'interval': 1
            }
        },
        'loggers': {
            'default': {
                'handlers': ['debug', 'info', 'warn', 'error'],
                'level': 'INFO',
                'propagate': True
            },
            'enable_debug': {
                'handlers': ['debug', 'info', 'warn', 'error'],
                'level': 'DEBUG',
                'propagate': True
            }
        }
    }

    logging.config.dictConfig(__LOGGING_CONFIG)
    if DEBUG:
        return logging.getLogger('enable_debug')
    else:
        return logging.getLogger('default')
