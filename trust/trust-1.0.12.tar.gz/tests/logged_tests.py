import logging
import unittest


class LoggedTests(unittest.TestCase):
    def setUp(self):
        logging.basicConfig(level=logging.DEBUG)
        self._logger = logging.getLogger(__name__)
        print()
        self._logger.info(
            "--- Testing %s.%s ---",
            self.__class__.__name__,
            self._testMethodName)
