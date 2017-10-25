# -*- coding: utf-8 -*-
"""
Datary sdk Requests File
"""
from requests import RequestException
import requests
import structlog


logger = structlog.getLogger(__name__)


class DataryRequests(object):
    """
    Datary Requests module class
    """

    URL_BASE = "http://api.datary.io/"
    headers = {}

    def __init__(self, **kwargs):
        """
        DataryRequests Init method
        """
        super(DataryRequests, self).__init__()
        self.headers = {"Content-Type": "application/x-www-form-urlencoded"}
        self.headers.update(kwargs.get('headers', {}))

    def request(self, url, http_method, **kwargs):
        """
        Sends request to Datary passing config through arguments.

        ===========   =============   =======================================
        Parameter     Type            Description
        ===========   =============   =======================================
        url           str             destination url
        http_method   str             http method request [GET, POST, DELETE]
        ===========   =============   =======================================

        Returns:
            content(): if HTTP response between the 200 range

        Raises:
            - Unknown HTTP method
            - Fail request to datary

        """
        try:
            #  HTTP GET Method
            if http_method == 'GET':
                content = requests.get(url, **kwargs)

            # HTTP POST Method
            elif http_method == 'POST':
                content = requests.post(url, **kwargs)

            # HTTP DELETE Method
            elif http_method == 'DELETE':
                content = requests.delete(url, **kwargs)

            # Unkwown HTTP Method
            else:
                logger.error(
                    'Do not know {} as HTTP method'.format(http_method))
                raise Exception(
                    'Do not know {} as HTTP method'.format(http_method))

            # Check for correct request status code.
            if 199 < content.status_code < 300:
                return content
            else:
                logger.error(
                    "Fail Request to datary done with code {}".format(content.status_code),
                    url=url, http_method=http_method,
                    code=content.status_code,
                    # text=content.text,
                    # kwargs=kwargs,
                )

        # Request Exception
        except RequestException as ex:
            logger.error(
                "Fail request to Datary - {}".format(ex),
                url=url,
                http_method=http_method,
                # requests_args=kwargs,
            )
