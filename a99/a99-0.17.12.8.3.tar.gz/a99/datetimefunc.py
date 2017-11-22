import datetime

__all__ = ["now_str"]

def now_str():
    return datetime.datetime.strftime(datetime.datetime.now(), '%Y-%m-%d %H:%M:%S')
