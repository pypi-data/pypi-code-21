from redis import ConnectionPool, StrictRedis
from functools import wraps
import logging
import NodeDefender

logger = logging.getLogger('Redis')
logger.setLevel('INFO')
logger.addHandler(NodeDefender.loggHandler)

class LocalStorage:
    def __init__(self):
        self.h = {}
        self.s = {}

    def hmset(self, key, **values):
        try:
            self.h[key].update(values)
        except KeyError:
            self.h[key] = values
        return self.h[key]

    def hgetall(self, key):
        try:
            return self.h[key]
        except KeyError:
            return {}

    def hkeys(self, key):
        try:
            return set(self.h[key])
        except KeyError:
            return set()

    def hdel(self, key, **values):
        for value in values:
            try:
                self.h[key].pop(value)
            except KeyError:
                pass
        return True

    def sadd(self, key, value):
        try:
            self.s[key].add(value)
        except KeyError:
            self.s[key] = set()
            self.s[key].add(value)
        return self.s[key]

    def smembers(self, key):
        try:
            return self.s[key]
        except KeyError:
            return set()

    def srem(self, key, value):
        try:
            self.s[key].remove(value)
        except KeyError:
            return False
        return self.s[key]

if NodeDefender.config.redis.enabled():
    host = NodeDefender.config.redis.host()
    port = NodeDefender.config.redis.port()
    db = NodeDefender.config.redis.database()
    pool = ConnectionPool(host=host, port=int(port), db=db, decode_responses=True)
    conn = StrictRedis(connection_pool=pool)
else:
    conn = LocalStorage()

def redisconn(func):
    @wraps(func)
    def wrapper(*args, **kwargs):
        return func(*args, conn = conn, **kwargs)
    return wrapper

from NodeDefender.db.redis import icpe, sensor, field, mqtt
