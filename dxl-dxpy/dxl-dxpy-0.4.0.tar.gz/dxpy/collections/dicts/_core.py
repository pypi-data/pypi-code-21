from collections import UserDict
from dxpy import serialization
from dxpy.filesystem import Path
from ._exceptions import NotDictError


class DXDict(UserDict):
    yaml_tag = '!dxdict'

    def __init__(self, *args, default_dict=None, **kwargs):
        super(__class__, self).__init__(*args, **kwargs)
        if default_dict is not None:
            self.default_dict = DXDict(default_dict)
        else:
            self.default_dict = None

    def __getitem__(self, key):
        if key in self.data:
            return self.data[key]
        elif self.default_dict is not None:
            return self.default_dict[key]
        return None

    def keys(self):
        from itertools import chain
        if self.default_dict is not None:
            return chain(self.data.keys(), self.default_dict.keys())
        else:
            return self.data.keys()

    def apply_default(self, default_dict):
        if self.default_dict is None:
            return DXDict(self.data, default_dict=default_dict)
        else:
            return DXDict(self.data, default_dict=self.default_dict.apply_default(default_dict))


serialization.register(DXDict)

# from .trees import PathTree


# class TreeDict(PathTree):
#     yaml_tag = '!treedict'

#     def __init__(self, *args, **kwargs):
#         super(__class__, self).__init__()

#     def compile(self):
#         self._push_dict()

#     def _push_dict(self, path=None, dct=None):
#         if dct is None:
#             dct = DXDict()
#         if path is None:
#             path = '/'
#         if self.get_data(path) is None:
#             self.get_node(path).data = DXDict(dct)
#             new_dict = self.get_node(path).data
#         else:
#             new_dict = self.get_data(path).apply_default(dct)
#         self.get_node(path).data = new_dict
#         nodes = self.tree.children(path)
#         for n in nodes:
#             self._push_dict(n.indentifier, self.get_node(path).data)

#     def __getitem__(self, path):
#         return self.get_data(path)

#     def add_dict(self, name, parent, dct):
#         self.create_node(name, parent, data=DXDict(dct))

class TreeDict(UserDict):
    """
    A dict with tree struct:
        1. Hierarchy access
            Support a['name1']['name2'] style access;
        2. Autogenerate for missing layers
            If there is no a['name1'] dict while setting a['name1']['name2'],
            an empty TreeDict will be created on a['name1']
        3. Inherence values
            If we are accessing a['name1']['name2'], but there is not 'name2' key in a['name1'],
            the dict will try to find if there is 'name2' in a (root).
        4. KeyError only happens when need a dict but got a object which is not dict,
           For those keys are not defined in the TreeDict, return a empty TreeDict object.
    """
    yaml_tag = '!dxdict'

    def __init__(self, dct=None, fa=None):
        if not isinstance(dct, (dict, UserDict)):
            raise NotDictError(type(dct))
        super(__class__, self).__init__(dct)
        self.fa = fa
        for k in self.data:
            if isinstance(self.data[k], (dict, UserDict)):
                self.data[k] = TreeDict(self.data, fa=self)

    @classmethod
    def _parse_path(cls, name):
        if '/' in name:
            names = Path(name).parts
            if len(names) > 1:
                return names[0], '/'.join(names[1:])
            elif len(names) == 1:
                return names[0], None
            elif len(names) == 0:
                return None, None
        else:
            return name, None

    def _ensure_mid_layers(self, name, names):
        if names is not None:
            if not name in self.data:
                self.data[name] = TreeDict(fa=self)
            elif not isinstance(self.)

    def _get_value_on_leaf(self, name):
        if name is self.data:
            return self.data[name]
        value_inherent = self._get_value_by_inherence(name)
        if value_inherent is None:
            self.data[name] = TreeDict()
        else:
            self.data[name] = value_inherent
        return self.data[name]

    def _get_value(name, names):
        if names is None:
            return self._get_value_on_leaf(name)
        else:
            if not isinstance(self.data[name], (TreeDict, dict, UserDict)):
                raise _exceptions.KeyNotDictError(name)
            if name in self.data:
                return self.data[name]
            else:
                return default

    def __getitem__(self, name):
        if name is None:
            return self
        name, names = self._parse_path(name)
        self._auto_create_mid_layers(name, names)
        return self._get_value(name, names)
