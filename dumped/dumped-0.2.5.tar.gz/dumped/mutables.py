'''Dumped.mutables — patch for Dumped, which makes you able to use dicts and lists in Dumped objects.'''
import functools


class TrackedList(list):
    def __init__(self, *args, _dumped_parent, **kwargs):
        self._dumped_parent = _dumped_parent
        list.__init__(self, *args, **kwargs)

    @functools.wraps(list.append)
    def append(self, obj):
        list.append(self, patch(obj, self._dumped_parent))
        self._dumped_parent._dump()

    @functools.wraps(list.clear)
    def clear(self):
        list.clear(self)
        self._dumped_parent._dump()

    @functools.wraps(list.extend)
    def extend(self, iterable):
        for item in iterable:
            self.append(item)
        self._dumped_parent._dump()

    @functools.wraps(list.insert)
    def insert(self, index, obj):
        list.insert(self, index, patch(obj, self._dumped_parent))
        self._dumped_parent._dump()

    @functools.wraps(list.pop)
    def pop(self, index=-1):
        result = list.pop(self, index)
        self._dumped_parent._dump()
        return result

    @functools.wraps(list.remove)
    def remove(self, value):
        list.remove(self, value)
        self._dumped_parent._dump()

    @functools.wraps(list.reverse)
    def reverse(self):
        list.reverse(self)
        self._dumped_parent._dump()

    @functools.wraps(list.sort)
    def sort(self):
        list.sort(self)
        self._dumped_parent._dump()

    @functools.wraps(list.__setitem__)
    def __setitem__(self, key, value):
        list.__setitem__(self, key, patch(value, self._dumped_parent))
        self._dumped_parent._dump()

    @functools.wraps(list.__delitem__)
    def __delitem__(self, key):
        list.__delitem__(self, key)
        self._dumped_parent._dump()


class TrackedDict(dict):
    class SPECIAL_DEFAULT:
        pass

    def __init__(self, *args, _dumped_parent, **kwargs):
        self._dumped_parent = _dumped_parent
        dict.__init__(self, *args, **kwargs)

    @functools.wraps(dict.clear)
    def clear(self):
        dict.clear(self)
        self._dumped_parent._dump()

    @functools.wraps(dict.pop)
    def pop(self, key, default=SPECIAL_DEFAULT):
        if default == SPECIAL_DEFAULT:
            result = dict.pop(self, key)
        else:
            result = dict.pop(self, key, default)
        self._dumped_parent._dump()
        return result

    @functools.wraps(dict.popitem)
    def popitem(self):
        result = dict.popitem(self)
        self._dumped_parent.dump()
        return result

    @functools.wraps(dict.setdefault)
    def setdefault(key, default=None):
        result = dict.setdefault(self, key, patch(default, self._dumped_parent))
        self._dumped_parent.dump()
        return result

    @functools.wraps(dict.update)
    def update(self, other, **kwargs):
        dict.update(self, other, **kwargs)
        for k in self:
            self[k] = patch(self[k], self._dumped_parent)
        self._dumped_parent.dump()

    @functools.wraps(dict.__setitem__)
    def __setitem__(self, key, value):
        dict.__setitem__(self, key, patch(value, self._dumped_parent))
        self._dumped_parent._dump()

    @functools.wraps(dict.__delitem__)
    def __delitem__(self, key):
        dict.__delitem__(self, key)
        self._dumped_parent._dump()


def patch(obj, parent):
    def patch_list(obj):
        result = TrackedList(obj, _dumped_parent=parent)
        for i, x in enumerate(result):
            result[i] = patch(x, parent)
        return result

    def patch_dict(obj):
        result = TrackedDict(obj, _dumped_parent=parent)
        for k in result:
            result[k] = patch(result[k], parent)
        return result

    if isinstance(obj, list):
        return patch_list(obj)

    if isinstance(obj, dict):
        return patch_dict(obj)

    return obj
