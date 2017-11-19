
import os
import redis

# ELK_SERVER = os.environ['ELK_SERVER']
# ELK_PASSWORD = os.environ['ELK_PASSWORD']
# REDIS_SERVER = os.environ['REDIS_SERVER']
# REDIS_PASSWORD = os.environ['REDIS_PASSWORD']
REDIS_LIST_KEY = 'logstash'

class Logging(object):
  def __init__(self, options, tag=None, stdout=True):
    self.redis_server = options['REDIS_SERVER']
    self.redis_password = options['REDIS_PASSWORD']
    # self.elk_server = options['ELK_SERVER']
    # self.elk_password = options['ELK_PASSWORD']
    self.rconn = redis.StrictRedis(self.redis_server, port=6379, password=self.redis_password)
    self.stdout = stdout
    self.tag = tag

  def log(self, level, message):
    msg = {}
    msg['level'] = level
    msg['tag'] = self.tag
    msg['message'] = message
    if self.stdout:
      print(level + ':' + str(message))
    self.rconn.lpush(REDIS_LIST_KEY, msg)

  def debug(self, message):
    self.log('DEBUG', message)

  def info(self, message):
    self.log('INFO', message)

  def warn(self, message):
    self.log('WARN', message)

  def error(self, message):
    self.log('ERROR', message)

