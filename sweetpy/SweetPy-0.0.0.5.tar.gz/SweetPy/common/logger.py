from .datetime_plus import DatetimePlus
from .func_helper import FuncHelper
import logging
from ..core.global_share import GlobalShareValue
from .configer import Configer


class Logger(object):
    def __init__(self):
        _configer_file_path = GlobalShareValue.get_configer_file_path()
        _configer = Configer(_configer_file_path)
        _is_debug = _configer.is_debug

        path = FuncHelper.get_curr_path() + '/' + 'log'
        FuncHelper.create_dirs(path)
        date_str = DatetimePlus.get_nowdate_to_str()
        log_path = path + '/' + date_str
        if _is_debug:
            level = logging.DEBUG
        else:
            level = logging.ERROR
        logging.basicConfig(level=level,
                            format='%(asctime)s %(filename)s[line:%(lineno)d] %(levelname)s %(message)s',
                            datefmt='%Y-%m-%d %H:%M:%S',
                            filename=log_path + '.log',
                            filemode='a')
        if _is_debug:
            console = logging.StreamHandler()
            console.setLevel(logging.DEBUG)
            formatter = logging.Formatter('%(asctime)s : %(levelname)-8s %(message)s',datefmt='%Y-%m-%d %H:%M:%S')
            console.setFormatter(formatter)
            logging.getLogger('').addHandler(console)

    def info(self, msg):
        logging.info(msg)

    def debug(self, msg):
        logging.debug(msg)

    def warning(self, msg):
        logging.warning(msg)

    def error(self, msg):
        logging.error(msg)

    def fatal(self, msg):
        logging.fatal(msg)

    def critical(self, msg):
        logging.critical(msg)
