from builtins import int, super

import itertools as it

from collections import namedtuple
from contextlib import contextmanager
from ctypes import c_char_p, c_void_p, cast
from enum import Enum
from six import string_types

from ..tecutil import _tecutil
from ..constant import *
from ..exception import *
from ..tecutil import lock, lock_attributes


@lock_attributes
class AuxData(c_void_p):
    """Auxiliary data.

    The |Tecplot Engine| can hold auxiliary data attached to one of the
    following objects:

        - `Layout <layout.aux_data>`
        - `Page <Page.aux_data>`
        - `Frame <Frame.aux_data>`
        - `Dataset <Dataset.aux_data>`
        - `Variable <Variable.aux_data>`
        - `Zone <OrderedZone.aux_data>`
        - `Linemap <XYLinemap.aux_data>`

    Auxiliary data is an ordered key-value pair that behaves like an ordered
    dictionary, or `OrderedDict <collections.OrderedDict>`. Keys are strings
    which are ordered alphabetically and values can additionally be access by
    index. The keys must be alphanumeric (special characters "." and "_" are
    allowed), must not contain spaces, and must begin with a non-numeric
    character or underscore. Values, on the other hand, are arbitrary strings
    and can contain anything except the null character. In this example, we
    query the auxiliary data attached to the dataset and add some information
    to it. Notice that the stored order is alphabetical::

        >>> import tecplot as tp
        >>> aux = tp.active_frame().aux_data
        >>> aux['info'] = 'Here is some information.'
        >>> aux['Xavg'] = 3.14159
        >>> aux['note'] = 'Aux data values are always converted to strings.'
        >>> for k, v in aux.items():
        ...     print('{}: {}'.format(k,v))
        info: Here is some information.
        note: Aux data values are always converted to strings.
        Xavg: 3.14159
    """
    def __init__(self, parent, object_type, object_index=None):
        self.parent = parent
        self.object_type = object_type
        self.getref_args = [] if object_index is None else [object_index + 1]
        super().__init__(self._native_reference)

    @property
    def _native_reference(self):
        _dispatch = {
            AuxDataObjectType.Dataset: _tecutil.AuxDataDataSetGetRef,
            AuxDataObjectType.Frame: _tecutil.AuxDataFrameGetRef,
            AuxDataObjectType.Layout: _tecutil.AuxDataLayoutGetRef,
            AuxDataObjectType.Linemap: _tecutil.AuxDataLineMapGetRef,
            AuxDataObjectType.Page: _tecutil.AuxDataPageGetRef,
            AuxDataObjectType.Variable: _tecutil.AuxDataVarGetRef,
            AuxDataObjectType.Zone: _tecutil.AuxDataZoneGetRef}
        with self._activated_parent():
            return _dispatch[self.object_type](*self.getref_args)

    @contextmanager
    def _activated_parent(self):
        if self.parent:
            with self.parent.activated():
                yield
        else:
            yield

    @contextmanager
    def assignment(self):
        _tecutil.AuxDataBeginAssign()
        try:
            yield
        finally:
            _tecutil.AuxDataEndAssign()

    def index(self, key):
        """Returns the zero-based index of the element based on key.

        Example usage::

            >>> frame = tp.active_frame()
            >>> frame.aux_data['result'] = '3.1415'
            >>> frame.aux_data['other_info'] = '128'
            >>> print(frame.aux_data.index('other_info'))
            0
            >>> print(frame.aux_data.index('result'))
            1
        """
        try:
            success, index = _tecutil.AuxDataGetItemIndex(self, key)
            index -= 1
            if not success:
                raise TecplotKeyError
        except TecplotSystemError:
            raise TecplotKeyError
        return index

    _Item = namedtuple('Item', ['key', 'value', 'dtype', 'retain'])

    def _item(self, index):
        res =_tecutil.AuxDataGetItemByIndex(self, index + 1)
        key, value, dtype, retain = res
        if dtype is AuxDataType.String:
            value = cast(value, c_char_p).value.decode('utf-8')
        else:
            # if we ever add another type to AuxDataType, this would
            # need to be expanded as well as setitem which currently
            # just converts every input to a string.
            raise TecplotNotImplementedError
        return AuxData._Item(key, value, dtype, retain)

    def key(self, index):
        """Returns the key at a specific zero-based index.

        Example usage::

            >>> frame = tp.active_frame()
            >>> frame.aux_data['result'] = '3.1415'
            >>> frame.aux_data['other_info'] = '128'
            >>> print(frame.aux_data.key(0))
            other_info
            >>> print(frame.aux_data.key(1))
            result
        """
        return self._item(index).key

    def __getitem__(self, key):
        if isinstance(key, string_types):
            key = self.index(key)
        return self._item(key).value

    @lock()
    def __setitem__(self, key, value):
        if isinstance(key, int):
            try:
                key = self.key(key)
            except:
                raise TecplotIndexError
        if not _tecutil.AuxDataSetItem(self, key, str(value),
                                       AuxDataType.String.value, True):
            raise TecplotSystemError()

    @lock()
    def __delitem__(self, key):
        if isinstance(key, string_types):
            key = self.index(key)
        _tecutil.AuxDataDeleteItemByIndex(self, key + 1)

    def __len__(self):
        return _tecutil.AuxDataGetNumItems(self)

    def __iter__(self):
        self._current_index = -1
        self._current_length = len(self)
        return self

    def __next__(self):
        self._current_index += 1
        if self._current_index < self._current_length:
            return self.key(self._current_index)
        else:
            raise StopIteration

    def next(self):
        return self.__next__()

    def items(self):
        """Yields all key/value pairs of the Aux Data attached to the parent.

        Elements are always ordered alphabetically by the keys. Example usage::

            >>> frame = tp.active_frame()
            >>> frame.aux_data['result'] = '3.1415'
            >>> frame.aux_data['other_info'] = '128'
            >>> for key, value in frame.aux_data.items():
            ...     print(key, value)
            other_info 128
            result 3.1415
        """
        for i in range(len(self)):
            item = self._item(i)
            yield item.key, item.value

    def keys(self):
        """Yields all keys of the Aux Data attached to the parent.

        Elements are always ordered alphabetically by the keys. Example usage::

            >>> frame = tp.active_frame()
            >>> frame.aux_data['result'] = '3.1415'
            >>> frame.aux_data['other_info'] = '128'
            >>> for value in frame.aux_data.keys():
            ...     print(value)
            other_info
            result
        """
        for key in self:
            yield key

    def values(self):
        """Yields all values of the Aux Data attached to the parent.

        Elements are always ordered alphabetically by the keys. Example usage::

            >>> frame = tp.active_frame()
            >>> frame.aux_data['result'] = '3.1415'
            >>> frame.aux_data['other_info'] = '128'
            >>> for value in frame.aux_data.values():
            ...     print(value)
            128
            3.1415
        """
        for _, value in self.items():
            yield value

    def as_dict(self):
        """Returns a Python dict of the Aux Data attached to the parent.

        Note that this will remove the alphabetical ordering guarantee that Aux
        Data has since Python dict objects are unordered. Example usage::

            >>> frame = tp.active_frame()
            >>> frame.aux_data['result'] = '3.1415'
            >>> frame.aux_data['other_info'] = '128'
            >>> aux = frame.aux_data.as_dict()
            >>> print(aux)
            {'result': '3.1415', 'other_info': '128'}
        """
        return {k: v for k, v in self.items()}

    def __str__(self):
        return str(self.as_dict())

    def update(self, *other, **kwargs):
        """Update Aux Data with key/value pairs from another Aux Data or dict.

        Example usage::

            >>> frame = tp.active_frame()
            >>> frame.aux_data.update({'result': '3.1415', 'other_info': '128'})
            >>> print(frame.aux_data)
            {'result': '3.1415', 'other_info': '128'}
        """
        with self.assignment():
            for d in it.chain(other, [kwargs]):
                for k, v in d.items():
                    self[k] = v

    def clear(self):
        """Deletes all Aux Data from the associated object.

        Example usage::

            >>> print(frame.aux_data)
            {'bb': 'test bb', 'cc': 'test cc', 'aa': 'test aa'}
            >>> frame.aux_data.clear()
            >>> print(frame.aux_data)
            {}
        """
        for key in list(self.keys()):
            del self[key]
