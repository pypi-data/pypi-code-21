import sys

from contextlib import contextmanager
from functools import wraps

from .tecutil_connector import _tecutil_connector, _tecutil


_FORCE_RECORDING = False


def _enable_force_recording(enable):
    global _FORCE_RECORDING
    _FORCE_RECORDING = enable


@contextmanager
def lock(with_recording=True):
    """
    ParentLockStart takes a boolean: ShutdownImplicitRecording
    ShutdownImplicitRecording = True -> No recording
    ShutdownImplicitRecording = False -> With Recording
    """
    if _tecutil_connector.connected:
        yield
    else:
        _tecutil.ParentLockStart(not (with_recording or _FORCE_RECORDING))
        try:
            yield
        finally:
            _tecutil.handle.tecUtilParentLockFinish()


if sys.version_info < (3, 3):
    """
    This allows the contextmanager lock
    to be used as a decorator as well as a
    context. (This is already included in Py 3.3+)
    """
    from functools import wraps

    _lock = lock

    class lock(object):
        def __init__(self, *args, **kwargs):
            self.args = args
            self.kwargs = kwargs
            self._cm = _lock

        def __enter__(self, *args, **kwargs):
            self.cm = self._cm(*self.args, **self.kwargs)
            return self.cm.__enter__(*args, **kwargs)

        def __exit__(self, *args, **kwargs):
            return self.cm.__exit__(*args, **kwargs)

        def __call__(self, func):
            @wraps(func)
            def wrapper(*args, **kwargs):
                with self._cm(*self.args, **self.kwargs):
                    return func(*args, **kwargs)

            return wrapper
