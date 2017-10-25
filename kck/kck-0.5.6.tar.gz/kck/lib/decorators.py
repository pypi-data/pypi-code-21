from kck.lib.kck_cache import KCKCache
from kck.lib.kck_primer import KCKPrimer
import types

def NoDataAvailable(Exception):
    key = None

    def __init__(self, key):
        self.key = key

def get_decorator_primer(keys, compute_func):

    def compute_with_self_and_args(self, keystr):
        args = keystr.split(KCKCache.keysep)[1:]
        return compute_func(*args)

    p = KCKPrimer()
    p.keys = keys
    p.compute = types.MethodType(compute_with_self_and_args, p)
    return p

class kckprime:

    dargs = None
    dkwargs = None

    def __init__(self, *args, **kwargs):
        self.dargs = args
        self.dkwargs = kwargs

    def __call__(self, f, *args, **kwargs):

        def cache_lookup(*args, **kwargs):
            cache_obj = KCKCache.get_instance()
            key = "{}{}{}".format(self.dkwargs["name"],cache_obj.keysep,cache_obj.keysep.join(args))
            response = cache_obj.get(key)
            if bool(response["success"]):
                return response["value"]
            raise NoDataAvailable(key)

        def df(*args, **kwargs):
            # set up primer
            keys = self.dkwargs["keys"]
            name = self.dkwargs["name"]

            cache_obj = KCKCache.get_instance()
            if not cache_obj.primer_registered(name):
                cache_obj.register_primer(name, get_decorator_primer(keys, f))

            return cache_lookup(*args, **kwargs)

        return df

class kckrefresh:
    dargs = None
    dkwargs = None

    def __init__(self, *args, **kwargs):
        self.dargs = args
        self.dkwargs = kwargs

    def __call__(self, f, *args, **kwargs):
        def df(*args, **kwargs):
            ret =  f(*args, **kwargs)

            param_dict = {}
            for compute_param_name, param_name in self.dkwargs["param_keys"].items():
                param_dict[compute_param_name] = kwargs[param_name]

            key_param_list = []
            for param_name in self.dkwargs["keys"]:
                key_param_list.append(param_dict[param_name])

            cache_obj = KCKCache.get_instance()
            name = self.dkwargs["name"]
            keys = self.dkwargs["keys"]
            if not cache_obj.primer_registered(name):
                cache_obj.register_primer(name, get_decorator_primer(keys, self.dkwargs["compute"]))

            refresh_key = "{}{}{}".format(self.dkwargs["name"], cache_obj.keysep, cache_obj.keysep.join(key_param_list))
            cache_obj.refresh(refresh_key)

            return ret

        return df
