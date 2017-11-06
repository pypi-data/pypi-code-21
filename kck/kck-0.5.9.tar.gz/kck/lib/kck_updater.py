import inspect
import os
import pkgutil
import importlib

import sys

# from kck.lib.kck_data import KCKData
from .kck_database import KCKDatabase
# from .kck_primer import KCKPrimer
from .config import kck_config_lookup
from .framework_actor import FrameworkActor



class KCKUpdater(FrameworkActor):

    name = None
    database = None
    parameters = None
    query_template = None
    data_type = "string"

    @classmethod
    def register_updaters(cls, data_obj):

        # from kck.lib.kck_data import KCKData
        # data_obj = KCKData.get_instance()

        def proc_updater_class(updater_name, cls):
            data_obj.register_updater(updater_name, cls)

        above_dirpath = cls.make_relpath_absolute(
            os.path.join(
                cls.make_relpath_absolute(kck_config_lookup("kck", "updaters_dirpath")),
                '..'
            )
        )
        if above_dirpath not in sys.path:
            sys.path.insert(0, above_dirpath)

        sp = sys.path
        # import kupdaters
        kupdaters = importlib.import_module("kupdaters")

        for loader, name, ispkg in pkgutil.iter_modules(kupdaters.__path__):
            m = loader.find_module(name).load_module(name)
            for n, c in inspect.getmembers(m, inspect.isclass):
                if not issubclass(c, KCKUpdater) or c.__name__ == "KCKUpdater":
                    continue
                proc_updater_class(name, c())

    def _typed_data(self, d):
        ret = d
        transform = dict(
            string=lambda x: str(x),
            float=lambda x: float(x),
            int=lambda x: int(x)
        )
        if self.data_type in transform:
            return transform[self.data_type](ret)
        return ret

    def update(self, data, queued=False):
        prim_key_param_name = self.primary_key_parameter_name()
        ret = KCKDatabase.query(
            self.database,
            self.query_template["update" if prim_key_param_name in data else "insert"],
            data
        )
        return ret


