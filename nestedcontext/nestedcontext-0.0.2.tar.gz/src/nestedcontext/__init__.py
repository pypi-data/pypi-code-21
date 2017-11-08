import typing
from contextlib import contextmanager

from . import context


@contextmanager
def bind(stackname: typing.Optional[str]=None, conflicts_are_errors: bool=False, **kwargs):
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


def inject(variablename: str, stackname: typing.Optional[str]=None) -> typing.Any:
    stack = context.ContextStack.get_contextstack(stackname)
    return stack.lookup(variablename)
