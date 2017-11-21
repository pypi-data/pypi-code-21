from time import time

CACHE_TIME = 5


class LocalCache(object):
    def __init__(self):
        self.cache = {}

    def update(self, key, value):
        if not (key in self.keys() and time() - self.cache[key]['time'] < CACHE_TIME):
            self.cache.update({key: {'data': value, 'time': time()}})

    def get(self, key):
        return self.cache[key]['data']

    def keys(self):
        return self.cache.keys()

    def __setitem__(self, key, value):
        return self.update(key, value)

    def __getitem__(self, key):
        return self.get(key)
