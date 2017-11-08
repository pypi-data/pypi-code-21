# -*- coding: utf-8 -*-

from pysnow import Client, Request


class PysnowClient(Client):
    def __init__(self, *args, logger=None, **kwargs):
        """Overrides pysnow _request() to inject request logging
        :param args: Args passed along to Request
        :param logger: Logger (if enabled)
        :param kwargs: Kwargs passed along to Request
        """
        self.logger = logger
        super(PysnowClient, self).__init__(*args, **kwargs)

    def _request(self, method, table, **kwargs):
        """Creates and returns a new `Request` object, takes some basic settings from the `PysnowClient` and
        passes along to the `Request` constructor
        :param method: HTTP method
        :param table: Table to operate on
        :param kwargs: Keyword arguments passed along to `Request`
        :return: `Request` object
        """

        query = kwargs.get('query', None)
        payload = kwargs.get('payload', None)

        if self.logger:
            self.logger.debug("table: %s, method: %s, query: %s, payload: %s" % (
                table,
                method,
                query,
                payload
            ))

        return Request(method,
                       table,
                       request_params=self.request_params,
                       raise_on_empty=self.raise_on_empty,
                       session=self.session,
                       instance=self.instance,
                       base_url=self.base_url,
                       **kwargs)

