from types import (CodeType,
                   FunctionType)

from hypothesis import strategies

from .utils import names


def empty_function():
    pass


def function(name: str,
             *,
             base: FunctionType = empty_function) -> FunctionType:
    code = CodeType(base.__code__.co_argcount,
                    base.__code__.co_kwonlyargcount,
                    base.__code__.co_nlocals,
                    base.__code__.co_stacksize,
                    base.__code__.co_flags,
                    base.__code__.co_code,
                    base.__code__.co_consts,
                    base.__code__.co_names,
                    base.__code__.co_varnames,
                    base.__code__.co_filename,
                    name,
                    base.__code__.co_firstlineno,
                    base.__code__.co_lnotab)

    return FunctionType(code, base.__globals__, name)


empty_functions = strategies.builds(function,
                                    name=names)
