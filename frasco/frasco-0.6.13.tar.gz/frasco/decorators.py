from flask import current_app
from .actions import (Action, ActionFunction, ActionList, ensure_context,\
                     execute_actions, load_actions, current_context,\
                     ContextExitException, ReturnValueException)
from .utils import ClassBoundDecoratorMixin
from werkzeug.urls import url_join
import functools


def hook(name=None, *args, **kwargs):
    """Decorator to register the function as a hook
    """
    def decorator(f):
        if not hasattr(f, "hooks"):
            f.hooks = []
        f.hooks.append((name or f.__name__, args, kwargs))
        return f
    return decorator


def register_hooks(func, hooks, obj):
    """Register func on obj via hooks.
    Hooks should be a tuple of (name, args, kwargs) where
    name is a method name of obj. If args or kwargs are not empty,
    the method will be called first and expect a new function as return.
    """
    for name, args, kwargs in hooks:
        hook = getattr(obj, name)
        force_call = kwargs.pop("_force_call", False)
        if force_call or len(args) > 0 or len(kwargs) > 0:
            hook = hook(*args, **kwargs)
        hook(func)


def action(*args, **kwargs):
    """Transforms functions or class methods into actions.
    Optionnaly, you can define a function to be used as the view initializer:

        @action()
        def my_action():
            pass

        @my_action.init_view
        def my_action_init_view(view, options):
            pass
    """
    def decorator(f):
        return ActionFunction(f, *args, **kwargs)
    return decorator


class WithActionsDecorator(ClassBoundDecoratorMixin):
    """Decorator to execute actions before/after a function
    """
    def __init__(self, func, actions=None):
        self.unbound_func = func
        self.func = self._wrap_func(func)
        self.__name__ = func.__name__
        self.actions = ActionList(actions or [])

    def __call__(self, *args, **kwargs):
        rv = None
        with ensure_context(), current_context.clone(**kwargs):
            ctx_exit = None
            try:
                execute_actions(self.actions, ("before", None),
                    catch_context_exit=False)
                rv = self.func(*args, **kwargs)
            except ReturnValueException as e:
                rv = e.value
            except ContextExitException as e:
                ctx_exit = e
                current_context["response"] = e.result
            execute_actions(self.actions, ("after",),
                catch_context_exit=False)
            if ctx_exit:
                raise ctx_exit
        return rv


def with_actions(actions_or_group_name, actions=None):
    """Executes the list of actions before/after the function
    Actions should be a list where items are action names as
    strings or a dict. See frasco.actions.loaders.load_action().
    """
    group = None
    if isinstance(actions_or_group_name, str):
        group = actions_or_group_name
    else:
        actions = actions_or_group_name
    def decorator(f):
        if isinstance(f, WithActionsDecorator):
            dec = f
        else:
            dec = WithActionsDecorator(f)
        dec.actions.extend(load_actions(actions, group=group))
        return dec
    return decorator


def expose(rule, **options):
    """Decorator to add an url rule to a function
    """
    def decorator(f):
        if not hasattr(f, "urls"):
            f.urls = []
        if isinstance(rule, (list, tuple)):
            f.urls.extend(rule)
        else:
            f.urls.append((rule, options))
        return f
    return decorator

