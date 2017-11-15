from datetime import datetime
from threading import Lock

_print_time = datetime.utcnow()
_print_lock = Lock()


def sync_print(out, err):
    from sys import stderr
    from sys import stdout

    try:
        _print_lock.acquire()
        print(out, flush=True, file=stdout, end='')
        print(err, flush=True, file=stderr, end='')
    finally:
        _print_lock.release()


class BaseActionHandler(object):
    def __init__(self, resource):
        from io import StringIO

        self._resource = resource
        self._out = StringIO()
        self._err = StringIO()

    def try_sync(self, phase, settings, variables):
        return True

    def fore_phase(self, phase, settings, variables):
        pass

    def fore_children(self, phase, settings, variables):
        if self._resource.is_dirty:
            self._time_from = datetime.utcnow()

    def post_children(self, phase, settings, variables):
        if self._resource.is_dirty:
            self._time_till = datetime.utcnow()
            self._out.write(
                '{0:%H:%M}   {1:>+4}: \033[36;1m<>\033[0m {2} ({3})\n'.format(
                self._time_till,
                (int)((self._time_till - _print_time).total_seconds()),
                self._resource.path,
                (int)((self._time_till - self._time_from).total_seconds())))

            sync_print(self._out.getvalue(), self._err.getvalue())

    def post_phase(self, phase, settings, variables):
        pass

class BaseRefreshHandler(BaseActionHandler):
    pass


class BaseDestroyHandler(BaseActionHandler):
    pass


class BaseHandler(object):
    def __init__(self, refresh, destroy, resource):
        self._resource = resource
        self.refresh = refresh(resource) if refresh else None
        self.destroy = destroy(resource) if destroy else None
