from .core import ActionFunction, ActionProxy
from contextlib import contextmanager


class ActionNotFoundError(Exception):
    pass


class ActionResolver(object):
    def __init__(self):
        self.stack = []

    def push(self, registry, bubbleup=True):
        self.stack.append((registry, bubbleup))

    def pop(self):
        self.stack.pop()

    def resolve(self, name):
        for registry, bubbleup in reversed(self.stack):
            try:
                return registry.resolve(name)
            except ActionNotFoundError:
                pass
            if not bubbleup:
                break
        raise ActionNotFoundError("Action '%s' does not exist" % name)

    def resolve_or_delayed(self, name, *args, **kwargs):
        try:
            action_class = self.resolve(name)
            return action_class(*args, **kwargs)
        except ActionNotFoundError:
            return DelayedInstanciationAction(name, *args, **kwargs)


action_resolver = ActionResolver()


def resolve_action(name):
    return action_resolver.resolve(name)


class ActionRegistry(object):
    """Register and access action classes. If a package name
    is specified when registering an action, the action will be
    available through its short name or through package_name.action_name
    """
    def __init__(self, actions=None, package=None):
        self.actions = {}
        self.aliases = {}
        if actions:
            self.register_many(actions, package)

    def register(self, action, package=None):
        if isinstance(action, ActionRegistry):
            return self.merge(action, package)
        if isinstance(action, ActionFunction):
            action = action.action
        fullname = action.name
        if package is not None:
            fullname = package + "." + fullname
        self.actions[fullname] = action
        self.aliases[action.name] = fullname

    def register_many(self, actions, package=None):
        if isinstance(actions, ActionRegistry):
            return self.merge(actions, package)
        for action in actions:
            self.register(action, package)

    def merge(self, registry, package=None):
        for action in registry:
            self.register(action, package)

    def action(self, *args, **kwargs):
        def decorator(f):
            af = ActionFunction(f, *args, **kwargs)
            self.register(af.action)
            return af
        return decorator

    def resolve(self, name):
        if name in self.aliases:
            return self.actions[self.aliases[name]]
        if name in self.actions:
            return self.actions[name]
        raise ActionNotFoundError("Action '%s' does not exist" % name)

    def as_only_resolver(self):
        action_resolver.push(self, False)
        try:
            yield self
        finally:
            action_resolver.pop()

    def __getitem__(self, name):
        return self.resolve(name)

    def __getattr__(self, name):
        return self.resolve(name)

    def __contains__(self, name):
        return name in self.aliases or name in self.actions

    def __iter__(self):
        return self.actions.itervalues()

    def __enter__(self):
        action_resolver.push(self)
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        action_resolver.pop()
        return False


class DelayedInstanciationAction(ActionProxy):
    """Wrap action constructor args for later initialization
    """
    def __init__(self, name, *ctorargs, **ctorkwargs):
        self._name = name
        self.ctorargs = ctorargs
        self.ctorkwargs = ctorkwargs
        self._action = None

    @property
    def name(self):
        return self._name
    
    @property
    def action(self):
        if not self._action:
            action_class = action_resolver.resolve(self.name)
            self._action = action_class(*self.ctorargs, **self.ctorkwargs)
        return self._action

    def __repr__(self):
        return '<%s(%s, %s, %s)>' % (self.__class__.__name__, self._name, self.ctorargs, self.ctorkwargs)