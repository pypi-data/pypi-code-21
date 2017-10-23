import linecache
import logging
from logging.handlers import RotatingFileHandler
import sys
import traceback

from aalam_common.config import cfg


class StackReporter(object):
    def __init__(self, exc_frame):
        self.frame = exc_frame
        self.filename = exc_frame.f_code.co_filename
        self.lineno = exc_frame.f_lineno
        self.function = exc_frame.f_code.co_name

    def get_file_line(self, from_line):
        code = linecache.getline(self.filename, from_line,
                                 self.frame.f_globals)
        if code:
            code = code.rstrip('\n')

        return "%d: %s" % (from_line, code)

    def get_pre_context(self, num_lines):
        from_line = self.lineno - num_lines if self.lineno > num_lines else 0
        ret = []
        while from_line < self.lineno:
            ret.append(self.get_file_line(from_line))
            from_line += 1

        return ret

    def get_post_context(self, num_lines):
        from_line = self.lineno
        to_line = self.lineno + num_lines
        ret = []
        while from_line <= to_line:
            ret.append(self.get_file_line(from_line))
            from_line += 1

        return ret

    def get_locals(self):
        ret = []
        for (k, v) in self.frame.f_locals.items():
            if not (k.startswith('__') and k.endswith('__')):
                ret.append('{} = {}'.format(k, v))

        return ret

    def get_globals(self):
        ret = []
        for (k, v) in self.frame.f_globals.items():
            ret.append('{} = {}'.format(k, v))

        return ret


class ExceptionTraceback(object):
    def __init__(self, exc_type, exc_value, exc_tb):
        self.exc_type = exc_type
        self.exc_value = exc_value
        self.exc_tb = exc_tb

    def format_exception(self):
        ret = ["Traceback of the most recent exception"]
        frame_num = 0
        tb = self.exc_tb
        ret += traceback.format_exception_only(self.exc_type, self.exc_value)
        ret += [' ----------------------------------------- ']
        while tb is not None:
            if tb.tb_frame.f_locals.get('__traceback_hide__'):
                tb = tb.tb_next
                continue

            stack = StackReporter(tb.tb_frame)
            ret += ["File %s, line %s, function %s" %
                    (stack.filename, stack.lineno, stack.function)]
            ret += [""]
            ret.extend(stack.get_locals())
            ret += [""]
            ret.extend(stack.get_pre_context(3))
            ret.extend(stack.get_post_context(3))
            ret += [' ----------- End of frame %d ------------- '
                    % (frame_num)]

            frame_num += 1
            tb = tb.tb_next

        return ret


def _except_hook(exc_type, exc_value, exc_tb):
    if getattr(cfg.CONF.debug, "detail_exc", False):
        etb = ExceptionTraceback(exc_type, exc_value, exc_tb)
        lines = etb.format_exception()

        for line in lines:
            logging.critical(line)

    traceback.print_exception(exc_type, exc_value, exc_tb)


def init_logging(logger):
    cfg_debug = getattr(cfg.CONF, "debug", None)
    ll = getattr(
        logging, cfg.CONF.debug.log_level.upper() if cfg_debug else "DEBUG")
    if cfg_debug and getattr(cfg_debug, "log_file", None):
        lh = RotatingFileHandler(cfg_debug.log_file,
                                 maxBytes=10485760,
                                 backupCount=5)
        FORMAT = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
        lh.setFormatter(logging.Formatter(FORMAT))
        logger.addHandler(lh)

    logger.setLevel(ll)


# init_debug() should be called at the module initialization
# and only once. This will register for the logging,
# exception hooks, etc
def init_debug():
    sys.excepthook = _except_hook
    init_logging(logging.getLogger())
