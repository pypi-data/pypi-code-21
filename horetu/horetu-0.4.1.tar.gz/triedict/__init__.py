__all__ = ['triedict']
from collections import MutableMapping, OrderedDict
from collections import defaultdict

class AmbiguousKey(KeyError):
    pass

class KeyNotFound(KeyError):
    pass

class DefaultOrderedDict(OrderedDict):
    def __init__(self, default_factory):
        self._f = default_factory
        super(DefaultOrderedDict, self).__init__()
    def __getitem__(self, key):
        try:
            return super(DefaultOrderedDict, self).__getitem__(key)
        except KeyError:
            self[key] = self._f()
            return self[key]

def _dictdefaultdict():
    return DefaultOrderedDict(_dictdefaultdict)

def _chars(key):
    for i in range(len(key)):
        yield key[i:i+1]

def _iter_trie_dict(prefix, d):
    for k, v in d.items():
        if k == None:
            yield prefix
        else:
            yield from _iter_trie_dict(prefix + k, v)

class triedict(MutableMapping):
    def __init__(self, *args, **kwargs):
        self._type = None
        self._trie = _dictdefaultdict()
        self.update(OrderedDict(*args, **kwargs))

    def _check_type(self, key):
        if self._type:
            if isinstance(key, self._type):
                pass # good
            else:
                raise TypeError('Key must be of %s type.' % self._type)
        else:
            if hasattr(key, '__iter__'):
                self._type = type(key)
            else:
                raise TypeError('Key must be iterable.')
    def _join(self, key):
        if issubclass(self._type, str):
            return self._type(''.join(key))
        else:
            return self._type(key)

    def __repr__(self):
        return 'triedict(%s)' % repr(list(self.items()))

    def key(self, key):
        return self._item(key)['key']
    def __getitem__(self, key):
        return self._item(key)['value']
    def _item(self, key):
        self._check_type(key)
        d = self._trie
        subkey = [None] + list(key)
        for char in _chars(key):
            if char in d:
                d = d[char]
                subkey = subkey[1:]
            else:
                break
        if d == self._trie and len(key) > 0:
            raise KeyNotFound('Not found: ' + str(key))

        if None in d:
            if len(subkey) == 1:
                return {'key': key, 'value': d[None]}
            else:
                raise KeyNotFound('Not found: ' + str(key))
        else:
            fullkey = key
            while None not in d and len(d) == 1:
                nextchar = next(iter(d))
                fullkey = fullkey + nextchar
                d = d[nextchar]
                subkey = subkey[1:]

            if len(d) > 1:
                if (not subkey) or (subkey[0] in d):
                    raise AmbiguousKey('Ambiguous: ' + str(key))
                else:
                    raise KeyNotFound('Not found: ' + str(key))
            elif len(d) == 0 or None not in d:
                raise KeyNotFound('Not found: ' + str(key))
            else:
                return {'key': self._join(fullkey), 'value': d[None]}

    def __setitem__(self, key, value):
        self._check_type(key)
        d = self._trie
        for char in _chars(key):
            d = d[char]
        d[None] = value

    def __delitem__(self, key):
        self._check_type(key)
        raise NotImplementedError

    def __iter__(self):
        d = self._trie
        if d:
            return _iter_trie_dict(self._type(), d)
        else:
            return iter([])

    def __len__(self):
        n = 0
        for _ in self:
            n += 1
        return n
