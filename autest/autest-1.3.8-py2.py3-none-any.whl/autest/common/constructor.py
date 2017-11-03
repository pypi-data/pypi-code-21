from __future__ import absolute_import, division, print_function
from functools import *
import inspect

from . import is_a


def map_kw(cls, func_info, args, kw):
    # type (func_info : any, args:tuple, kw:dict) -> dict
    '''
    map all argument value to kw
    '''

    total_passed = len(args)
    total_args = len(func_info.args)  # get total defined args
    total_default = 0 if func_info.defaults is None else len(
        func_info.defaults)
    arg_diff = total_args - total_default
    # map each argument in the signature of the function
    for cnt, a in enumerate(func_info.args):
        if cnt < total_passed:
            kw[a] = args[cnt]
        # map default value if and only if we don't have a value for it in kw
        elif cnt >= arg_diff and a not in kw:
            kw[a] = func_info.defaults[cnt - arg_diff]
    return kw


def user_map(func_info, argmap, kw):
    '''
    based on function info map the arguments needed
    to call the function based on what we have in KW
    '''
    ret = {}
    if func_info.keywords:
        # we have a kw to pass
        for k, v in kw.items():
            if k != "__arg_map__" and k != "self":
                ret[k] = v

    for cnt, a in enumerate(argmap):
        if cnt + 2 > len(func_info.args):
            raise RuntimeError(
                "Invalid mapping of arguments, function takes {0} arguments got {1}".
                format(len(func_info.args), cnt + 2))
        if not inspect.isfunction(a):
            ret[func_info.args[cnt + 1]] = kw[a] if a in kw else a
        else:  # assume it is a function
            ret[func_info.args[cnt + 1]] = a(kw)
    return ret


def map_kw_init(clsname, func_info, kw):
    '''
    based on function info map the arguments needed
    to call the function based on what we have in KW
    '''
    rkw = {}
    arg_map = kw.get("__arg_map__", {}).get(clsname)
    # user mapping
    if arg_map:
        return user_map(func_info, arg_map, kw)

    if func_info.keywords:
        # we have a kw to pass
        for k, v in kw.items():
            if k != arg_map:
                rkw[k] = v
    else:
        # normal mapping
        default_indx = 0
        total_args = len(func_info.args)  # get total defined args
        total_default = 0 if func_info.defaults is None else len(
            func_info.defaults)
        # map each argument in the signature of the function
        for cnt, a in enumerate(func_info.args):
            if a != 'self':
                try:
                    rkw[a] = kw[a]
                    if cnt >= total_args - total_default:
                        default_indx += 1
                except KeyError:
                    # try defaults.. else error out
                    if func_info.defaults is not None:
                        rkw[a] = func_info.defaults[default_indx]
                        default_indx += 1
                    else:
                        print(
                            "argument mapping error for class {0}:\n Trying to map arguments {1}\n Has arguments {2}".
                            format(clsname, func_info.args, kw.keys()))
                        raise
    return rkw


def _next_class(pcls, cur_cls):
    '''
    get next class to be called in MRO init call order
    '''
    mro = inspect.getmro(pcls)
    idx = mro.index(cur_cls) + 1
    return mro[idx]


def call_base(**kw):
    # test to see if we should call super
    # this allows for a way to bind with existing code
    # and not break the inheritance __init__ logic
    call_super = kw.get("super", True)
    try:
        del kw["super"]
    except KeyError:
        pass
    arg_map = kw
    # validate we input types
    for c, args in arg_map.items():
        if not is_a.OrderedSequence(args):
            raise TypeError(
                "Argument mapping needs to be a list of tuple type")

    def constructor_mapper(func):
        @wraps(func)
        def init_wrapper(*lst, **kw):
            # get class of function we are calling
            cls = init_wrapper.__cls__

            # map all argument to kw for easy passing
            kw = map_kw(cls, inspect.getargspec(func), lst, kw)
            try:
                # map in the __init__ argments we want to pass based on class
                # type
                for k, v in arg_map.items():
                    if k in kw["__arg_map__"]:
                        raise RuntimeError(
                            "class {0} is already been defined for mapping, in valid class mapping".
                            format(k))
                    kw["__arg_map__"][k] = v
            except KeyError:
                # we have not set it yet
                kw["__arg_map__"] = arg_map.copy()
            # get the arguments we need to get for the current class __init__
            # call
            init_kw = map_kw_init(cls.__name__, inspect.getargspec(func), kw)
            # get next init function to make sure we can pass **kw to it
            # the python object does not allow for this
            tmp = _next_class(type(lst[0]), cls)
            if call_super and (inspect.isfunction(tmp.__init__) or
                               inspect.ismethod(tmp.__init__)):
                super(cls, lst[0]).__init__(**kw)
            func(lst[0], **init_kw)

        return init_wrapper

    return constructor_mapper


def smart_init(cls):
    # python 2
    try:
        setattr(cls.__init__.im_func, "__cls__", cls)
    except:
        # python 3
        setattr(cls.__init__, "__cls__", cls)
    return cls
