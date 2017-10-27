import inspect
gparams = {}

def set_param(function):
    def wrapper(dict):
        global gparams
        gparams.update(dict)
        return function(dict)
    return wrapper


def get_param(function):
    def wrapper(*args, **kwds):
        signature = inspect.signature(function)
        params = {
                 k:gparams.get(k,None)
                 for k,v in signature.parameters.items()
                 if v.default is None
            }
        kwds.update(params)
        return function(*args, **kwds)
    return wrapper
