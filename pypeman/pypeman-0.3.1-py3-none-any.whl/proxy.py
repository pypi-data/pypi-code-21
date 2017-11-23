import importlib
import traceback

proxies = []


# Lazy pour éviter d'importer des module non utilisé
# Optionnel si la dépendance n'est pas là
# À partir du module concerné (channels.HTTPChannel)


def load_class(module, sub, dep):
    try:
        mod = importlib.import_module(module)
        return getattr(mod, sub)
    except ImportError as exc:
        traceback.print_exc()
        msg = str(exc)
        if not dep in msg:
            print("IMPORT ERROR...")
            raise
        print("%s module not activated" % module)
        return None

def lazy_load(module, sub, dep=None):
    def init(*args, **kwargs):
        C = load_class(module, sub, dep)
        return C(*args, **kwargs)

    return init

#################
class Proxy():
    def __init__(self, module, sub):
        print('Proxy for %s %s' % (module, sub))
        self.module = module
        self._subject = None
        self.sub = sub
        proxies.append(self)

    def load_module(self):
        try:
            mod = importlib.import_module(self.module)
            self._subject = getattr(mod, self.sub)
        except ImportError as exc:
            traceback.print_exc()
            msg = str(exc)
            if not self.module in msg:
                print("IMPORT ERROR...")
                raise
            print("%s module not activated" % self.module)

    def __getattr__(self, name):
        if self._subject:
            return getattr(self._subject, name)
        else:
            raise Exception('Module %s not loaded' % self.sub)

    def __call__(self, *args, **kwargs):
        return self._subject(*args, **kwargs)

def load_modules():
    for p in proxies:
        p.load_module()