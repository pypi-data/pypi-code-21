import inspect
from typing import Callable, Dict


def get_properties(obj: type, skip=list()) -> Dict[str, property]:
    return {
        name: member for name, member in inspect.getmembers(obj)
        if isinstance(member, property) and name not in skip
    }


def get_methods(obj: object, args_count=1, include_magic_functions: bool = False, skip=list()) -> Dict[str, Callable]:
    return {
        name: member for name, member in inspect.getmembers(obj)
        if inspect.isfunction(member) and name not in skip
        and len(inspect.getfullargspec(member).args) == args_count
        and (name.startswith('__') and name.endswith('__')) == include_magic_functions
    }
