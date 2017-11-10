from functools import wraps
from paramdec import paramdec


@paramdec
def accepts(func, types=()):
    @wraps(func)
    def wrapper(*args, **real_kwargs):
        if all(isinstance(a, t) for a, t in zip(args, types)):
            return func(*args, **real_kwargs)
        else:
            raise TypeError("%s only accepts %s, but was given %s" % (func, types, args))
    return wrapper


@paramdec
def returns(func, type_=None):
    @wraps(func)
    def wrapper(*args, **kwargs):
        result = func(*args, **kwargs)
        if isinstance(result, type_):
            return result
        else:
            raise TypeError("%s must return %s, but returned %s" % (func, type_, result))
    return wrapper
