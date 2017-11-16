from logging import Formatter, PercentStyle, LogRecord
import traceback

DEFAULT_PROPERTIES = list(LogRecord('', '', '', '', '', '', '', '').__dict__.keys())
# The logging module sucks big time. when Formatter.getMessage is
# called, it just casually sets a message attribute on the
# record. Same thing with Formatter.format and asctime. This same
# extra handling has to be done also in logging/__init__.py, line
# 1387.
DEFAULT_PROPERTIES.extend(['message', 'asctime'])

def get_extras(record):
    if len(DEFAULT_PROPERTIES) == len(record.__dict__):
        return None
    extras = set(record.__dict__).difference(set(DEFAULT_PROPERTIES))
    if not extras:
        return None
    return {key: getattr(record, key) for key in extras}


class LogglyJSONFormatter(Formatter):

    def __init__(self, *args, **kwargs):
        super().__init__(self, *args, **kwargs)
        self._style = PercentStyle(PercentStyle.asctime_format)


    def format(self, record):
        # Need to do this to set time and exception fields on the
        # record. Python's logging module just loves state
        super().format(record)
        message = record.getMessage()
        if record.exc_info:
            message = '\n'.join(
                [message, ''.join(traceback.format_exception(*record.exc_info))])

        data = {
            'loggerName': record.name,
            'timestamp': record.asctime,
            'fileName': record.filename,
            'logRecordCreationTime': record.created,
            'functionName': record.funcName,
            'levelNo': record.levelno,
            'lineNo': record.lineno,
            'time': record.msecs,
            'levelName': record.levelname,
            'message': message
        }
        extras = get_extras(record)
        if extras:
            data['extra'] = extras
        return data


class ExtraDataFormatter(Formatter):

    def format(self, record):
        normal_format = super().format(record)
        extras = get_extras(record)
        if not extras:
            return normal_format
        parts = ['{}: {}'.format(key, extras[key])
                 for key in sorted(extras.keys())]
        record.msg = '{} {}'.format(record.msg, ' '.join(parts))
        return super().format(record)
