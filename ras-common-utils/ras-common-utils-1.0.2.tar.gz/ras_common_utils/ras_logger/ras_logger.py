import logging
import sys

import structlog

LEVELS = {'debug': logging.DEBUG,
          'info': logging.INFO,
          'warning': logging.WARNING,
          'error': logging.ERROR,
          'critical': logging.CRITICAL}


def _configure_structlogger(config):
    def add_service_name(logger, method_name, event_dict):  # pylint: disable=unused-argument
        """
        Add the service name to the event dict.
        """
        event_dict['service'] = config['NAME']
        return event_dict

    processors = [
        structlog.processors.TimeStamper(fmt='iso'),
        structlog.stdlib.filter_by_level,
        add_service_name,
        structlog.stdlib.add_log_level,
        structlog.processors.format_exc_info,
        structlog.processors.JSONRenderer(sort_keys=True)
    ]
    structlog.configure(
        processors=processors,
        context_class=structlog.threadlocal.wrap_dict(dict),
        logger_factory=structlog.stdlib.LoggerFactory(),
        wrapper_class=structlog.stdlib.BoundLogger,
        cache_logger_on_first_use=True
    )


def _configure_basiclogger(config):
    logging.basicConfig(
        format="%(message)s",
        stream=sys.stdout,
        level=LEVELS.get(config.get('LOG_LEVEL', 'INFO').lower(), logging.INFO)
    )


def configure_logger(config):
    _configure_basiclogger(config)
    _configure_structlogger(config)
