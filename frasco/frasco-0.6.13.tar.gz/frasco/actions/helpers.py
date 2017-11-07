from .context import ContextExitException, TriggerActionGroupException, current_context, ensure_context
from .core import Action
from ..utils import logger


class ActionList(list):
    """A list of action. Makes it easy to filter
    """
    @property
    def groups(self):
        groups = set()
        for action in self:
            groups.add(action.group)
        return groups

    @property
    def methods(self):
        methods = set()
        for action in self:
            if not action.group and action.methods:
                methods.update(action.methods)
            elif action.group in ("get", "post", "put", "delete", "head", "options"):
                methods.add(action.group.upper())
        if not methods:
            methods.add("GET")
        return methods

    @property
    def requirements(self):
        reqs = set()
        for action in self:
            reqs.update(action.requires)
        return reqs

    def init_view(self, view):
        for action in self:
            action.init_view(view)

    def has_action(self, action_name):
        for action in self:
            if action.name == action_name:
                return True
        return False

    def filter_by_action(self, *action_names):
        for action in self:
            if action.name in action_names:
                yield action

    def filter_by_group(self, *groups):
        for action in self:
            if action.group in groups:
                yield action

    def execute(self, **kwargs):
        return execute_actions(self, **kwargs)

    def __call__(self, *args, **kwargs):
        return self.execute(*args, **kwargs)


class InvalidActionError(Exception):
    pass


def execute_action(action, catch_context_exit=True):
    with ensure_context():
        try:
            if not action.is_valid(current_context):
                logger.debug("Skipping invalid action %s" % action.name)
                raise InvalidActionError
            current_context.executed_actions.add(action.name)
            logger.debug("Executing action %s" % action.name)
            return action.execute()
        except ContextExitException as e:
            if not catch_context_exit:
                raise
            return e.result


def execute_actions(actions, limit_groups=None, catch_context_exit=True, trigger_error_group_on_exc=True):
    if limit_groups and not isinstance(limit_groups, (list, tuple)):
        limit_groups = [limit_groups]
    with ensure_context():
        try:
            if limit_groups and len(limit_groups) > 1:
                for group in limit_groups:
                    execute_actions(actions, (group,), False)
            else:
                for action in actions:
                    if limit_groups and action.group not in limit_groups:
                        continue
                    try:
                        execute_action(action, False)
                    except InvalidActionError:
                        continue
                    except TriggerActionGroupException as e:
                        logger.debug("Triggering action group %s" % e.group)
                        execute_actions(actions, (e.group,), False)
                    except Exception as e:
                        if trigger_error_group_on_exc:
                            execute_actions(actions, ("%s_error" % action.name,), False)
                        raise

        except ContextExitException as e:
            rv = e.result
            if e.trigger_action_group is not None:
                logger.debug("Triggering action group %s after context exit" % e.trigger_action_group)
                rv = execute_actions(actions, (e.trigger_action_group,)) or rv
            if not catch_context_exit:
                raise ContextExitException(rv)
            return rv


class ReturnValueException(Exception):
    def __init__(self, value):
        super(ReturnValueException, self).__init__()
        self.value = value


class ActionsAction(Action):
    """Represents an action that executes a list of actions when executed.
    Child actions can raise a ReturnValueException which will hold the return
    value of the action.
    """
    actions = None

    def __init__(self, *args, **kwargs):
        actions = kwargs.pop('actions', None)
        super(ActionsAction, self).__init__(*args, **kwargs)
        self.actions = ActionList(self.actions or [])
        if actions:
            self.actions.extend(actions)

    @property
    def methods(self):
        return self.actions.methods

    def init_view(self, view):
        for action in self.actions:
            action.init_view(view)

    def _execute(self, options):
        with current_context.clone(**options):
            try:
                execute_actions(self.actions, (None,), catch_context_exit=False)
            except ReturnValueException as e:
                return e.value

    def __call__(self, **kwargs):
        return self._execute(kwargs)