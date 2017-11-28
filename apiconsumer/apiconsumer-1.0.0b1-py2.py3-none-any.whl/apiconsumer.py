import logging
import requests

logger = logging.getLogger(__name__)


class BadApiCall(Exception):
    def __init__(self, *args, **kwargs):
        super(BadApiCall, self).__init__(*args, **kwargs)


class ApiConsumer(object):
    allowed_methods = ['head', 'get', 'post', 'put', 'patch', 'delete', 'options']

    def __init__(self, url, extra_headers, user_agent='ApiConsumer'):
        logger.debug("Setting up an api consumer for %s" % url)
        self.session = requests.Session()
        self.url = url

        if extra_headers:
            self.session.headers.update(extra_headers)

        # Override User-Agent
        if user_agent:
            self.session.headers.update({'User-Agent': user_agent})

    def __getattr__(self, attr):
        if attr.startswith('__'):
            raise AttributeError(attr)

        method, _, endpoint_underscored = attr.partition('_')

        if method not in self.allowed_methods:
            raise AttributeError(attr)

        def wrapper(**kwargs):
            response = self.session.request(method, self.url + "/" + endpoint_underscored.replace('_', '/'), **kwargs)

            if response.status_code >= 300:
                logger.error("Bad response json %s" % response.json())
                raise BadApiCall(response.status_code)

            return response.json()

        return wrapper
