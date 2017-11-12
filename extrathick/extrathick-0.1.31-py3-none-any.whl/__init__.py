import logging
import steov

def anonify (obj):
    if isinstance(obj, dict):
        return steov.Anon({k: anonify(v) for k, v in obj.items()})
    if isinstance(obj, (list, set, tuple)):
        return type(obj)(map(anonify, obj))
    return obj

def unanonify (obj):
    if isinstance(obj, steov.Anon):
        obj = vars(obj)
    if isinstance(obj, dict):
        return {k: unanonify(v) for k, v in obj.items()}
    if isinstance(obj, (list, set, tuple)):
        return type(obj)(map(unanonify, obj))
    return obj


def dictstat (st):
    return {attr: getattr(st, "st_"+attr) for attr in [
        "mode",
        "ino",
        "dev",
        "nlink",
        "uid",
        "gid",
        "size",
        "atime",
        "mtime",
        "ctime",
    ]}

def anonstat (st):
    return steov.Anon(dictstat(st))



# http://wiki.python.org/moin/PythonDecoratorLibrary#Memoize
class memoized:
    """
    Decorator. Caches a function's return value each time it is called.
    If called later with the same arguments, the cached value is returned
    (not reevaluated).
    """
    def __init__ (self, function):
        self._function = function
        self._cache = dict()

    def __call__ (self, *args):
        import collections
        if not isinstance(args, collections.Hashable):
            # uncacheable. a list, for instance.
            # better to not cache than blow up.
            return self._function(*args)
        if args in self._cache:
            return self._cache[args]
        else:
            value = self._cache[args] = self._function(*args)
            return value

    def reload (self):
        self._cache.clear()

    # TODO I don't understand this just yet. look up python descriptors
    def __get__ (self, obj, objtype):
        import functools
        """Support instance methods."""
        return functools.partial(self.__call__, obj)



@memoized
def _get_dt_pattern ():
    import re
    return re.compile(r"\A(\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}\.\d{6})(\d{3})(?:(Z)|([\+\-]\d{2}):(\d{2}))\Z")

_dt_fmt = "%Y-%m-%dT%H:%M:%S.%f"
def dt_serialize (dt):
    fmt = _dt_fmt
    if dt.tzinfo is None:
        tz = "Z"
    else:
        hours, minutes = divmod(int(dt.utcoffset().total_seconds()/60.0), 60)
        tz = "{hours:+03}:{minutes:02}".format(**locals())
    return "{dt:{fmt}}000{tz}".format(**locals())

def dt_deserialize (dt_str):
    from datetime import datetime, timedelta, timezone
    m = _get_dt_pattern().search(dt_str)
    if not m:
        error = ValueError("dt_str: incorrect format. must match regex: " + _get_dt_pattern().pattern)
        error.dt_str = dt_str
        raise error
    dt_str, nanosec_str, tz_str, hours_str, minutes_str = m.groups()
    dt = datetime.strptime(dt_str, _dt_fmt)
    if hours_str:
        dt = dt.replace(tzinfo=timezone(timedelta(hours=int(hours_str), minutes=int(minutes_str))))
    return dt



def json_default (obj):
    if isinstance(obj, bytes):
        import base64
        return base64.b64encode(obj)
    import datetime
    if isinstance(obj, datetime.datetime):
        return dt_serialize(obj)
    if isinstance(obj, datetime.date):
        return obj.strftime("%Y-%m-%d")
    if isinstance(obj, datetime.timedelta):
        return obj.total_seconds()
    import uuid
    if isinstance(obj, uuid.UUID):
        return str(obj)
    import decimal
    if isinstance(obj, decimal.Decimal):
        return float(obj)
    raise TypeError("{!a} is not JSON serializable".format(obj))



def safecall (function, *args, **kwargs):
    try:
        value = function(*args, **kwargs)
    except Exception as ex:
        return False, (type(ex), ex, format_exc())
    else:
        return True, value

def passthru (function, *args, **kwargs):
    return function(*args, **kwargs)

def always (value):
    def factory (*args, **kwargs):
        return value
    return factory

def _logging_format_time (self, record, datefmt=None):
    import datetime
    created_utc = datetime.datetime.utcfromtimestamp(record.created)
    if datefmt is not None:
        return created_utc.strftime(datefmt)
    else:
        return dt_serialize(created_utc)

def logging_basic_config (logfile, level=logging.DEBUG):
    from os import makedirs
    from os.path import abspath, dirname
    makedirs(dirname(abspath(logfile)), exist_ok=True)
    logging.Formatter.formatTime = _logging_format_time
    logging.basicConfig(format="%(asctime)s %(levelname)s %(name)s %(thread)d %(message)s", level=level, filename=logfile)

def logging_adv_config (dir, name, file_level=logging.DEBUG, console_level=logging.INFO):
    from os import makedirs
    from os.path import abspath, dirname, join
    from datetime import datetime as dt
    from logging.config import dictConfig
    dir = abspath(dir)
    if "/" in name:
        raise ValueError("name must not be a path containing parent directories")
    file = join(dir, name + ".log." + dt.utcnow().strftime("%Y-%m-%d"))
    makedirs(dir, exist_ok=True)
    logging.Formatter.formatTime = _logging_format_time

    dictConfig({
        "version": 1,
        "disable_existing_loggers": False,
        "formatters": {
            "full": {
                "format": "%(asctime)s %(levelname)s %(name)s %(thread)d %(message)s",
            },
            "simple": {
                "format": "%(asctime)s %(levelname)s %(name)s %(message)s",
                "datefmt": "%Y-%m-%d %H:%M:%S",
            },
        },
        "handlers": {
            "file": {
                # TODO someday, make this a proper rotating file handler
                "class": "logging.FileHandler",
                "filename": file,
                "level": file_level,
                "formatter": "full",
                "encoding": "utf-8",
            },
            "console": {
                "class": "logging.StreamHandler",
                "stream": "ext://sys.stderr",
                "level": console_level,
                "formatter": "simple",
            },
        },
        "root": {
            "handlers": [
                "file",
                "console",
            ],
            "level": logging.DEBUG,
        },
    })

def log_exception (logger, level, label, exception, stacktrace=None):
    if label is not None:
        prefix = label + "."
    else:
        prefix = ""
    if stacktrace is None:
        stacktrace = steov.format_exc(1)
    for line in stacktrace.splitlines(keepends=False):
        logger.log(level, prefix + "stacktrace.line: " + line)
    for k, v in getattr(exception, "__dict__", {}).items():
        logger.log(level, prefix + "exception." + k + ": " + ascii(v))

def get_type_name (t):
    return t.__module__ + "." + t.__name__

def get_function_name (f):
    if not callable(f):
        raise TypeError("Not callable: " + str(f))
    try:
        module = f.__module__
        if module is None:
            prefix = get_type_full_name(type(f.__self__))
        elif module == "__main__":
            prefix = ""
        else:
            prefix = module
        return prefix + ( "." if prefix else "" ) + f.__qualname__
    except Exception:
        # TODO log error
        return str(f)

def groupby (iterable, key_func=steov.iden):
    import collections
    retval = collections.defaultdict(list)
    for item in iterable:
        retval[key_func(item)].append(item)
    return retval
