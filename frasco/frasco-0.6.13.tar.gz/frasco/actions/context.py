from ..utils import AttrDict, ContextStack as BaseContextStack
from flask import request, g, session
import datetime
from contextlib import contextmanager
import functools


class ContextStack(BaseContextStack):
    def pop(self):
        exported_vars = self.top.get_exported_vars()
        super(ContextStack, self).pop()
        if self.top:
            self.top.vars.update(exported_vars)


_context_stack = ContextStack()
current_context = _context_stack.make_proxy()


def has_action_context():
    return _context_stack.top is not None


@contextmanager
def ensure_context(**vars):
    """Ensures that a context is in the stack, creates one otherwise.
    """
    ctx = _context_stack.top
    stacked = False
    if not ctx:
        ctx = Context()
        stacked = True
        _context_stack.push(ctx)
    ctx.update(vars)
    try:
        yield ctx
    finally:
        if stacked:
            _context_stack.pop()


class ContextExitException(Exception):
    """Exception to stop the execution of an action and of the following ones
    """
    def __init__(self, result=None, trigger_action_group=None):
        super(ContextExitException, self).__init__()
        self.result = result
        self.trigger_action_group = trigger_action_group


class TriggerActionGroupException(Exception):
    """Exception to stop the execution of an action and trigger another action group
    Normal execution flow will resume after that.
    """
    def __init__(self, group):
        super(TriggerActionGroupException, self).__init__()
        self.group = group


class Context(object):
    """Holds the data for an execution context. The data attribute is used to
    hold data which actions want to pass to each others without exposing them
    in the view. The vars attribute holds data for the template.
    """
    def __init__(self, vars=None, data=None, **kwargs):
        self.vars = AttrDict(vars or {}, **kwargs)
        self.data = AttrDict(data or {})
        self.export_vars = []
        self.executed_actions = set()

    def __getitem__(self, name):
        return self.vars[name]

    def __setitem__(self, name, value):
        self.vars[name] = value

    def __contains__(self, name):
        return name in self.vars

    def update(self, vars):
        self.vars.update(vars)

    def get(self, name, default=None):
        return self.vars.get(name, default)

    def clone(self, **override_vars):
        """Creates a copy of this context"""
        c = Context(self.vars, self.data)
        c.executed_actions = set(self.executed_actions)
        c.vars.update(override_vars)
        return c

    def trigger_action_group(self, group):
        raise TriggerActionGroupException(group)

    def exit(self, result=None, trigger_action_group=None):
        raise ContextExitException(result, trigger_action_group)

    def get_exported_vars(self):
        return dict((k, self.vars[k]) for k in self.export_vars)

    def __enter__(self):
        _context_stack.push(self)
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        _context_stack.pop()
        return False


def request_context(app, request):
    """Creates a Context instance from the given request object
    """
    vars = {}
    if request.view_args is not None:
        vars.update(request.view_args)
    vars.update({
        "request": request,
        "GET": AttrDict(request.args.to_dict()),
        "POST" : AttrDict(request.form.to_dict()),
        "app": app,
        "config": app.config,
        "session": session,
        "g": g,
        "now": datetime.datetime.now,
        "utcnow": datetime.datetime.utcnow,
        "today": datetime.date.today})
    context = Context(vars)
    context.vars["current_context"] = context
    return context


def pass_context_var(*vars):
    def decorator(f):
        @functools.wraps(f)
        def wrap(*args, **kwargs):
            kwargs.update(dict((k, current_context[k]) for k in vars))
            return f(*args, **kwargs)
        return wrap
    return decorator