import os
import configparser
import json
import xmltodict
import yaml


from .nested import KEY_ERR, NestedDict


class ConfigSource():
    def __init__(self, fname):
        self.fname = fname
        self.core_substs = None
        self.substs = {}
        self.dict = NestedDict()
        if self.fname:
            # %(here)s
            here = os.path.dirname(os.path.abspath(self.fname))
            self.substs["here"] = here


    def addConfig(self, core_substs):
        self.core_substs = core_substs


    def parse(self):
        raise Exception("Must implement parse()")


    def asDict(self):
        return self.dict


    def interoplate(self, key, val):
        if not isinstance(val, str):
            return val

        for skey, sval in self.substs.items():
            if skey in val:
                return val.replace("%(skey)s", sval)
        for skey, sval in self.core_substs.items():
            if skey in val:
                return val.replace("%(skey)s", sval)
        return val


class INISource(ConfigSource):
    def __init__(self, fname, cfgparser=None):
        super().__init__(fname)
        self.parser = cfgparser


    def parse(self):
        if self.parser:
            return
        self.parser = configparser.ConfigParser(
            interpolation=configparser.ExtendedInterpolation())
        self.parser.read(self.fname)


    def asDict(self):
        d = NestedDict()
        for section, values in self.parser.items():
            if section == "DEFAULT":
                continue
            s = d.dict(section)
            for key, val in values.items():
                s[key] = val
        return d


class XMLSource(ConfigSource):
    def __init__(self, fname, strip_outer=True):
        super().__init__(fname)
        self.strip_outer = strip_outer


    def parse(self):
        with open(self.fname) as fp:
            self.dict = xmltodict.parse(fp.read(), attr_prefix="")
            if self.strip_outer and len(self.dict.keys()) == 1:
                for key in self.dict.keys():
                    self.dict = self.dict[key]
                    break


class JSONSource(ConfigSource):
    def parse(self):
        with open(self.fname) as fp:
            self.dict = json.load(fp)


class YAMLSource(ConfigSource):
    def parse(self):
        with open(self.fname) as fp:
            self.dict = yaml.load(fp)


class DBSource(ConfigSource):
    def __init__(self, db_creds):
        super().__init__(None)
        self.db_creds = db_creds


##
# mappings:
#   None: All args added the config
#   {}: Empty dict prevents any from added
#   {"key": None}: Filters args by key, no mapping into the dict. added top
#   {"key": "some/path"}: Filters args by key, mapped into the dict by path
#
class ArgParserSource(ConfigSource):
    def __init__(self, args, mappings=None):
        super().__init__(None)
        self.args = args
        self.mappings = mappings


    def parse(self):
        for key, val in vars(self.args).items():
            if self.mappings is None:
                self.dict[key] = val
            else:
                if key in self.mappings:
                    path = self.mappings[key]
                    if not path:
                        path = key
                    self.dict[path] = val


class Config(NestedDict):
    def __init__(self, sources=[], defaults={},
                 notfound=KEY_ERR, path_delim="/"):
        super().__init__(notfound=notfound, path_delim=path_delim)
        self.substs = dict()
        if not isinstance(sources, list):
            self.sources = [sources]
        else:
            self.sources = sources
        self.defaults = defaults
        self._setupSubsts()


    def load(self):
        for src in self.sources:
            src.parse()
            self.merge(src.asDict())


    def addSubst(self, key, val):
        self.substs[key] = val


    def delSubst(self, key):
        del self.substs[key]


    def _setupSubsts(self):
        # %(install)s
        install = "/".join(os.path.dirname(__file__).split("/")[:-1])
        self.substs["install"] = install
