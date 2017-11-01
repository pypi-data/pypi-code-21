# common
import functools

# my
from admin_logs.log import get_record, set_record, RequestRecord


class Log(object):

    def __init__(self):
        self.old_request = None

    def __enter__(self):
        self.old_request = get_record()
        record = RequestRecord()
        set_record(record)

    def __exit__(self, exc_type, exc_val, exc_tb):
        record = get_record()
        record.finish_request()

        set_record(self.old_request)


def log(func):
    @functools.wraps(func)
    def inner(*args, **kwargs):
        with Log():
            return func(*args, **kwargs)
    return inner
