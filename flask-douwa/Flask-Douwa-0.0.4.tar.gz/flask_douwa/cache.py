import redis
from datetime import datetime


class RedisCache(object):
    """ Redis操作函数 """

    def connect(self, host, port, db):
        pool = redis.ConnectionPool(host=host,
                                    port=port,
                                    db=db,
                                    decode_responses=True)
        self.r = redis.Redis(connection_pool=pool)

    def set(self, key, value, expired=None):
        if isinstance(value, str):
            if expired and isinstance(expired, datetime):
                dif = expired - datetime.now()
                seconds = int(dif.total_seconds())
                if seconds < 0:
                    seconds = 0
                expired = seconds
            else:
                expired = None

            self.r.set(key, value, ex=expired)

    def get(self, key):
        return self.r.get(key)

    def ttl(self, key):
        return self.r.ttl(key)

    def expire(self, key, time):
        return self.r.expire(key, time)

    def sadd(self, name, value):
        return self.r.sadd(name, value)

    def smembers(self, name):
        return self.r.smembers(name)

    def delete(self, name):
        self.r.delete(name)
