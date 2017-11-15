"""Some utilities"""

import errno
import os
import logging
from logging.handlers import TimedRotatingFileHandler
from . import constants as C


class ColorFormatter(logging.Formatter):
    """ A simple class to color log output
    """
    FORMAT = ("[%(app_name)-10s][%(levelname)22s] "
              "%(message)s "
              "(%(filename)s:%(lineno)d)")

    COLORS = {}
    COLORS['WARNING'] = "\033[%sm" % (";".join([C.BOLD, C.FG_YELLOW, C.BG_BLACK]))
    COLORS['INFO'] = "\033[%sm" % (";".join([C.NO_EFFECT, C.FG_GREEN, C.BG_BLACK]))
    COLORS['DEBUG'] = "\033[%sm" % (";".join([C.NO_EFFECT, C.FG_BLUE, C.BG_BLACK]))
    COLORS['CRITICAL'] = "\033[%sm" % (";".join([C.BOLD, C.FG_RED, C.BG_BLACK]))
    COLORS['ERROR'] = "\033[%sm" % (";".join([C.NO_EFFECT, C.FG_RED, C.BG_BLACK]))
    COLORS['NAME'] = "\033[%sm" % (";".join(C.FAINT))

    def formatter_msg(self, msg, use_color=True):
        """ Formats a console message with fancy colors
        """

        if use_color:
            msg = msg.replace("$RESET", C.RESET_SEQ).replace("$BOLD", C.BOLD_SEQ)
        else:
            msg = msg.replace("$RESET", "").replace("$BOLD", "")
        return msg

    def __init__(self, use_color=True):
        msg = self.formatter_msg(self.FORMAT, use_color)
        logging.Formatter.__init__(self, msg)
        self.use_color = use_color

    def format(self, record):
        levelname = record.levelname
        app_name = record.app_name
        if self.use_color and levelname in self.COLORS:
            levelname_color = self.COLORS[levelname] + levelname + C.RESET_SEQ
            record.levelname = levelname_color
            name_color = self.COLORS['NAME'] + app_name + C.RESET_SEQ
            record.app_name = name_color


        return logging.Formatter.format(self, record)

def mkdir_p(path):
    """ Make a directory if it deosn't exists

    Args:
        path (string): The directory to ensure

    """
    try:
        os.makedirs(path)
    except OSError as exc:  # Python >2.5
        if exc.errno == errno.EEXIST and os.path.isdir(path):
            pass
        else:
            raise


def create_logger(settings):
    """Build a logger instance

    file_level and console_level, should be one of the levels of the
    logging modules. Example: DEBUG, INFO, WARNING etc.

    Args:

        file_level: (str): The file logging level
        console_level: (str): The file logging level
        name (str): The name for the log messages
        path (str): The directory for the logs

    Returns:

        a logger

    """
    mkdir_p(os.path.dirname(settings.logging.file.path))
    logger = logging.getLogger(__package__)
    logger.propagate = True
    logger.setLevel(logging.DEBUG)
    formatter = logging.Formatter('%(asctime)s - %(app_name)s - %(levelname)s - %(message)s')

    file_handler = TimedRotatingFileHandler(settings.logging.file.path,
                                            when=settings.logging.file.when,
                                            interval=settings.logging.file.interval,
                                            backupCount=settings.logging.file.backupCount)
    file_handler.setLevel(logging.getLevelName(settings.logging.levels.file))
    file_handler.setFormatter(formatter)
    logger.addHandler(file_handler)

    console_handler = logging.StreamHandler()
    console_handler.setLevel(logging.getLevelName(settings.logging.levels.file))
    console_handler.setFormatter(ColorFormatter())
    logger.addHandler(console_handler)

    extra = {'app_name':settings.app_name}
    logger = logging.LoggerAdapter(logger, extra)

    return logger
