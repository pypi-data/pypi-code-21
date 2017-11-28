import logging
import requests
from requests.exceptions import RequestException
from .exceptions import ApiConsumerRequestException, ApiConsumerResponseError

logger = logging.getLogger(__name__)
HEAD, GET, POST, PUT, PATCH, DELETE, OPTIONS = 'head', 'get', 'post', 'put', 'patch', 'delete', 'options'


class ApiConsumer(object):
    allowed_methods = [HEAD, GET, POST, PUT, PATCH, DELETE, OPTIONS]

    def __init__(self, url, extra_headers, user_agent='ApiConsumer'):
        logger.debug("Setting up an api consumer for %s" % url)
        self.session = requests.Session()
        self.url = url

        if extra_headers:
            self.session.headers.update(extra_headers)

        # Override User-Agent
        if user_agent:
            self.session.headers.update({'User-Agent': user_agent})

    def __getitem__(self, item):
        return self.__getattr__(item)

    def __getattr__(self, attr):
        if attr.startswith('__'):
            raise AttributeError(attr)

        attr_partition_tuple = attr.partition('_')
        method, _, endpoint_underscored = attr_partition_tuple

        if method not in self.allowed_methods:
            raise AttributeError(attr)

        def wrapper(*args, **kwargs):
            endpoint_string = endpoint_underscored

            if not endpoint_string and len(args):
                endpoint_string = args[0]
            endpoint = endpoint_string.replace('_', '/')

            try:
                response = self.session.request(
                    method=method,
                    url='{url}/{endpoint}'.format(url=self.url, endpoint=endpoint),
                    **kwargs
                )
            except RequestException as e:
                raise ApiConsumerRequestException(e)

            if response.status_code >= 300:
                raise ApiConsumerResponseError(response)

            return response.json()

        return wrapper
