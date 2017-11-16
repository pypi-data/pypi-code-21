from builtins import super

import logging

from six import string_types
from ctypes import c_void_p, cast, pointer

from .tecutil_connector import _tecutil_connector, _tecutil
from .util import flatten_args
from .. import constant
from ..exception import TecplotTypeError


log = logging.getLogger(__name__)


class StringList(c_void_p):
    def __init__(self, *strings):
        super().__init__(_tecutil.StringListAlloc())
        self += flatten_args(*filter(lambda x: x, strings))

    @staticmethod
    def _bind_tecutil():
        try:
            _tecutil.handle.tecUtilArgListGetStringListByIndex.restype = StringList
        except AttributeError:
            pass

        if _tecutil_connector.client is not None:
            _ArgListGetStringListByIndex = _tecutil_connector.client.ArgListGetStringListByIndex
            def ArgListGetStringListByIndex(*a, **kw):
                return cast(_ArgListGetStringListByIndex(*a, **kw), StringList)
            _tecutil_connector.client.ArgListGetStringListByIndex = ArgListGetStringListByIndex

        _CustomLabelsGet = _tecutil.CustomLabelsGet
        def CustomLabelsGet(*a, **kw):
            success, ptr = _CustomLabelsGet(*a, **kw)
            if not success:
                raise TecplotSystemError()
            return cast(ptr, StringList)
        _tecutil.CustomLabelsGet = CustomLabelsGet

    # data access
    def __getitem__(self,i):
        return _tecutil.StringListGetRawStringPtr(self, i+1)

    def __len__(self):
        return _tecutil.StringListGetCount(self)

    def __eq__(self, other):
        if len(self) != len(other):
            return False
        for i in self:
            if i not in other:
                return False
        return True

    # string representations
    def __repr__(self):
        return 'StringList({args})'.format(args=', '.join("'{arg}'".format(arg=s) for s in self))

    def __str__(self):
        return str(list(self))

    # iterating
    def __iter__(self):
        self.current_index = -1
        self.max_index = len(self)
        return self

    def __next__(self):
        self.current_index += 1
        if self.current_index < self.max_index:
            return self.__getitem__(self.current_index)
        else:
            del self.current_index
            del self.max_index
            raise StopIteration()

    # context management
    def __enter__(self):
        return self

    def __exit__(self, *args):
        self.dealloc()

    # public methods
    def __iadd__(self, string_list):
        for s in string_list:
            self.append(s)
        return self

    def append(self,s):
        if not isinstance(s, string_types):
            raise TecplotTypeError('StringList can only hold strings')
        _tecutil.StringListAppendString(self, s)

    def clear(self):
        _tecutil.StringListClear(self)

    def dealloc(self):
        _tecutil.StringListDealloc(pointer(self))

    def next(self): # if sys.version_info < (3,)
        return self.__next__()

StringList._bind_tecutil()
