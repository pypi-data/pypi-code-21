import inspect
import os
import pkgutil
import sys

from kck.lib.exceptions import PrimerComputerReturnedNoResults
from .config import kck_config_lookup
from .kck_database import KCKDatabase
from .framework_actor import FrameworkActor

SCRIPT_DIRPATH = os.path.dirname(os.path.realpath(__file__))
KCK_SOURCES_DIRPATH = os.path.join(SCRIPT_DIRPATH, "..")

QUERY_TYPE_ROWS = 1
QUERY_TYPE_DICTS = 2

def refresh_for_param_dict_list(primer_obj, param_dict_list):
    cache_obj = primer_obj.get_cache()
    for param_dict in param_dict_list:
        cache_obj.refresh(
            key="{}{}{}".format(primer_obj.name, primer_obj.keysep, primer_obj.param_dict_to_key(param_dict)),
            hints=None,
            queued=True
        )


class KCKPrimer(FrameworkActor):
    keys = None
    database = None
    expire = None
    query_template = None
    query_type = QUERY_TYPE_ROWS
    result_filter = None
    domain_key = None
    processes = {
        "refresh__over_domain": {
            "type": "key",
            "key_attribute": "domain_key",
            "hooks": {
                "pre": None,
                "value": [refresh_for_param_dict_list],
                "post": None,
            }
        }
    }

    def __str__(self):
        return "{}: [keys: {}, database: {}, parameters: {}, expire: {}, qrytmpl: {}]".format(
            self.__class__,
            self.keys,
            self.database,
            self.parameters,
            self.expire,
            self.query_template
        )

    def refresh(self, keystr):
        pass

    def compute(self, keystr):

        ret = []

        if self.query_type == QUERY_TYPE_ROWS:
            ret = [ list(x) for x in KCKDatabase.query(
                self.database,
                self.query_template,
                self.key_to_param_dict(keystr)
            ).fetchall() ]

        if self.query_type == QUERY_TYPE_DICTS:
            res = KCKDatabase.query(
                self.database,
                self.query_template,
                self.key_to_param_dict(keystr)
            )

            while True:

                row = res.fetchone()
                if row is None:
                    break
                rowdict = dict(zip(row.keys(), row.values()))


                ret.append(rowdict)

            res.close()

        if self.result_filter is not None:
            ret = self.result_filter(ret)

        if ret is None or not bool(ret):
            raise PrimerComputerReturnedNoResults
        return ret

    @classmethod
    def register_primers(cls, cache_obj):

        def proc_primer_instance(primer_name, primer_obj):
            cache_obj.register_primer(primer_name, primer_obj)

        # register the path one level up from the primers dirpath as a python library path
        above_dirpath = cls.make_relpath_absolute(
            os.path.join(
                cls.make_relpath_absolute(kck_config_lookup("kck", "primers_dirpath")),
                '..'
            )
        )
        if above_dirpath not in sys.path:
            sys.path.append(above_dirpath)

        # import the kprimers module, instantiate each primer class found and register it with the cache instance
        import kprimers
        for loader, name, ispkg in pkgutil.iter_modules(kprimers.__path__):
            m = loader.find_module(name).load_module(name)
            for n, c in inspect.getmembers(m, inspect.isclass):
                if not issubclass(c, KCKPrimer) or c.__name__ == "KCKPrimer":
                    continue
                proc_primer_instance(name, c())

