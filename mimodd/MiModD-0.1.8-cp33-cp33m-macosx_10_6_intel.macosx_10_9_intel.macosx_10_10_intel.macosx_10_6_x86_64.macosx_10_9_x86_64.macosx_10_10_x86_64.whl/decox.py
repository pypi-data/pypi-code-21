"""A stripped-down, MiModD-specific version of decox,
a larger module for decorator-related code."""

import inspect
from collections import namedtuple

FuncInfo = namedtuple('FuncInfo', ['func','innerscope'])

def parachute (f):
    """Parachute decorator.

Useful for wrapping parameter checking functions.
This is the Python <3.3 compatible version of parachute."""
    
    def wrappee(*args, **kwargs):
        """Tests validity of *args[1:], **kwargs for calling function func
specified by args[0].
Binds *args[1:], **kwargs to func's paramters and passes them as a
dictionary mapping to the wrapped function."""

        funcinfo, *args = args
        try:
            if not isinstance(funcinfo.innerscope, bool):
                raise TypeError ('Second element innerscope of funcinfo must be boolean')
        except AttributeError:
            raise TypeError ('Expected FuncInfo(namedtuple) instance as first argument')
        Sig = inspect.getfullargspec(funcinfo.func)
        params = (Sig.args or [])
        if Sig.varargs:
            params.append(Sig.varargs)
        if Sig.varkw:
            params.append(Sig.varkw)
        
        if funcinfo.innerscope:
            args = args[0]
            arg_dict = {k : v for (k,v) in args.items() if k in params}
        else:
            arg_dict = inspect.getcallargs(funcinfo.func, *args, **kwargs)
        arg_dict.update(arg_dict.pop(Sig.varkw, {}))
        ret = f(**arg_dict)
        return ret
    return wrappee
