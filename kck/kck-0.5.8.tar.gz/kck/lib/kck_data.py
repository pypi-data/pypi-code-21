from .log import log
from .cassandra_actor import CassandraActor

process_data_singleton = None

class KCKData(CassandraActor):

    _pcol = None
    parameters = None
    cache_obj = None

    @classmethod
    def get_instance(cls, **kwargs):
        global process_data_singleton
        if process_data_singleton is None:
            process_data_singleton = cls(**kwargs)
        return process_data_singleton

    def __init__(self, inhibit_framework_registration=False, cache_obj=None):
        self.primitive_init()
        if cache_obj is None:
            from kck.lib.kck_cache import KCKCache
            self.init(inhibit_framework_registration=inhibit_framework_registration, cache_obj=KCKCache.get_instance(data_obj=self), data_obj=self)
        else:
            self.init(inhibit_framework_registration=inhibit_framework_registration, cache_obj=cache_obj, data_obj=self)

    def register_updater(self, name, updater_obj):
        updater_obj.set_data(self)
        updater_obj.set_cache(self.cache_obj)
        updater_obj.set_name(name)
        self.updaters[name] = updater_obj

    def _updater_obj(self, key):
        ret = self.updater(key.split(self.keysep)[0])
        return ret

    def updater(self, name):
        return self.updaters[name]

    def update(self, keystr, data):
        u = self._updater_obj(keystr)
        u.do_hooks("pre_update", key=keystr, hints=data)
        key_data = u.key_to_param_dict(key_str=keystr)
        key_data.update(data)
        r = u.update(key_data)
        u.do_hooks("post_update", key=keystr, hints=data)
        return dict(success=True)
