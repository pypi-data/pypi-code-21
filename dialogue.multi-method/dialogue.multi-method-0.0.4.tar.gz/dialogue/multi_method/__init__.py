# Multi-dispatch functions for python
# Taken from https://gist.github.com/adambard/6bf15282874ca89404f7


def multi(dispatch_fn, default=None):
    """A decorator for a function to dispatch on.

    The value returned by the dispatch function is used to look up the
    implementation function based on its dispatch key.

    The dispatch function is available using the `dispatch_fn` function.
    """
    def _inner(*args, **kwargs):
        dispatch_value = dispatch_fn(*args, **kwargs)
        f = _inner.__multi__.get(dispatch_value, _inner.__multi_default__)
        if f is None:
            raise Exception("No implementation of %s for dispatch value %s",
                            dispatch_fn.__name__, dispatch_value)
        return f(*args, **kwargs)

    _inner.__multi__ = {}
    _inner.__multi_default__ = default
    _inner.__dispatch_fn__ = dispatch_fn
    return _inner


def method(dispatch_fn, dispatch_key=None):
    """A decorator for a function implementing dispatch_fn for dispatch_key.

    If no dispatch_key is specified, the function is used as the
    default dispacth function.
    """
    def apply_decorator(fn):
        if dispatch_key is None:
            # Default case
            dispatch_fn.__multi_default__ = fn
        else:
            dispatch_fn.__multi__[dispatch_key] = fn
        return fn
    return apply_decorator


def dispatch_fn(multi_fn):
    """Return the dispatch function for a multi-method."""
    return multi_fn.__dispatch_fn__
