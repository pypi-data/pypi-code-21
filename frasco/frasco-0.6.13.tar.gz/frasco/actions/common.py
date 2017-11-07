from .helpers import ReturnValueException
from .context import current_context
from .registry import ActionRegistry
from ..utils import populate_obj, slugify
from ..signals import signal
import flask


common_actions = ActionRegistry()



@common_actions.action()
def exit_context(trigger_action_group=None):
    """Triggers a ContextExitException
    """
    current_context.exit(trigger_action_group=trigger_action_group)


@common_actions.action(default_option="group")
def trigger_group(group):
    """Triggers a TriggerActionGroupException
    """
    current_context.trigger_action_group(group)


@common_actions.action("return", default_option="value")
def return_value(value=None):
    raise ReturnValueException(value)


@common_actions.action(default_option="vars")
def export_var(vars):
    if not isinstance(vars, list):
        vars = [vars]
    current_context.export_vars.extend(vars)


@common_actions.action('set')
def set_var(**vars):
    """Sets context variables using the key/value provided in the options
    """
    current_context.vars.update(**vars)


@common_actions.action()
def incr(**vars):
    """Increments context variables
    """
    for k, v in vars:
        current_context.vars.setdefault(k, 0)
        current_context[k] += v


@common_actions.action('set_default')
def set_default_var(**vars):
    """Sets context variables using the key/value provided in the options
    """
    for k, v in vars.iteritems():
        current_context.vars.setdefault(k, v)


@common_actions.action()
def append_to(obj, items=None):
    obj.extend(items)


@common_actions.action()
def remove_from(obj, items=None):
    for i in items:
        obj.remove(i)


@common_actions.action()
def update_dict(obj, **items):
    obj.update(items)


@common_actions.action()
def pop_dict(obj, keys):
    for key in keys:
        obj.pop(key, None)


@common_actions.action()
def append_to_attr(obj, **attrs):
    for name, value in attrs.iteritems():
        if not hasattr(obj, name) or getattr(obj, name) is None:
            setattr(obj, name, [])
        getattr(obj, name).append(value)


@common_actions.action()
def remove_from_attr(obj, **attrs):
    for name, value in attrs.iteritems():
        if hasattr(obj, name):
            getattr(obj, name).remove(value)


@common_actions.action()
def update_in_attr(obj, **attrs):
    for name, value in attrs.iteritems():
        if not hasattr(obj, name) or getattr(obj, name) is None:
            setattr(obj, name, {})
        getattr(obj, name).update(value)


@common_actions.action()
def pop_in_attr(obj, **attrs):
    for name, value in attrs.iteritems():
        if not hasattr(obj, name) or getattr(obj, name) is None:
            setattr(obj, name, {})
        getattr(obj, name).pop(value, None)


@common_actions.action()
def populate_obj(obj, **attrs):
    populate_obj(obj, attrs)


@common_actions.action()
def incr_obj(obj, **attrs):
    """Increments context variables
    """
    for name, value in attrs.iteritems():
        v = getattr(obj, name, None)
        if not hasattr(obj, name) or v is None:
            v = 0
        setattr(obj, name, v + value)


@common_actions.action()
def call(obj, func_name, **kwargs):
    return getattr(obj, func_name)(**kwargs)


@common_actions.action('do', default_option='code')
def exec_python(code):
    return eval(code, globals(), current_context.vars)


@common_actions.action(default_option="code")
def abort(code, **kwargs):
    """Triggers flask.abort() using the specified http code
    """
    flask.abort(code, **kwargs)


@common_actions.action(default_option="view")
def redirect(view=None, url=None, **kwargs):
    """Redirects to the specified view or url
    """
    if view:
        if url:
            kwargs["url"] = url
        url = flask.url_for(view, **kwargs)
    current_context.exit(flask.redirect(url))


@common_actions.action(default_option="msg")
def flash(msg, label="success"):
    """Adds a flash message
    """
    flask.flash(msg, label)


@common_actions.action(default_option="__obj")
def jsonify(__obj=None, **obj):
    if __obj:
        obj = __obj
    current_context.exit(flask.jsonify(**obj))


@common_actions.action(default_option="filename")
def render_template(filename, **kwargs):
    return flask.render_template(filename, **kwargs)


@common_actions.action()
def set_headers(**kwargs):
    current_context.vars.response.headers.extend(kwargs)


@common_actions.action(default_option="msg")
def log(msg, level="info"):
    getattr(flask.current_app.logger, level)(msg)


@common_actions.action(default_option="msg")
def log_debug(msg):
    flask.current_app.logger.debug(msg)


@common_actions.action(default_option="name")
def send_signal(name, **kwargs):
    s = signal(name)
    s.send(**kwargs)


@common_actions.action(default_option="text", as_="slug")
def slugify(text, **kwargs):
    return slugify(text, **kwargs)