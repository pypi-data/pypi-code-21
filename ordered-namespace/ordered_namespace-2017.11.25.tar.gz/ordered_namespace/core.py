from collections import OrderedDict
import re


class Struct:
    """Ordered namespace class
    """

    # Regular expression pattern for valid Python attributes
    # https://docs.python.org/3/reference/lexical_analysis.html#identifiers
    # _valid_key_pattern = re.compile('[a-zA-Z_][a-zA-Z0-9_]*')
    _valid_key_pattern = re.compile('[a-zA-Z][a-zA-Z0-9_]*')
    _special_names = ['_odict']
    _repr_max_width = 13

    def __init__(self, *args, **kwargs):
        """Ordered namespace class
        """
        self.__dict__['_odict'] = OrderedDict()

        self.update(*args, **kwargs)

    def update(self, *args, **kwargs):
        d = {}
        d.update(*args, **kwargs)
        for key, value in d.items():
            self[key] = value

    def _valid_key(self, key):
        """Return True if supplied key string serves as a valid attribute name: alphanumeric strings
        beginning with a letter.  Leading underscore not allowed.  Also test for conflict with protected
        attribute names (e.g. dict class instance methods).
        """
        if not isinstance(key, str):
            return False
        elif hasattr({}, key):
            return False
        elif key in self._special_names:
            return True
        else:
            return self._valid_key_pattern.match(key)

    def asdict(self):
        """Return a recursive dict representation of self
        """
        d = dict(self._odict)

        for k,v in d.items():
            if isinstance(v, Struct):
                d[k] = v.asdict()

        return d

    #--------------------------------
    # Expose a few standard dict methods
    def items(self):
        return self._odict.items()

    def keys(self):
        return self._odict.keys()

    def values(self):
        return self._odict.values()

    def pop(self, key):
        return self._odict.pop(key)

    #--------------------------------
    # Expose essential dict internal methods
    def __setattr__(self, key, value):
        """Set an item with dot-style access while testing for invalid names
        """
        if not self._valid_key(key):
            raise AttributeError('Invalid attribute name: {}'.format(key))

        try:
            self[key] = value
        except KeyError as e:
            raise AttributeError(e)

    def __setitem__(self, key, value):
        if not self._valid_key(key):
            raise KeyError('Invalid attribute name: {}'.format(key))

        if isinstance(value, dict) and key not in self._special_names:
            value = Struct(value)

        self._odict[key] = value

    def __getattr__(self, key):
        return self._odict[key]

    def __getitem__(self, key):
        return self._odict[key]

    def __delitem__(self, key):
        del self._odict[key]

    def __delattr__(self, key):
        del self._odict[key]

    def __iter__(self):
        return self._odict.__iter__()

    def __len__(self):
        return self._odict.__len__()

    def __contains__(self, key):
        return self._odict.__contains__(key)

    def __dir__(self):
        """http://ipython.readthedocs.io/en/stable/config/integrating.html#tab-completion
        """
        return self._odict.keys()

    def __eq__(self, other):
        return self._odict.__eq__(other)

    def __ne__(self, other):
        return self._odict.__ne__(other)

    def __repr__(self):
        return self._odict.__repr__()

    # def _ipython_key_completions_(self):
    #     """http://ipython.readthedocs.io/en/stable/config/integrating.html#tab-completion
    #     """
    #     print('sdfdsfdf')
    #     return self.__dir__()

    def _repr_pretty_(self, p, cycle):
        """Derived from IPython's dict and sequence pretty printer functions,
        https://github.com/ipython/ipython/blob/master/IPython/lib/pretty.py
        """
        if cycle:
            p.text('{...}')
        else:
            keys = self.keys()

            if keys:
                delim_start = '[{'
                delim_end = '}]'

                wid_max_max = self._repr_max_width
                wid_max = max([len(k) for k in keys])
                wid_max = min([wid_max, wid_max_max])
                key_template = '{{:{:d}s}}: '.format(wid_max)

                with p.group(len(delim_start), delim_start, delim_end):
                    # Loop over item keys
                    for idx, key in p._enumerate(keys):
                        if idx:
                            p.text(',')
                            p.breakable()

                        p.text(key_template.format(key))
                        p.pretty(self[key])
            else:
                p.text('{}')

#------------------------------------------------

if __name__ == '__main__':
    pass
