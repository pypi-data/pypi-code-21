from ..expression import Parser as ExpressionParser
from .helpers import ActionList, ActionsAction
from .core import Action, ActionFunction
from .decorators import action_decorators
from .registry import action_resolver


def load_actions(spec, group=None, expr_parser=None):
    """Each item can be an action name as a string or a dict. When using a dict,
    one key/item pair must be the action name and its options and the rest action
    decorator names and their options.
    Example:
        load_actions(["login_required", {"flash": {"message": "hello world", "label": "warning"}}])
    """
    if expr_parser is None:
        expr_parser = ExpressionParser()
    actions = ActionList()

    for name in spec:
        options = {}
        as_ = None
        decorators = []

        if isinstance(name, dict):
            actionspec = dict(name)
            as_ = actionspec.pop("as", None)
            for dec, dec_cls in action_decorators:
                if dec in actionspec:
                    decorators.append((dec_cls, expr_parser.compile(actionspec.pop(dec))))
            name, options = actionspec.popitem()
            if options:
                options = expr_parser.compile(options)

        if isinstance(name, Action):
            action = name
        elif isinstance(name, ActionFunction):
            action = name.action
        else:
            action = action_resolver.resolve_or_delayed(name, options, group, as_)

        for dec_cls, arg in decorators:
            action = dec_cls(action, arg)

        actions.append(action)

    return actions


def load_grouped_actions(spec, default_group=None, key_prefix="actions", pop_keys=False, expr_parser=None):
    """Instanciates actions from a dict. Will look for a key name key_prefix and
    for key starting with key_prefix followed by a dot and a group name. A group
    name can be any string and will can be used later to filter actions.
    Values associated to these keys should be lists that will be loaded using load_actions()
    """
    actions = ActionList()
    if expr_parser is None:
        expr_parser = ExpressionParser()
    for key in spec.keys():
        if key != key_prefix and not key.startswith(key_prefix + "."):
            continue
        group = default_group
        if "." in key:
            (_, group) = key.split(".")
        actions.extend(load_actions(spec[key], group, expr_parser))
        if pop_keys:
            spec.pop(key)
    return actions


def create_action_from_dict(name, spec, base_class=ActionsAction, metaclass=type, pop_keys=False):
    """Creates an action class based on a dict loaded using load_grouped_actions()
    """
    actions = load_grouped_actions(spec, pop_keys=pop_keys)
    attrs = {"actions": actions, "name": name}
    if "as" in spec:
        attrs["as_"] = spec["as"]
        if pop_keys:
            del spec["as"]
    for k in ("requires", "methods", "defaults", "default_option"):
        if k in spec:
            attrs[k] = spec[k]
            if pop_keys:
                del spec[k]
    return metaclass(name, (base_class,), attrs)