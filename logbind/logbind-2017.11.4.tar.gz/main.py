import logging
import sys
import json
import datetime
import platform
import traceback


class JSONHandler(logging.StreamHandler):
    def __init__(self, *args, logstash_mode=False, **kwargs):
        # super().__init__(*args, stream=sys.stdout, **kwargs)
        super().__init__(*args, **kwargs)
        self.logstash_mode = logstash_mode

    def format(self, record: logging.LogRecord):
        """Don't even need a Formatter class at all."""
        record.message = record.getMessage()
        if record.exc_info:
            record.exc_text = ''.join(traceback.format_exception(*record.exc_info))
            del record.exc_info
            record.message += '\n' + record.exc_text
        # Actual isoformat. self.formatTime() is not the same.
        record.created_iso = datetime.datetime.fromtimestamp(
            record.created, datetime.timezone.utc
        ).isoformat()

        if self.logstash_mode:
            d = {
                '@message': record.message,
                '@source_host': platform.node(),
                '@timestamp': record.created_iso,
                '@fields': record.__dict__,
            }
            # Avoid repetition
            del record.message
            del record.created_iso
        else:
            d = record.__dict__
        return json.dumps(d, indent=2)


def logwrap(logger, **kwargs) -> logging.LoggerAdapter:

    class Ad(logging.LoggerAdapter):
        def __init__(self, logger, extra):
            if hasattr(logger, "extra"):
                # Reuse "extra" from the given logger
                extra.update(logger.extra)
            super().__init__(logger, extra)

    adapter = Ad(logger, kwargs)
    return adapter


logging.basicConfig(level='DEBUG', handlers=[JSONHandler()])


logging.info('hi %s %s!', 'you', 'there')

try:
    1/0
except:
    logging.exception('Something went %s wrong:', 'horribly')


logging.info('blah', extra=dict(a=1, b=2))


logger = logging.getLogger('blah')
logger.warning('Just checking %s', 'hell yeah')

log2 = logwrap(logger, aaa=1, bbb=2)
log2.info('But does it work tho?')

log3 = logwrap(log2, ccc=3, ddd=4)
log3.info('And the wrapper?')
