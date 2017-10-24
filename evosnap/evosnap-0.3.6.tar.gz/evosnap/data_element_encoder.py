import enum
import inspect
from collections import OrderedDict
from json import JSONEncoder

import sys

from evosnap import constants


class DataElementEncoder(JSONEncoder):

    @staticmethod
    def in_module(obj):
        module = __name__.split('.')[0]
        classes = [ x[1] for x in inspect.getmembers(
            sys.modules[module],
            lambda member: inspect.isclass(member) and module in member.__module__
        )]
        return any([isinstance(obj, c) for c in classes])

    def default(self, o):
        if self.in_module(o) and not isinstance(o, enum.Enum):
            __camelcase = '_'+o.__class__.__name__+'__camelcase'
            __lower_camelcase = '_'+o.__class__.__name__+'__lower_camelcase'
            __exclude = '_'+o.__class__.__name__+'__exclude'
            __order = '_'+o.__class__.__name__+'__order'
            res = dict(o.__dict__)
            if 'i_type' in res:
                res['$type'] = res.pop('i_type')
            if __exclude in res:
                items = res.pop(__exclude)
                for i in items:
                    res.pop(i)
            if __camelcase in res:
                items = res.pop(__camelcase)
                if items == constants.ALL_FIELDS:
                    items = list(res.keys())
                for i in items:
                    if i != '$type' and i != __order:
                        res[self.camel_case(i)] = res.pop(i)
            if __lower_camelcase in res:
                items = res.pop(__lower_camelcase)
                if items == constants.ALL_FIELDS:
                    items = list(res.keys())
                for i in items:
                    if i != '$type' and i != __order:
                        res[self.lower_camel_case(i)] = res.pop(i)
            if __order in res:
                res = self.order_dict(res, res.get(__order))
            return res
        if isinstance(o, enum.Enum):
            return o.value
        return super(DataElementEncoder, self).default(o)

    @staticmethod
    def camel_case(string):
        return string.replace('_', ' ').title().replace(' ','')

    @staticmethod
    def lower_camel_case(string):
        components = string.split('_')
        return components[0] + "".join(x.title() for x in components[1:])

    def order_dict(self, d, order):
        if order:
            return OrderedDict([(k, d.get(k)) for k in order])
        else:
            return OrderedDict(sorted(d, key=lambda t: t[0]))
