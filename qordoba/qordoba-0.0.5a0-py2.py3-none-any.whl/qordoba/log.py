import logging
import os
import sys


class BaseFormatter(logging.Formatter):
    def __init__(self, fmt=None, datefmt=None, traceback=False):
        FORMAT = '%(customlevelname)s %(message)s'
        super(BaseFormatter, self).__init__(fmt=FORMAT, datefmt=datefmt)
        self._traceback = traceback

    def format(self, record):
        record.__dict__['customlevelname'] = self._get_levelname(record.levelname)
        # format multiline messages 'nicely' to make it clear they are together
        if hasattr(record.msg, 'replace'):
            record.msg = record.msg.replace('\n', '\n  | ')
        return super(BaseFormatter, self).format(record)

    def formatException(self, ei):
        ''' prefix traceback info for better representation '''
        # .formatException returns a bytestring in py2 and unicode in py3
        # since .format will handle unicode conversion,
        # str() calls are used to normalize formatting string
        s = super(BaseFormatter, self).formatException(ei)
        # fancy format traceback
        s = str('\n').join(str('  | ') + line for line in s.splitlines())
        # separate the traceback from the preceding lines
        s = str('  |___\n{}').format(s)
        if not self._traceback:
            return str('')
        return s

    def _get_levelname(self, name):
        ''' NOOP: overridden by subclasses '''
        return name


class ANSIFormatter(BaseFormatter):
    ANSI_CODES = {
        'red': '\033[1;31m',
        'yellow': '\033[1;33m',
        'cyan': '\033[1;36m',
        'white': '\033[1;37m',
        'bgred': '\033[1;41m',
        'bggrey': '\033[1;100m',
        'reset': '\033[0;m'}

    LEVEL_COLORS = {
        'INFO': 'cyan',
        'WARNING': 'yellow',
        'ERROR': 'red',
        'CRITICAL': 'bgred',
        'DEBUG': 'bggrey'}

    def _get_levelname(self, name):
        color = self.ANSI_CODES[self.LEVEL_COLORS.get(name, 'white')]
        if name == 'INFO':
            fmt = '{0}->{2}'
        else:
            fmt = '{0}{1}{2}:'
        return fmt.format(color, name, self.ANSI_CODES['reset'])


class TextFormatter(BaseFormatter):
    """
    Convert a `logging.LogRecord' object into text.
    """

    def _get_levelname(self, name):
        if name == 'INFO':
            return '->'
        else:
            return name + ':'


def init(level=None, traceback=False, handler=logging.StreamHandler()):
    logger = logging.getLogger('qordoba')

    if os.isatty(sys.stdout.fileno()) and not sys.platform.startswith('win'):
        fmt = ANSIFormatter(traceback=traceback)
    else:
        fmt = TextFormatter(traceback=traceback)
    handler.setFormatter(fmt)
    logger.addHandler(handler)

    if level:
        logger.setLevel(level)
        if level == logging.INFO:
            logging.getLogger("requests").setLevel(logging.WARNING)
