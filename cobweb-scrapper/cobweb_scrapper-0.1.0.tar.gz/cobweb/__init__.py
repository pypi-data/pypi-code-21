"""
The fundamental 'Cobweb' class that represents all of the app functionality
"""

import logging

from multiprocessing import cpu_count, Queue
from types import FunctionType

import urllib3

from cobweb.spiders import Spider
from cobweb.settings import Settings
from cobweb.adapters.http import Http
from cobweb.link_extractor import LinkExtractor
from cobweb.common import Singleton


class Cobweb(metaclass=Singleton):
    """
    The fundamental 'Cobweb' class that represents all of the app functionality
    """

    def __init__(
            self,
            start_url=None,
            settings=Settings(),
            adapter=Http(),
            link_extractor=LinkExtractor(),
            log_to_file: bool = False,
            logger_filename: str = None,
            file_logger_level=logging.INFO,
            console_logger_level=logging.INFO,
    ):
        self.start_url = start_url
        self._settings = settings
        self._spiders = None
        self._queue = Queue()
        self._adapter = adapter
        self._link_extractor = link_extractor
        self._default_process_function = None

        self.log_format = '[%(processName)s: %(asctime)s] %(levelname)-8s %(message)s'
        self.log_to_file = log_to_file
        self.logger_filename = logger_filename
        self.file_logger_level = file_logger_level
        self.console_logger_level = console_logger_level

    @property
    def logger(self):
        return logging.getLogger("cobweb")

    @property
    def settings(self):
        return self._settings

    @property
    def queue(self):
        return self._queue

    @property
    def adapter(self):
        return self._adapter

    @property
    def link_extractor(self):
        return self._link_extractor

    @link_extractor.setter
    def domain(self, value):
        self._link_extractor = value

    @property
    def default_process_function(self):
        return self._default_process_function

    @default_process_function.setter
    def default_process_function(self, value):
        if not isinstance(value, FunctionType) and value is not None:
            raise ValueError("Trying to set not a function to callback")
        else:
            self._default_process_function = value

    def __getitem__(self, item: int):
        return self._spiders[item]

    def follow_rules(self, rules):
        self._link_extractor.follow_patterns = rules

    def exclude_rules(self, rules):
        self._link_extractor.exclude_patterns = rules

    def setup_logging(self) -> None:
        """
        method for configuring logging in all application
        :return: None
        """

        logger = self.logger
        logger.setLevel(self.console_logger_level)
        formatter = logging.Formatter(self.log_format)

        if self.log_to_file:
            if not self.logger_filename:
                raise ValueError("'log_to_file' was on but no 'logger_filename' specified")
            file_handler = logging.FileHandler('spam.log')
            file_handler.setLevel(logging.DEBUG)
            file_handler.setFormatter(formatter)
            logger.addHandler(file_handler)

        console_handler = logging.StreamHandler()
        console_handler.setLevel(logging.ERROR)
        console_handler.setFormatter(formatter)
        logger.addHandler(console_handler)

        logging.basicConfig(format=self.log_format)

    def start_from(self, url: str):
        self.start_url = url
        self.queue.put(self.start_url)

    def get_spider(self):
        if self.default_process_function is None:
            raise ValueError("No process function set")
        spider = Spider(
            queue=self.queue,
            settings=self.settings,
            adapter=self.adapter,
            link_extractor=self.link_extractor
        )
        spider.process_response = self.default_process_function
        return spider

    def populate_spiders(self, num=cpu_count()):
        self._spiders = [
            self.get_spider()
            for _ in range(num)
        ]

    def add_spider(self, spider: Spider):
        spider._queue = self._queue
        self._spiders.append(spider)

    def start(self):
        if not self.start_url:
            raise ValueError("No start url specified")

        self.setup_logging()
        urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)
        self.logger.info("starting spiders")

        self.logger.debug("on start queue size: %s", self.queue.qsize())

        for spider in self._spiders:
            spider.start()

    def stop(self):
        self.logger.info("stopping spiders")
        for spider in self._spiders:
            spider.stop()
