import flask.signals
from .actions import load_grouped_actions, current_context, ensure_context


_signals = flask.signals.Namespace()
signal = _signals.signal


def listens_to(name, sender=None, weak=True):
    """Listens to a named signal
    """
    def decorator(f):
        if sender:
            return signal(name).connect(f, sender=sender, weak=weak)
        return signal(name).connect(f, weak=weak)
    return decorator


def create_action_listener(event, actions):
    def callback(sender, **kwargs):
        with ensure_context():
            with current_context.clone(sender=sender, **kwargs):
                actions.execute()
    signal(event).connect(callback, weak=False)


def create_listeners_from_config(config):
    for spec in config:
        create_action_listener(spec['name'], load_grouped_actions(spec))