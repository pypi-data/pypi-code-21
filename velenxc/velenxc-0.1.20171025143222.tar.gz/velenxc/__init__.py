import datetime
import inspect
import os
from importlib import import_module
from itertools import chain

__version__ = '0.1.' + datetime.datetime.today().strftime('%Y%m%d%H%M%S')


class LazyLoading(object):
    func_parent_modules = [
        'velenxc.funclibs'
    ]

    def __init__(self):
        self._installed_dotted_path = []
        self._installed_modules = []
        self._loaded_funcs = {}

        self._autodiscover_submodules()

    @classmethod
    def _get_sub_module_names(cls, ppath):
        sub_modules = []

        files = os.listdir(ppath)
        for f in files:
            if f.endswith('.py') and not f.startswith('__init__') and len(f) > 3:
                sub_modules.append(f[:-3])

        return sub_modules

    def _autodiscover_submodules(self):
        self._installed_dotted_path = list(chain(self._installed_dotted_path, self.func_parent_modules))

        for parent_module in self.func_parent_modules:
            parent = import_module(parent_module)
            sub_modules = map(lambda x: '%s.%s' % (parent_module, x), self._get_sub_module_names(parent.__path__[0]))
            sub_modules = map(import_module, sub_modules)
            self._installed_modules = list(chain(sub_modules, self._installed_modules))

    def install(self, modules):
        if not isinstance(modules, list):
            modules = [modules]

        app_modules = []
        for module in modules:
            if module not in self._installed_dotted_path:
                app_modules.append(import_module(module))

        self._installed_modules = list(chain(app_modules, self._installed_modules))

        return self._installed_modules

    def import_function(self, func_name):
        if func_name not in self._loaded_funcs:
            for installed in self._installed_modules:
                # TODO 可以根据startwith进行优化，而不用全部循环
                func = getattr(installed, func_name, None)

                if inspect.isfunction(func) and callable(func):
                    self._loaded_funcs[func_name] = func
                    break

        return self._loaded_funcs.get(func_name, None)


func_loading = LazyLoading()  # thread safe question ???
