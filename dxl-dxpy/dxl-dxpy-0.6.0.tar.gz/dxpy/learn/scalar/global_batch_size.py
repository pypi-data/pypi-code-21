import tensorflow as tf

from .base import ScalarVariable


def batch_size():
    return graph().as_tensor()


def graph():
    if _instance is None:
        raise TypeError("Global batch size not created yet.")
    return _instance


_instance = None


class _BatchSize(ScalarVariable):
    def __init__(self):
        super().__init__('batch_size')


def create():
    global _instance
    _instance = _BatchSize('batch_size')
