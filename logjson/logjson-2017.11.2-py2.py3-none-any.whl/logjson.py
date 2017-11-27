"""
logjson
=======

A Python logging Handler for JSON logs (with LogStash support)

"""
import sys
import logging
import json
import datetime
import platform
import traceback
import copy


__version__ = '2017.11.2'


class JSONHandler(logging.StreamHandler):
    def __init__(self, logstash_mode=False, pretty=False, *args, **kwargs):
        # super().__init__(*args, stream=sys.stdout, **kwargs)
        print(kwargs)
        super(JSONHandler, self).__init__(*args, **kwargs)
        self.logstash_mode = logstash_mode
        self.pretty = pretty

    def format(self, record):
        # type: (logging.LogRecord) -> str
        """Don't even need a Formatter class at all."""
        record.message = record.getMessage()
        if hasattr(record, 'exc_info') and record.exc_info:
            record.exc_text = ''.join(traceback.format_exception(*record.exc_info))
            record.message += '\n' + record.exc_text
        # Actual isoformat. self.formatTime() is not the same.
        if sys.version_info.major == 2:  # pragma: no cover
            record.created_iso = datetime.datetime.fromtimestamp(
                record.created
            ).isoformat()
        else:
            record.created_iso = datetime.datetime.fromtimestamp(
                record.created, datetime.timezone.utc
            ).isoformat()

        if self.logstash_mode:
            d = {
                '@message': record.message,
                '@source_host': platform.node(),
                '@timestamp': record.created_iso,
                '@fields': copy.copy(record.__dict__)
            }
            # Avoid duplicates
            del d['@fields']['message']
            del d['@fields']['created_iso']
            # This doesn't serialise to JSON well.
            del d['@fields']['exc_info']
        else:
            d = copy.copy(record.__dict__)
            # This doesn't serialise to JSON well.
            del d['exc_info']

        return json.dumps(d, indent=2 if self.pretty else None)
