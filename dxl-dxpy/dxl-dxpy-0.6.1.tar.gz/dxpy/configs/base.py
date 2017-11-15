import copy
from dxpy.collections.dicts import DXDict


class Configs(DXDict):
    """
    A configs object is a *imutable* dict like collection. elements of the collection can be one of the following:
    #. basic types (str, int, bool)
    #. list or dict of basic types
    #. Configs object
    #. list or dict of Configs
    """
    yaml_tag = '!configs'
    _names = tuple()
    _default_configs = {}

    def __init__(self, *args, default_dict=None, **kwargs):
        if default_dict is None:
            default_dict = DXDict(self._default_configs)
        else:
            default_dict = default_dict.apply_default(default_dict)
        super(__class__, self).__init__(
            *args, **kwargs, default_dict=default_dict)

    @classmethod
    def names(cls):
        """ All keys of a configs class.
        """
        return cls._names


from dxpy import serialization
serialization.register(Configs)


