import os
import random
import zlib
import pickle

import datetime

from .config import kck_config_lookup
from .exceptions import PrimerComputerReturnedNoResults, KCKKeyNotSetException, KCKKeyNotRegistered, KCKUnknownKey
from .cassandra_actor import CassandraActor

SCRIPT_DIRPATH = os.path.dirname(os.path.realpath(__file__))
KCK_SOURCES_DIRPATH = os.path.join(SCRIPT_DIRPATH, "..")

process_cache_singleton = None


class KCKCache(CassandraActor):

    prime_on_cache_miss = False
    tpickle = False
    tcompress = False

    def __init__(
        self,
        inhibit_framework_registration=False,
        key_string_sep="/",
        serialize=True,
        compress=True,
        data_obj=None
    ):
        self.primitive_init()
        if data_obj is None:
            from .kck_data import KCKData
            self.init(
                inhibit_framework_registration=inhibit_framework_registration,
                cache_obj=self,
                data_obj=KCKData.get_instance(cache_obj=self)
            )
        else:
            self.init(
                inhibit_framework_registration=inhibit_framework_registration,
                cache_obj=self,
                data_obj=data_obj
            )

        self.prime_on_cache_miss = kck_config_lookup("kck", "prime_on_cache_miss")
        self.keysep = key_string_sep

        self.tpickle = serialize
        self.tcompress = compress

    @classmethod
    def get_instance(cls, **kwargs):
        global process_cache_singleton
        if process_cache_singleton is None:
            process_cache_singleton = cls(**kwargs)
        return process_cache_singleton

    @staticmethod
    def gen_new_version():
        """returns a new random integer to be used for versioning"""
        minver = -2147483648
        maxver = 2147483647
        return random.randint(minver, maxver)

    def set(self, key, val, expire=None):
        """places a cache entry in the primary cache with key=key and value=val"""
        self._primcache_put(key, val, expire=expire)

    def get(self, key):
        """given a key, try to find a corresponding value in the primary cache. failing that,
           try to find the corresponding value in the secondary cache. failing that, if
           self.prime_on_cache_miss is True, call the primer"""
        try:
            return self._primcache_get(key)

        except KCKKeyNotSetException:

            # if kck is depending on the val cached in the
            # secondary cache, it's time to refresh
            # self.refresh(key, queued=True)

            if not self.prime_on_cache_miss:

                ret = self._seccache_get(key)
                self.refresh(key, queued=True)
                return ret

            try:
                ret = self._seccache_get(key)
                self.refresh(key, queued=True)
                return ret

            except KCKKeyNotSetException:
                try:
                    return self._prime(key)
                except PrimerComputerReturnedNoResults:
                    raise KCKKeyNotSetException(key, self.prim_cache_name, msg="primer found, but compute() returned no results")


    def refresh(self, key, hints=None, queued=False):

        if bool(queued):

            if hints is not None and type(hints) is dict:
                hints["modified"] = datetime.datetime.utcnow()

            return self.raw_queue_refresh(key=key, hints=hints)

        print("refreshing key: {}".format(key))
        ret =  self._prime(key, hints=hints)
        return ret

    def primer_registered(self, name):
        return bool(name in self.primers)

    def register_primer(self, name, primer_obj):
        print("registering primer: {}".format(name))
        primer_obj.set_cache(self)
        primer_obj.set_data(self.data_obj)
        primer_obj.set_name(name)
        self.primers[name] = primer_obj



    def _prime(self, key, hints=None):

        try:
            p = self.primer_obj(key)

            p.do_hooks("pre_prime", key=key)

            primed_val = p.compute(key)

        except KCKKeyNotRegistered:
            raise KCKUnknownKey(key)

        ret = self._primcache_put(key, primed_val, p.expire)
        self._seccache_put(key, primed_val, p.expire)

        p.do_hooks("post_prime", key=key, hints=ret)

        return ret

    def _primcache_get(self, key):
        return self._cache_get(key, self.prim_cache_name)

    def _seccache_get(self, key):
        return self._cache_get(key, self.sec_cache_name)

    def _primcache_put(self, key, val, expire=None):
        return self._cache_put(key, self.prim_cache_name, val, expire=expire)

    def _seccache_put(self, key, val, expire=None):
        return self._cache_put(key, self.sec_cache_name, val, expire=expire)

    def _cache_get(self, key, tbl):

        def decomprickle(val):
            ret = val
            # print("decom ret[{}]: {}".format(type(ret), ret))
            if self.tcompress:
                ret = zlib.decompress(ret)
            if self.tpickle:
                ret = pickle.loads(ret)["d"]
            return ret

        raw_get_result = self.raw_cache_get(key, tbl)

        try:
            return dict(success=True, version=raw_get_result[0][1], key=key, value=decomprickle(raw_get_result[0][0]), tbl=tbl, modified=raw_get_result[0][2])
        except IndexError:
            raise KCKKeyNotSetException(key, tbl)

    def _cache_put(self, key, tbl, val, version=None, check_last_version=None, expire=None):
        
        def comprickle(v):
            nv = v
            if self.tpickle:
                nv = pickle.dumps({"d": nv})
            if self.tcompress:
                nv = zlib.compress(nv)
            return nv

        new_version = version if version is not None else self.gen_new_version()

        newval = comprickle(val)

        current_timestamp = datetime.datetime.utcnow()

        self.raw_cache_put(key, tbl, newval, version=new_version, check_last_version=check_last_version, expire=expire, modified=current_timestamp)
        ret = dict(success=True, version=new_version, key=key, value=val, tbl=tbl, modified=current_timestamp)
        return ret

    def _cache_delete(self, key, tbl):
        self.raw_cache_delete(key, tbl)
        return dict(success=True, key=key, tbl=tbl)

