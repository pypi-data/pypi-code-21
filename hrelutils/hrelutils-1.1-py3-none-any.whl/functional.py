def curry(func, *curry_args, **curry_kwargs):
    def curried(*args, **kwargs):
        return func(*curry_args, *args, **curry_kwargs, **kwargs)

    return curried


def identity(x):
    return x


def is_defined(x):
    return x is not None


def every(collection, check=identity):
    for thing in collection:
        if not check(thing):
            return False

    return True