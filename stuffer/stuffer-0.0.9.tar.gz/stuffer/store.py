"""Key/value store for passing state between invocations of stuffer."""

from stuffer.configuration import config
from stuffer.content import StringArg
from .core import Action


def _store_dir():
    return config.store_directory


def _create_store_dir():
    if not _store_dir().is_dir():
        _store_dir().mkdir(parents=True)


def _key_path(key):
    return _store_dir().joinpath(key)


def set_value(key: str, value: str):
    """Set a key to a value.

    Parameters
    ----------
    key
        Key name.
    value
        Value of key.
    """
    _create_store_dir()
    with _key_path(key).open('w') as f:
        f.write(value)


def get_value(key):
    """Retrieve the value of a key.

    Parameters
    ----------
    key
        Key name.

    Returns
    -------
    The value of the key, or None if no key value has been set.
    """
    if _key_path(key).exists():
        with _key_path(key).open('r') as f:
            return f.read()


class Set(Action):
    """Set the key value. Same as ``set``, but implemented as Action.

    Parameters
    ----------
    key
        Key name.
    value
        Value of key.
    """
    def __init__(self, key: StringArg, value: StringArg):
        self.key = key
        self.value = value
        super().__init__()

    def run(self):
        set_value(self.key, self.value)
