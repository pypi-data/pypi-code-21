import multiprocessing
import logging

from queue import Empty
from types import FunctionType

from urllib.parse import unquote

from cobweb.adapters import AbstractAdapter
from cobweb.adapters.http import Http
from cobweb.link_extractor import LinkExtractor
from cobweb.settings import Settings


class Spider(multiprocessing.Process):

    NORMAL = 0

    def __init__(
            self,
            queue=None,
            settings: Settings = Settings(),
            adapter: AbstractAdapter = Http(),
            link_extractor: LinkExtractor = LinkExtractor(),
            process_response: FunctionType = None,
            on_failure_callback: FunctionType = None,
            on_queue_timeout_callback: FunctionType = None,
            validator: FunctionType = None):

        multiprocessing.Process.__init__(self)

        self._queue = queue
        self._link_extractor = link_extractor
        self._settings = settings
        self._adapter = adapter
        self._on_failure_callback = None
        self._on_queue_timeout_callback = None
        self._process_response = None
        self._validator = None

        self.daemon = False
        self.keep_alive = True
        self.process_response = process_response
        self.on_failure_callback = on_failure_callback
        self.on_queue_timeout = on_queue_timeout_callback
        self.validator = validator

    @property
    def logger(self):
        return logging.getLogger('cobweb.spiders')

    @property
    def adapter(self):
        return self._adapter

    @property
    def on_failure_callback(self):
        if self._on_failure_callback:
            return self._on_failure_callback
        else:
            return self._settings.default_error_handler

    @on_failure_callback.setter
    def on_failure_callback(self, value: FunctionType):
        if not isinstance(value, FunctionType) and value is not None:
            raise ValueError("Trying to set not a function to callback")
        else:
            self._on_failure_callback = value

    @property
    def on_queue_timeout(self):
        if self._on_queue_timeout_callback:
            return self._on_queue_timeout_callback
        else:
            return self._settings.default_queue_timeout_handler

    @on_queue_timeout.setter
    def on_queue_timeout(self, value: FunctionType):
        if not isinstance(value, FunctionType) and value is not None:
            raise ValueError("Trying to set not a function to callback")
        else:
            self._on_queue_timeout_callback = value

    @property
    def process_response(self):
        return self._process_response

    @process_response.setter
    def process_response(self, value: FunctionType):
        if not isinstance(value, FunctionType) and value is not None:
            raise ValueError("Trying to set not a function to callback")
        else:
            self._process_response = value

    @property
    def validator(self):
        return self._validator

    @validator.setter
    def validator(self, value: FunctionType):
        if not isinstance(value, FunctionType) and value is not None:
            raise ValueError("Trying to set not a function to callback")
        else:
            self._validator = value

    @property
    def queue(self):
        return self._queue

    @queue.setter
    def queue(self, value):
        self._queue = value

    @property
    def keep_alive_timeout(self):
        return self._settings.keep_alive_timeout

    @property
    def block_level(self):
        return self._settings.block_level

    @property
    def success_codes(self):
        return self._settings.success_codes

    @property
    def failure_codes(self):
        return self._settings.failure_codes

    @property
    def settings(self):
        raise AttributeError("Settings object isn't directly accessible")

    @settings.setter
    def settings(self, value: Settings):
        self._settings = value

    def is_alive(self):
        return self.keep_alive

    def stop(self):
        self.keep_alive = False

    def _extract_links_async(self, response):
        def inner(_response):
            for link in self._link_extractor.extract(_response):
                self._queue.put(link)

        process = multiprocessing.Process(target=inner, args=(response,))
        process.start()

    def _process_response_async(self, response):
        process = multiprocessing.Process(target=self.process_response, args=(response,))
        process.start()

    def _process_url(self, url: str) -> None:
        with self.adapter:
            response = self.adapter(url)

            if response.status_code in self.success_codes:
                if self.validator and not self.validator(response):
                    return

                self._extract_links_async(response)
                self._process_response_async(response)
                self.logger.debug("currently have %s async tasks", len(multiprocessing.active_children()))
            elif response.status_code in self.failure_codes:
                self.on_failure_callback(response)
            else:
                # What to do here?
                pass

    def run(self):
        if not self.process_response:
            raise ValueError("No processing function specified")

        self.logger.info("starting queue extraction loop")
        while self.keep_alive:
            try:
                url = self.queue.get(timeout=self.keep_alive_timeout)
            except Empty:
                self.logger.warning(
                    "queue is empty (approximate size is %s): waited for %s",
                    self.queue.qsize(),
                    self.keep_alive_timeout
                )
                self.on_queue_timeout()
                self.logger.debug("queue timeout callback was called. continue execution")
            else:
                self.logger.info("fetched new url from queue: %s", unquote(url))
                try:
                    self._process_url(url)
                except Exception as exception:
                    # Implement possible Exceptions
                    raise exception
                else:
                    self.logger.info("page at %s was successfully processed", unquote(url))
