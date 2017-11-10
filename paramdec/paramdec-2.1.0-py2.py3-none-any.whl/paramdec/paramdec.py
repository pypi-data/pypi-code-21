from functools import wraps


def paramdec(dec):
    """
    Create parametrized decorator.
    """
    @wraps(dec)
    def wrapper(func=None, **dec_kwargs):
        if callable(func) and not dec_kwargs:
            return dec(func)
        return lambda real_func: dec(real_func, **dec_kwargs)
    return wrapper


__all__ = ("paramdec",)
