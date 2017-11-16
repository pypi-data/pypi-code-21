# encoding: utf-8
import logging
import sys

reload(sys)
sys.setdefaultencoding('utf-8')

CONSUME_SUCCESS = 0
CONSUME_REDELIVER = 1
CONSUME_REJECT = 2

logger = logging.getLogger('default')

logger.warning('进程版已经废弃！请使用异步、多线程或者GEVENT版本！')


class Consumer(object):
    pass
