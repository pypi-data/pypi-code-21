import os
import yaml
from .err import handle_error, log_error

SCRIPT_DIRPATH = os.path.dirname(os.path.realpath(__file__))
KCK_SOURCES_DIRPATH = os.path.join(SCRIPT_DIRPATH, "..")

class NotEnoughParameters(Exception):
    pass

class FrameworkActor(object):

    keysep = "/"
    parameters = []
    cache_obj = None
    data_obj = None
    hooks = None
    name = None

    @staticmethod
    def make_relpath_absolute(dirpath):
        """given any dirpath, relative or absolute, return an absolute dirpath"""
        if dirpath[0] == '/':
            return dirpath
        return os.path.abspath(os.path.join(KCK_SOURCES_DIRPATH, dirpath))

    @staticmethod
    def proc_files_in_dirpath(dirpath, filter_func, callback_func):
        """walk all files in dirpath, recursing into subdirs, and, if filter_func
           returns True for a given filepath, call callback_func with the filepath
           as a parameter"""
        for subdir, dirs, files in os.walk(dirpath):
            for file in files:
                fp = os.path.join(subdir, file)
                if filter_func(fp):
                    callback_func(os.path.join(subdir, file))

    @staticmethod
    def read_yaml(filepath, on_error=None):
        """read/parse a yaml file, return resulting object"""
        with open(filepath, 'r') as stream:
            try:
                return yaml.load(stream)
            except yaml.YAMLError as exc:
                handle_error(exc, "unable to init config object", on_error)

    def set_name(self, name_str):
        self.name = name_str

    def get_name(self):
        return self.name

    def set_cache(self, cache_obj):
        self.cache_obj = cache_obj

    def get_cache(self):
        return self.cache_obj

    def set_data(self, data_obj):
        self.data_obj = data_obj

    def get_data(self):
        return self.data_obj

    def primary_key_parameter_name(self):
        for p in self.parameters:
            if "primary_key" in p and bool(p["primary_key"]):
                return p["name"]
        return None

    def dependency_key(self):
        ret = self.name
        for p in self.parameters:
            ret += self.keysep + ":{}".format(p["name"])
        return ret

    def dependency_key_to_param_dict(self, key_tmpl, key):
        print("dependency_key_to_param_dict entered")
        key_tmpl_names_with_colons = \
            key_tmpl.split(self.keysep) if self.keysep in key_tmpl else [key_tmpl]
        print("key_tmpl_names_with_colons: {}".format(key_tmpl_names_with_colons))
        key_tmpl_names = \
            [ x.split(':')[1] if ':' in x else x for x in key_tmpl_names_with_colons][1:]
        print("key_tmpl_names: {}".format(key_tmpl_names))
        key_values = key.split(self.keysep)[1:] if self.keysep in key else [key]
        print("key_values: {}".format(key_values))

        ret = {}
        for ndx, name in enumerate(key_tmpl_names):
            ret[name] = key_values[ndx]

        return ret

    def key_to_param_dict(self, key_str):

        transform = dict(
            string=lambda x: str(x),
            float=lambda x: float(x),
            int=lambda x: int(x)
        )

        if key_str is None or key_str == "":
            return {}

        param_list = key_str.split(self.keysep)[1:] if self.keysep in key_str else []
        # print("key_str: {}, param_list: {}".format(key_str, param_list))
        try:
            if len(param_list) < len(self.parameters):
                raise NotEnoughParameters
            ret = {}
            for ndx, param_dict in enumerate(self.parameters):
                ret[param_dict["name"]] = param_list[ndx]
                if "type" in param_dict:

                    try:
                        ret[param_dict["name"]] = transform[param_dict["type"]](ret[param_dict["name"]])
                    except ValueError:
                        ret[param_dict["name"]] = None

            return ret
        except (IndexError, NotEnoughParameters):

            # this builds the dict when there's no primary key (as when records
            #  are being created)

            if len(param_list) == 0:
                return {}

            # if there's just one arg, it's the primary key and we're updating
            if len(param_list) == 1:
                primary_key_name = None
                for ndx, param_dict in enumerate(self.parameters):
                    if "primary_key" in param_dict and bool(param_dict["primary_key"]):
                        primary_key_name = param_dict["name"]
                        return { primary_key_name: param_list[0] }

            ret = {}
            offset = 0
            for ndx, param_dict in enumerate(self.parameters):
                if "primary_key" in param_dict and bool(param_dict["primary_key"]):
                    offset = -1
                    continue
                print("ndx: {}".format(ndx))
                ret[param_dict["name"]] = param_list[ndx+offset]
                if "type" in param_dict:
                    try:
                        ret[param_dict["name"]] = transform[param_dict["type"]](ret[param_dict["name"]])
                    except ValueError:
                        ret[param_dict["name"]] = None
            return ret

    def param_dict_to_key(self, param_dict):
        key_components = []
        for p in self.parameters:
            try:
                key_components.append(str(param_dict[p["name"]]))
            except KeyError:
                raise NotEnoughParameters
        return self.keysep.join(key_components)

    def register_hooks(self):
        if self.hooks is None:
            self.hooks = {}

    def add_hook(self, event, keystr, func):
        if self.hooks is None:
            self.hooks = {}
        if event not in self.hooks:
            self.hooks[event] = []
        self.hooks[event].append((keystr, func))

    def do_hooks(self, event, *args, **kwargs):

        if self.hooks is None:
            self.hooks = {}

        print("do_hooks({}) for {}".format(event, self.name))
        try:
            for hook_tuple in self.hooks[event]:
                keystr, hfunc = hook_tuple
                print("  found {} hook named {} with key: {}...".format(event, hfunc.__name__, keystr))
                kwargs["param_key"] = keystr
                try:
                    hfunc(*args, **kwargs)
                except Exception as e:
                    print("  err: {}".format(e))
                    log_error(e)
        except KeyError:
            pass
