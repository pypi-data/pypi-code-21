import typing
from contextlib import contextmanager

from . import context


@contextmanager
def bind(stackname: typing.Optional[str]=None, conflicts_are_errors: bool=False, **kwargs):
    """
    Binds zero or more values to a nested context.  Once the context is exited, the binding is removed.

    If `stackname` is not provided, the value is bound to the default context.  If `stackname` is provided, the value is
    bound to that context.

    if `conflicts_are_errors` is True, then `ValueError` is raised if an existing binding to the same variable name
    already exists in the context.
    """
    stack = context.ContextStack.get_contextstack(stackname)
    if conflicts_are_errors:
        for varname in kwargs.keys():
            try:
                stack.lookup(varname)
                raise ValueError(f"{varname} is already bound.")
            except KeyError:
                pass
    contextscope = context.ContextScope(**kwargs)
    stack.enter(contextscope)
    yield
    stack.exit()


__sentinel = object()


def inject(variablename: str, stackname: typing.Optional[str]=None, default: typing.Any=__sentinel) -> typing.Any:
    """
    Return the variable bound to the name `variablename`, if it is found in any of the enclosing contexts.  If
    `stackname` is not provided, the search is limited to the default unnamed contexts.  If `stackname` is provided, the
    search is limited to the contexts with the given name.

    If a bound value is not found and `default` is not provided, `KeyError` will be raised.  If `default` is provided,
    that is returned instead.
    """
    global __sentinel
    stack = context.ContextStack.get_contextstack(stackname)
    try:
        return stack.lookup(variablename)
    except KeyError:
        if default is not __sentinel:
            return default
        raise
