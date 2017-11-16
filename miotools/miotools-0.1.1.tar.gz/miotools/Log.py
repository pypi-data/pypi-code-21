"""
Logger Util for python
"""
import logging


class LoggerWrapper:
    """
    Wrap system logger
    """
    def __init__(self) -> None:
        self._logger = logging.getLogger('transaction')
        self._logger.setLevel(logging.DEBUG)
        self._ch = logging.StreamHandler()
        self._ch.setLevel(logging.DEBUG)
        self._ch.setFormatter(logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s'))
        self._logger.addHandler(self._ch)

    def get_logger(self):
        """
        get class instance logger
        :return:
        """
        return self._logger


_LOGGER = LoggerWrapper().get_logger()


def get_logger():
    """
    public function get logger singleton
    :return:
    """
    return _LOGGER
