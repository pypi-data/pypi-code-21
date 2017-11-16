from builtins import super, int

import ctypes

from ctypes import c_size_t, c_void_p, POINTER, cast, pointer
from six import string_types
from textwrap import dedent

from .tecutil_connector import _tecutil_connector, _tecutil
from .. import constant
from ..exception import TecplotTypeError
from .util import flatten_args, Index

class IndexSet(c_void_p):
    def __init__(self, *numbers):
        # numbers may be an iterable or a single value
        super().__init__(_tecutil.SetAlloc(False))
        self.__iadd__(flatten_args(*numbers))

    @staticmethod
    def _bind_tecutil():
        try:
            _tecutil.handle.tecUtilArgListGetSetByIndex.restype = IndexSet
        except AttributeError:
            pass
        try:
            _tecutil.handle.tecUtilDataValueGetShareZoneSet.restype = IndexSet
        except AttributeError:
            pass
        try:
            _tecutil.handle.tecUtilConnectGetShareZoneSet.restype = IndexSet
        except AttributeError:
            pass

        if _tecutil_connector.client is not None:
            _ArgListGetSetByIndex = _tecutil_connector.client.ArgListGetSetByIndex
            _tecutil_connector.client.ArgListGetSetByIndex = lambda *a, **kw: cast(_ArgListGetSetByIndex(*a, **kw), IndexSet)

            _DataValueGetShareZoneSet = _tecutil_connector.client.DataValueGetShareZoneSet
            _tecutil_connector.client.DataValueGetShareZoneSet = lambda *a, **kw: cast(_DataValueGetShareZoneSet(*a, **kw), IndexSet)

            _ConnectGetShareZoneSet = _tecutil_connector.client.ConnectGetShareZoneSet
            _tecutil_connector.client.ConnectGetShareZoneSet = lambda *a, **kw: cast(_ConnectGetShareZoneSet(*a, **kw), IndexSet)

        # tecutil function with output IndexSet pointer argument
        _ZoneGetActiveForFrame = _tecutil.ZoneGetActiveForFrame
        def ZoneGetActiveForFrame(*a, **kw):
            success, ptr = _ZoneGetActiveForFrame(*a, **kw)
            if not success:
                raise TecplotSystemError()
            return cast(ptr, IndexSet)
        _tecutil.ZoneGetActiveForFrame = ZoneGetActiveForFrame

    def __eq__(self, other):
        if len(self) != len(other):
            return False
        for i in self:
            if i not in other:
                return False
        return True

    # data access
    def __getitem__(self,i):
        return Index(_tecutil.SetGetMember(self, i + 1) - 1)

    def __len__(self):
        return _tecutil.SetGetMemberCount(self)

    # string representations
    def __repr__(self):
        return 'IndexSet({args})'.format(args=', '.join([str(s) for s in self]))

    def __str__(self):
        return str(set(self))

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
    def __iadd__(self, numbers):
        for i in numbers:
            self.append(i)
        return self

    def append(self, i):
        if isinstance(i, int):
            _tecutil.SetAddMember(self, i+1, False)
        elif hasattr(i, 'index') and isinstance(i.index, int):
            _tecutil.SetAddMember(self, i.index+1, False)
        else:
            msg = dedent('''\
                Set can only hold integers or objects
                with an integer attribute named index.
                failed on input: {} {}''')
            raise TecplotTypeError(msg.format(type(i),i))

    def clear(self):
        _tecutil.SetClear(self)

    def dealloc(self):
        _tecutil.SetDealloc(pointer(self))

    def next(self): # if sys.version_info < (3,)
        return self.__next__()

IndexSet._bind_tecutil()
