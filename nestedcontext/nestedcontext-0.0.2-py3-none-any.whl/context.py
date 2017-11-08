import collections
import typing


class ContextScope:
    def __init__(self, **kwargs):
        self.variables = kwargs  # type: typing.MutableMapping[str, typing.Any]

    def lookup(self, variablename: str) -> typing.Tuple[bool, typing.Any]:
        if variablename in self.variables:
            return True, self.variables[variablename]
        return False, None


class ContextStack:
    stacks = collections.defaultdict(
        lambda: ContextStack())  # type: typing.DefaultDict[typing.Optional[str], ContextStack]

    def __init__(self):
        self.stack = list()  # type: typing.MutableSequence[ContextScope]

    @staticmethod
    def get_contextstack(stackname: typing.Optional[str]) -> "ContextStack":
        return ContextStack.stacks[stackname]

    def enter(self, contextscope: ContextScope):
        self.stack.append(contextscope)

    def exit(self):
        self.stack.pop()

    def lookup(self, variablename: str) -> typing.Any:
        for contextscope in reversed(self.stack):
            hit, result = contextscope.lookup(variablename)
            if hit:
                return result
        raise KeyError(f"{variablename} not found")
