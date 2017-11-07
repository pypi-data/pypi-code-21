from smartbotsol import Cache
from smartbotsol import User
from smartbotsol.core.cache import _log

import os, dill, sys
import errno
import logging
from smartbotsol.core.cache import _log
log = logging.getLogger(__name__)

class DictCache(Cache):
    """Users cache store based on dictonary"""

    _cache = {}
    FILE_NAME = 'bot.pkl'
    BACKUP_DIR_PATH = '~/states_backup'
    
    def __str__(self):
        return str(self._cache)
    

    def __init__(self, newdict=None):
        if newdict:
            self._cache.update(newdict)

    @_log
    def get(self, uid):
        return self._cache.setdefault(uid, User(uid))

    def add(self, key, value):
        try:
            assert isinstance(value, User)
            self._cache[key] = value
        except AssertionError as e:
            log.warn(e)
            log.warn('User with id %s, is %s instance, it must be User instance, skip...' % (key, value.__class__.__name__))

    def to_dict(self):
        return self._cache

    @classmethod
    def from_dict(cls, fdict):
        assert isinstance(fdict, dict)
        cache = cls()
        for k,v in fdict.items():
            # if not k == v.uid:
            #     log.warn('User id must be equals store key %s != %s, skip...' % (k, v.uid))
            #     continue
            cache.add(k,v)
        return cache

    def save(self):
        """Save users cache to file"""
        path = os.path.join(DictCache.BACKUP_DIR_PATH, DictCache.FILE_NAME)
        if not os.path.exists(path):
            os.makedirs(path)

        with open(path, 'wb') as f:
            dill.dump(self._cache.keys(), f)
            # dill.dump(len(self._cache.keys()), f)
            # for user_key in self._cache.keys():
            #     dill.dump(self._cache[user_key], f)
            log.debug('All states saved to {}.'.format(path))

    def load(self):
        """Loads users cache from file"""
        path = os.path.join(DictCache.BACKUP_DIR_PATH, DictCache.FILE_NAME)
        try:
            with open(path, 'rb') as f:
                self._cache.update(dill.load(f))
                # # log.debug(str(self._cache))
                # for i in range(dill.load(f)):
                #     user = dill.load(f)
                #     self._cache[user.uid] = user
                log.debug('All states have been loaded from {}.'.format(path))
                # log.debug(str(self._cache))
        except OSError as e:
            log.debug('User_states file isn`t exist! {}'.format(e))
