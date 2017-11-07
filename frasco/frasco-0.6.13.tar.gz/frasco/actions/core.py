from ..utils import RequirementMissingError, ClassBoundDecoratorMixin
from ..expression import eval_expr
from .context import ensure_context, current_context
import inspect


class OptionMissingError(Exception):
    pass


class InvalidOptionError(Exception):
    pass


class Action(object):
    """Override this class to create a custom action
    """
    # Name of your action (it is mandatory to override it)
    name = None
    # Default group
    group = None
    # Allowed http methods for this action
    methods = None
    # When the function returns something, what should be the variable name
    as_ = None
    # A list of action names required for this action
    requires = []
    # Default options
    defaults = {}
    # If option is a string, it will be transformed to a dict using
    # default_option as the key
    default_option = "default"

    def __init__(self, options=None, group=None, as_=None, **kwargs):
        self.options = dict(self.defaults)
        if options:
            if not isinstance(options, dict):
                options = dict([(self.default_option, options)])
            self.options.update(options)
        self.options.update(kwargs)
        if group:
            self.group = group
        if as_:
            self.as_ = as_

    def init_view(self, view):
        """Called when an action is added to a view
        """

    def is_valid(self, context):
        """Checks through the previous_actions iterable if required actions have
        been executed
        """
        if self.requires:
            for r in self.requires:
                if not r in context.executed_actions:
                    raise RequirementMissingError("Action '%s' requires '%s'" % (self.name, r))
        return True

    def execute(self):
        with ensure_context():
            rv = self._execute(eval_expr(self.options, current_context.vars))
            g = None
            if inspect.isgenerator(rv):
                g = rv
                rv = g.next()
            if self.as_:
                current_context.vars[self.as_] = rv
            if g:
                try:
                    g.next()
                except StopIteration:
                    pass
        return rv

    def _execute(self, options):
        """Unless you want to override the evaluation of options, you should
        override this method to define the logic of your action
        """
        raise NotImplementedError

    def __repr__(self):
        return "<Action %s%s>" % (self.name, " in %s" % self.group if self.group else "")


class ActionFunction(ClassBoundDecoratorMixin):
    """A decorator to create action classes from functions or class methods.
    """
    # kwargs will be used as attributes of the action class
    def __init__(self, func, name=None, init_view_func=None, **kwargs):
        self.__name__ = self.name = name or func.__name__
        self.unbound_func = func
        self.func = self._wrap_func(func)
        self.init_view_func = None
        if init_view_func:
            self.init_view(init_view_func)

        def execute(s):
            self.as_ = s.as_
            rv = Action.execute(s)
            del self.as_
            return rv

        def _execute(s, options):
            self.as_ = s.as_
            rv = self.func(**options)
            s.as_ = self.as_
            return rv

        def init_view(s, view):
            if self.init_view_func is None:
                return
            self.as_ = s.as_
            rv = self.init_view_func(view, s.options)
            del self.as_
            return rv

        attrs = dict(kwargs, name=self.name, execute=execute,
            _execute=_execute, init_view=init_view)

        if hasattr(func, "actions"):
            # Override the methods property of the ActionFunction action
            # to return properties needed by the WithActionsDecorator actions.
            def methods(s):
                return func.actions.methods
            attrs.update(methods=property(methods))

        self.action = type(self.name, (Action,), attrs)

    def __call__(self, *args, **kwargs):
        with ensure_context():
            self.as_ = None
            rv = self.func(*args, **kwargs)
        return rv

    def init_view(self, f):
        self.unbound_init_view_func = f
        self.init_view_func = self._wrap_func(f)
        return f


class ActionProxy(Action):
    def __init__(self, action):
        self.action = action

    @property
    def name(self):
        return self.action.name

    @property
    def group(self):
        return self.action.group

    @property
    def methods(self):
        return self.action.methods

    @property
    def as_(self):
        return self.action.as_

    @property
    def requires(self):
        return self.action.requires

    @property
    def defaults(self):
        return self.action.defaults

    @property
    def default_option(self):
        return self.action.default_option

    @property
    def options(self):
        return self.action.options

    def init_view(self, *args, **kwargs):
        return self.action.init_view(*args, **kwargs)

    def is_valid(self, *args, **kwargs):
        return self.action.is_valid(*args, **kwargs)

    def execute(self, *args, **kwargs):
        return self.action.execute(*args, **kwargs)

    def _execute(self, *args, **kwargs):
        return self.action._execute(*args, **kwargs)

    def __call__(self, *args, **kwargs):
        return self.action(*args, **kwargs)

    def __repr__(self):
        return '<%s(%s)>' % (self.__class__.__name__, repr(self.action))