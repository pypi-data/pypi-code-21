from .core import ActionProxy
from .context import current_context
from ..expression import eval_expr
import inspect


action_decorators = []


def action_decorator(name):
    """Decorator to register an action decorator
    """
    def decorator(cls):
        action_decorators.append((name, cls))
        return cls
    return decorator


@action_decorator("with_items")
class WithItemsDecorator(ActionProxy):
    """Executes the proxyied action in a loop
    """
    def __init__(self, action, items):
        self.action = action
        self.items = items

    def execute(self):
        """Executes the action using a context where vars will be the kwargs
        """
        items = eval_expr(self.items, current_context.vars)
        if not items:
            return []
        for item in items:
            opts = eval_expr(self.action.options, dict(current_context.vars, item=item))
            rv = self.action._execute(opts)
            if inspect.isgenerator(rv):
                # see Action class for why this can be a generator
                try:
                    rv.next() # actual return value of the function, ignored
                    rv.next() # end function execution
                except StopIteration:
                    pass


@action_decorator("when")
class WhenDecorator(ActionProxy):
    """Executes the proxyies action only if an expression evals to True
    """
    def __init__(self, action, test):
        self.action = action
        self.test = test

    def is_valid(self, context):
        if self.test is None:
            valid = True
        else:
            valid = eval_expr(self.test, context.vars)
        if valid:
            return self.action.is_valid(context)
        return False


@action_decorator("ignore_errors")
class IgnoreErrorDecorator(ActionProxy):
    """Catches all errors raised by the action and ignores them
    """
    def __init__(self, action, enabled=True):
        self.action = action
        self.enabled = enabled

    def execute(self, *args, **kwargs):
        try:
            return self.action.execute(*args, **kwargs)
        except:
            if not self.enabled:
                raise


@action_decorator("only_once")
class OnlyOnceDecorator(ActionProxy):
    """Only executes the proxyied action if it was not already executed
    in the current context
    """
    def __init__(self, action, enabled=True):
        self.action = action
        self.enabled = enabled

    def is_valid(self, context):
        return not self.enabled or self.action.name not in current_context.executed_actions


with_items = WithItemsDecorator
when = WhenDecorator
ignore_errors = IgnoreErrorDecorator
only_once = OnlyOnceDecorator