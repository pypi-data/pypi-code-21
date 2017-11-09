"""Class & metaclass stuff"""


from functools import wraps
from collections import OrderedDict
from collections import defaultdict


__all__ = ["AttrsPart", "froze_it", "keydefaultdict"]



def froze_it(cls):
    """
    Decorator to prevent from creating attributes in the object ouside __init__().

    This decorator must be applied to the final class (doesn't work if a
    decorated class is inherited).

    Yoann's answer at http://stackoverflow.com/questions/3603502
    """
    cls._frozen = False

    def frozensetattr(self, key, value):
        if self._frozen and not hasattr(self, key):
            raise AttributeError("Attribute '{}' of class '{}' does not exist!"
                  .format(key, cls.__name__))
        else:
            object.__setattr__(self, key, value)

    def init_decorator(func):
        @wraps(func)
        def wrapper(self, *args, **kwargs):
            func(self, *args, **kwargs)
            self._frozen = True
        return wrapper

    cls.__setattr__ = frozensetattr
    cls.__init__ = init_decorator(cls.__init__)

    return cls


class _AAObject(object):
    """
    Implements "meta" property (used to store history, etc.)

    TODO making use of this 'meta' is for the future
    """

    @property
    def classname(self):
        return self.__class__.__name__

    def __init__(self):
        self.meta = {}


class AttrsPart(_AAObject):
    """
    Implements a new __str__() to print selected attributes.

    **Subclassing**:
      - set the `attrs` class variable
    """

    # for __str__()
    attrs = None
    # for __repr__()
    # Optional; if not set, will be overwritten with self.attrs at __init__()
    less_attrs = None

    def __init__(self):
        _AAObject.__init__(self)
        if self.less_attrs is None:
            self.less_attrs = self.attrs

    def __str__(self):
        if self.attrs is None or len(self.attrs) == 0:
            return _AAObject.__str__(self)

        maxlen = max([len(x) for x in self.attrs])
        s_format = "{{:>{0:d}}} = {{}}".format(maxlen)
        l = []
        for x in self.attrs:
            y = self.__getattribute__(x)
            if isinstance(y, list):
                # list gets special treatment
                v = "["+\
                     ",\n{0:{1}}".format("", maxlen+4).join([z.one_liner_str() if isinstance(z, AttrsPart)
                                                   else str(z) for z in y])+\
                     "\n{0:{1}}]".format("", maxlen+3)
            else:
                v = self.__getattribute__(x)

            l.append(s_format.format(x, v))

        s = "\n".join(l)
        return s

    def one_liner_str(self):
        """Returns string (supposed to be) shorter than str() and not contain newline"""
        assert self.less_attrs is not None, "Forgot to set attrs class variable"
        s_format = "{}={}"
        s = "; ".join([s_format.format(x, self.__getattribute__(x)) for x in self.less_attrs])
        return s

    def to_dict(self):
        """Returns OrderedDict whose keys are self.attrs"""
        ret = OrderedDict()
        for attrname in self.attrs:
            ret[attrname] = self.__getattribute__(attrname)
        return ret

    def to_list(self):
        """Returns list containing values of attributes listed in self.attrs"""

        ret = OrderedDict()
        for attrname in self.attrs:
            ret[attrname] = self.__getattribute__(attrname)
        return ret


class keydefaultdict(defaultdict):
    """
    Subclass of defaultdict to pass the missing key to the default factory

    Usage:

        d = keydefaultdict(C)
        d[x] # returns C(x)

    Source: solution by Rochen Ritzel at https://stackoverflow.com/questions/2912231/is-there-a-clever-way-to-pass-the-key-to-defaultdicts-default-factory
    """

    def __missing__(self, key):
        if self.default_factory is None:
            raise KeyError( key )
        else:
            ret = self[key] = self.default_factory(key)
            return ret

