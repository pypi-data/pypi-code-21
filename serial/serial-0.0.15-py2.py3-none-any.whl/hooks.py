from __future__ import nested_scopes, generators, division, absolute_import, with_statement, print_function,\
    unicode_literals

import collections

from copy import deepcopy
from future import standard_library

from serial import model

standard_library.install_aliases()

try:
    import typing
except ImportError as e:
    typing = None


class Hooks(object):

    def __init__(
        self,
        before_marshal=None,  # Optional[Callable]
        after_marshal=None,  # Optional[Callable]
        before_unmarshal=None,  # Optional[Callable]
        after_unmarshal=None,  # Optional[Callable]
        before_serialize=None,  # Optional[Callable]
        after_serialize=None,  # Optional[Callable]
        before_deserialize=None,  # Optional[Callable]
        after_deserialize=None,  # Optional[Callable]
        before_validate=None,  # Optional[Callable]
        after_validate=None,  # Optional[Callable]
    ):
        self.before_marshal = before_marshal
        self.after_marshal = after_marshal
        self.before_unmarshal = before_unmarshal
        self.after_unmarshal = after_unmarshal
        self.before_serialize = before_serialize
        self.after_serialize = after_serialize
        self.before_deserialize = before_deserialize
        self.after_deserialize = after_deserialize
        self.before_validate = before_validate
        self.after_validate = after_validate

    def __copy__(self):
        return self.__class__(**vars(self))

    def __deepcopy__(self, memo=None):
        # type: (dict) -> Memo
        return self.__class__(**{
            k: deepcopy(v, memo=memo)
            for k, v in vars(self).items()
        })

    def __bool__(self):
        return True


class Object(Hooks):

    pass


class Array(Hooks):

    pass


class Dictionary(Hooks):

    pass


def get(
    o  # type: Union[type, serial.model.Object]
):
    # type: (...) -> Union[Object, typing.Mapping, str]
    if isinstance(o, type):
        if o._hooks is None:
            o._hooks = (
                Object()
                if issubclass(o, model.Object) else
                Array()
                if issubclass(o, model.Array) else
                Dictionary()
                if issubclass(o, model.Dictionary)
                else None
            )
        else:
            for b in o.__bases__:
                if hasattr(b, '_hooks') and (o._hooks is b._hooks):
                    o._hooks = deepcopy(o._hooks)
                    break
        return o._hooks
    else:
        if o._hooks is None:
            o._hooks = deepcopy(get(type(o)))
    return o._hooks