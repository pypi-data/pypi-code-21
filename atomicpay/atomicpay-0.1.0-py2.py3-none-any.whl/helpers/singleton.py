"""
A non-thread safe function used to create singleton

The function is defined and implemented in PEP 318
    PEP 318 -- Decorators for Functions and Methods

@Link https://www.python.org/dev/peps/pep-0318/#examples

Singleton decorator defined

Example:

    @singleton
    class Foo:
        def __init__(self, bar):
            self._bar = bar
        @property
        def bar(self):
            return self._bar

    print(type(Foo("baz")))
"""


def singleton(cls):
    instances = {}

    def getinstance(*args, **kwargs):
        if cls not in instances:
            instances[cls] = cls(args, kwargs)
        return instances[cls]
    return getinstance
