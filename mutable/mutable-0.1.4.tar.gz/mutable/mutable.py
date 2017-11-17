import argparse
import inspect
import json
import os

# Mutable base class
class Mutable(object):

    # Initialization
    def __init__(self, value=None, root=True, name=None,
        args=False, auto=False, *vargs, **kwargs):

        # Convert all props to Mutable props
        self.__set__(self.__dict__)

        # Collect internal props
        self.__dot__ = chr(46)
        self.__type__ = type(value)
        self.__root__ = root

        # Set value
        self.__set__(self.load(value, auto))

        # Check for argument help in base class
        if hasattr(self.__class__, "help"):
            self.__help__ = self.__class__.help

        # Parse args and name
        if args: self.args()
        if name: self.__class__.__name__ = name

    # Custom get
    def __get__(self, inst=None, owner=None):

        # Return value
        if hasattr(self, "__value__"):
            return self.__value__

        # Return list
        if self.__type__ == list:
            return [self.__getattribute__(x) for x in self.fields()]

        return self

    # Custom getattribute
    def __getattribute__(self, key):
        v = object.__getattribute__(self, key)
        if hasattr(v, "__value__"):
            v = object.__getattribute__(v, "__value__")
        return v

    # Custom getitem
    def __getitem__(self, key):
        k = str(key).split(self.__dot__)

        # Handle lists
        if self.__type__ == list:
            try: v = self.__get__()[key]
            except: v = self.__get__()[int(k[0])]
            
        # Handle dicts
        elif hasattr(self, k[0]):
            v = getattr(self, k[0])

        # Others
        else:
            return None

        # Recurse key from mutable value or return
        if isinstance(v, Mutable):
            if len(k) > 1:
                return v[self.__dot__.join(k[1:])]
            else:
                return v.__get__()
        return v

    # Custom set
    def __set__(self, value):
        if hasattr(self, "__value__"):
            del self.__value__
        if isinstance(value, dict):
            for k, v in value.items():
                self.__dict__[str(k)] = Mutable(v, root=False)
        elif isinstance(value, list):
            for i in range(len(value)):
                self.__dict__[str(i)] = Mutable(value[i], root=False)
        else:
            self.__value__ = value

    # Custom setattr
    def __setattr__(self, key, value):
        if "__" in key:
            self.__dict__[key] = value
        else:
            self[key] = value

    # Custom setitem
    def __setitem__(self, key, value):

        # Not initialized
        if not hasattr(self, "__dot__"):
            self.__dict__[key] = value
            return value

        k = str(key).split(self.__dot__)
        if hasattr(self, k[0]):
            v = object.__getattribute__(self, k[0])
            if isinstance(v, Mutable):
                if len(k) > 1:
                    v[self.__dot__.join(k[1:])] = value
                else:
                    v.__set__(value)
            else:
                self.__set__(value)
        else:
            self.__set__(value)

    # Returns iterable from self
    def __iter__(self):
        for k in self.fields():

            # Yield values for list
            if self.__type__ == list:
                yield self[k]

            # Otherwise yield keys and values
            else:
                yield k, self[k]

    # Base descriptor
    def __int__(self):
        return int(self.__get__())

    # Base descriptor
    def __float__(self):
        return float(self.__get__())

    # Base descriptor
    def __str__(self):
        if hasattr(self, "__value__"):
            return str(self.__value__)
        try: value = dict(self)
        except: value = self.__get__()
        return json.dumps(value, default=lambda x: dict(x))

    # Base descriptor
    def __repr__(self):
        if hasattr(self, "__value__"):
            return repr(self.__value__)
        try: value = dict(self)
        except: value = self.__get__()
        return json.dumps(value, default=lambda x: dict(x), indent=2, sort_keys=True)

    # Base descriptor
    def __add__(self, value):
        if hasattr(self, "__value__"):
            return self.__value__ + value
        raise TypeError("Unsupported operand type(s) for +: '{0}' and '{1}'".format("Mutable", type(value)))

    # Base descriptor
    def __sub__(self, value):
        if hasattr(self, "__value__"):
            return self.__value__ - value
        raise TypeError("Unsupported operand type(s) for -: '{0}' and '{1}'".format("Mutable", type(value)))

    # Base descriptor
    def __mul__(self, value):
        if hasattr(self, "__value__"):
            return self.__value__ * value
        raise TypeError("Unsupported operand type(s) for *: '{0}' and '{1}'".format("Mutable", type(value)))

    # Base descriptor
    def __mul__(self, value):
        if hasattr(self, "__value__"):
            return self.__value__ / value
        raise TypeError("Unsupported operand type(s) for /: '{0}' and '{1}'".format("Mutable", type(value)))

    # Base descriptor
    def __contains__(self, key):
        return hasattr(self, key)

    # Base descriptor
    def __len__(self):
        return len(self.fields())

    # Parses command line arguments
    def args(self):
        parser = argparse.ArgumentParser(description=self.__class__.__name__)
        if __name__ != '__main__':
            parser.usage = argparse.SUPPRESS
        for p in self.props():
            v = self[p]
            desc = ''
            if hasattr(self, "__help__") and p in self.__help__.keys():
                desc = self.__help__[p]
            parser.add_argument('--{0}'.format(p),
                type=type(v),
                default=v,
                help=desc,
                metavar=''
            )
        args = parser.parse_args()
        for k, v in args.__dict__.items():
            self[k] = v

    # Loads base value
    def load(self, value, auto=False):
        if auto:
            value = self.__class__.__name__ + ".json"
        if self.__root__ and self.__type__ == str:
            if value.endswith('.json'):
                if os.path.exists(value):
                    with open(value, 'r') as jsonfile:
                        value = jsonfile.read()
                else:
                    raise ValueError("could not locate json file '{0}'".format(value))
            try:
                value = json.loads(value)
            except:
                pass
        return value

    # Saves self as json file
    def save(self, path=".", pretty=True):
        if path == ".":
            path = self.__class__.__name__
        with open(path, 'w') as jsonfile:
            jsonfile.write(repr(self) if pretty else str(self))

    # Returns sorted fields
    def fields(self):
        return sorted(filter(lambda x: "__" not in x, [x for x, y in self.__dict__.items()]))

    # Returns props generator
    def props(self, prev=None):
        for k, v in self.__dict__.items():
            if "__" not in k:
                if isinstance(v, Mutable):
                    if hasattr(v, "__value__"):
                        yield k if prev == None else prev + self.__dot__ + k
                    else:
                        for p in v.props(prev=k):
                            yield p if prev == None else prev + self.__dot__ + p

# Class decorator
def mutable(cls):
    class ClassWrapper(Mutable, cls):
        def __init__(self, *args, **kwargs):
            # Check class __init__ method to find what arguments are accepted
            vargs, kwvars, var, defaults = inspect.getargspec(cls.__init__.__func__)

            # Only pass known kwargs to base class
            _kwargs = {}
            for k, v in kwargs.items():
                if k in vargs:
                    _kwargs[k] = v

            # If positional arguments are accepted ['self', '...'] then pass args
            if len(vargs) > 1:
                if len(args) > 1:
                    # First argument is always mutable value
                    cls.__init__(self, *(args[1:]), **_kwargs)
                else:
                    # Only pass keyword arguments
                    cls.__init__(self, **_kwargs)
            # Otherwise don't pass args
            else:
                cls.__init__(self)

            # Check if name should be overridden
            if 'name' not in kwargs.keys():
                name = str(cls)
                if "__main__." in name:
                    name = ".".join(name.split(".")[1:])
                self.__class__.__name__ = name

            # Check if class has help legend
            try:
                self.__help__ = cls.help
            except:
                pass

            # Since mutable accepts *args, **kwargs we can safely pass all kwargs.
            # and we only pass args that were not consumed by base class
            Mutable.__init__(self, *((args[0],) + args[len(vargs):]) , **kwargs)
    return ClassWrapper

if __name__ == '__main__':
    print Mutable()
