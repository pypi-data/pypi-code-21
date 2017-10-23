import ConfigParser
import sys
import os


class ConfigObject(object):
    def __init__(self, _items):
        self._items = _items

    def __getattr__(self, k):
        if k == '_items':
            return self._items
        elif k in self._items:
            return self._items[k]
        else:
            raise AttributeError("Unable to find %s" % k)


class ConfigSectionsObject(object):
    def __init__(self, fpath):
        self._sections = {}
        if not os.path.exists(fpath):
            return

        c = ConfigParser.ConfigParser()
        c.read(fpath)
        for s in c.sections():
            opts = c.options(s)
            opt_items = {}
            for opt in opts:
                opt_items[opt] = c.get(s, opt)
            self._sections[s] = ConfigObject(opt_items)
        if c.defaults():
            self._sections['DEFAULT'] = c.defaults()

    def __getattr__(self, k):
        if k == "_sections":
            return self._sections

        if k in self._sections:
            return self._sections[k]

        else:
            if 'DEFAULT' in self._sections and k in self._sections['DEFAULT']:
                return self._sections['DEFAULT'][k]
            else:
                raise AttributeError("Unable to find %s" % k)


class Config(object):
    def __init__(self):
        try:
            index = sys.argv.index("--config-file")
            self.CONF = ConfigSectionsObject(sys.argv[index+1])
        except:
            self.CONF = ConfigSectionsObject("")

    def refresh(self, path):
        self.CONF = ConfigSectionsObject(path)
