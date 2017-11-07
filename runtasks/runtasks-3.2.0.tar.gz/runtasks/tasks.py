
import sys, inspect
from collections import defaultdict

_tasks = {}
# All defined tasks, mapping from function name to Task instance.


class Task:
    def __init__(self, func, flags=None, allow_positional=True):
        self.name = func.__name__
        self.func = func
        self.sig  = None
        # Function signature that needs to be retrieved differently based on python 2 and 3

        if hasattr(inspect, 'signature'):
            # If python 3 as indicated by the inspect.signature function
            self.sig = inspect.signature(func)
        else:
            # Else use the funcsigs package in python 2 to
            try:
                import funcsigs
                self.sig = funcsigs.signature(func)
            except ImportError:
                sys.exit('Task %s: python 2 requires the funcsigs package.' % self.name)

        self.flags = self._allocate_flags(flags)
        # Maps from shortflags to parameter names.

        self.allow_positional = allow_positional
        # If false, all parameters must be supplied by name (dashes or name=value).  This is
        # not documented and is only used when parsing the options for run itself.

    def _allocate_flags(self, flags):
        """
        Assign flags based on the first letter of each argument.

        flags
          An optional mapping provided by the user.
        """
        final = {}
        if flags:
            final.update(flags)

        reassigned = set(final.values())

        d = defaultdict(list)
        for name in self.sig.parameters:
            # If the parameter has been assigned a different flag, don't also assign it to its
            # first letter.  This also allows us to use the letter for another flag.
            if name not in reassigned and name[0] not in final:
                d[name[0]].append(name)

        for flag, names in d.items():
            if len(names) == 1:
                final[flag] = names[0]

        return final

    def call(self, boundargs):
        """
        Calls the task, passing the arguments returned from parse.
        """
        self.func(*boundargs.args, **boundargs.kwargs)

    def __repr__(self):
        return '<Task %s>' % (self.name)


def optional_args(fn):
    # Python's decorators act completely different when called with and without arguments.
    def wrapped_decorator(*args, **kwargs):
        if len(args) == 1 and callable(args[0]):
            return fn(args[0])
        else:
            def real_decorator(decoratee):
                return fn(decoratee, *args, **kwargs)
            return real_decorator
    return wrapped_decorator


@optional_args
def task(func, flags=None, register=True):
    """
    Registers a function as a task.

    flags
      An optional mapping of single-character flags to parameter names.

    register
      If True, the task will be registered in the global list of tasks so its name can be
      recognized during parsing.  This should only be set to false during testing of runtasks.
    """
    task = Task(func, flags=flags)

    if register:
        if task.name in _tasks:
            sys.exit('There is more than one task named {!r}'.format(task.name))
        _tasks[task.name] = task

    # Mark the function to make it easy.
    func._task = task

    return func


def get_task_names():
    """
    Returns a list of defined names.
    """
    return list(_tasks.keys())
