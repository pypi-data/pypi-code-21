# -*- coding: utf-8 -*-


# noinspection PyPep8Naming
class pset(dict):
    """Property Set class.
       A property set is an object where values are attached to attributes,
       but can still be iterated over as key/value pairs.
       The order of assignment is maintained during iteration.
       Only one value allowed per key.

         >>> x = pset()
         >>> x.a = 42
         >>> x.b = 'foo'
         >>> x.a = 314
         >>> x
         pset(a=314, b='foo')

    """
    def __init__(self, items=(), **attrs):
        object.__setattr__(self, '_order', [])
        super(pset, self).__init__()
        if isinstance(items, dict):
            items = items.items()
        for k, v in items:
            self._add(k, v)
        for k, v in attrs.items():
            self._add(k, v)

    def __repr__(self):
        return '{%s}' % ', '.join(["%r: %r" % kv for kv in self])

    def _add(self, key, value):
        """Add key->value to client vars.
        """
        if key not in self._order:
            self._order.append(key)
        dict.__setitem__(self, key, value)

    def remove(self, key):
        """Remove key from client vars.
        """
        if key in self._order:
            self._order.remove(key)
        dict.__delitem__(self, key)

    def __eq__(self, other):
        """Equal iff they have the same set of keys, and the values for
           each key is equal. Key order is not considered for equality.
        """
        if other is None:
            return False
        if type(other) == dict:
            return dict.__eq__(self, other)
        # noinspection PyProtectedMember
        if set(self._order) == set(other._order):  # pylint: disable=W0212
            for key in self._order:
                if self[key] != other[key]:
                    return False
            return True
        return False

    def __ne__(self, other):
        return not (self == other)

    def __iadd__(self, other):
        for k, v in other:
            self._add(k, v)
        return self

    def __add__(self, other):
        """self + other
        """
        tmp = self.__class__()
        tmp += self
        tmp += other
        return tmp

    def __radd__(self, other):
        """other + self
        """
        tmp = self.__class__()
        for k, v in other.items():
            tmp[k] = v
        tmp += self
        return tmp

    def __getattr__(self, key):
        if not super(pset, self).__contains__(key):
            raise AttributeError(key)
        return dict.get(self, key)

    def __getitem__(self, key):
        return dict.get(self, key)

    def __delattr__(self, key):
        if key in self:
            self.remove(key)

    def __delitem__(self, key):
        if key in self:
            self.remove(key)

    def __iter__(self):
        return ((k, dict.get(self, k)) for k in self._order)

    def items(self):
        return iter(self)

    def values(self):
        # type: () -> list
        return [dict.get(self, k) for k in self._order]

    def keys(self):
        return self._order

    def __setattr__(self, key, val):
        # assert key not in self._reserved, key
        if key.startswith('_'):
            object.__setattr__(self, key, val)
        else:
            self._add(key, val)

    def __setitem__(self, key, val):
        self._add(key, val)
