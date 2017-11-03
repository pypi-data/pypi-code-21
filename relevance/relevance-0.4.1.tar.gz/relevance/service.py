"""
Relevance services package.
"""

import flask
import typing
from argparse import Namespace

from relevance.settings import SettingsFactory


class Service(flask.Flask):
    """
    Service interface.
    """
    # The service instances list
    instances = {}

    def __init__(self, name: str, *args, **kwargs):
        """
        Initialize the service.

        :param name: the name of the service.
        """
        self.svc_name = name
        self.data = Namespace()
        imp_name = 'relevance.{0}.service'.format(name)
        super().__init__(imp_name, *args, **kwargs)

        self.before_start_funcs = []
        self.before_start_done = False

        # Initialize settings
        loader = SettingsFactory(['/etc/relevance', './etc'])
        self.settings = loader.load(self.svc_name)

        # Initialize error handlers
        @self.errorhandler(ResourceNotFoundError)
        def error_resource_not_found(e):
            return self.result(404, {
                'error': {
                    'type': e.__class__.__name__,
                    'desc': 'the requested resource does not exist',
                    'resource_type': e.resource_type,
                    'resource': str(e),
                }
            })

        @self.errorhandler(404)
        def error_404(_):
            e = ResourceNotFoundError('path', self.request.path)
            return error_resource_not_found(e)

        @self.errorhandler(405)
        def error_405(_):
            return self.result(405, {
                'error': {
                    'type': 'MethodNotAllowedError',
                    'desc': 'the requested method is not allowed for the requested resource',
                    'resource': self.request.path,
                    'key': self.request.method,
                }
            })

    @classmethod
    def instance(cls, name: str, *args, **kwargs) -> 'Service':
        """
        Create or get an instance of a service.

        :param name: the instance name.
        :returns: a service object.
        """
        if name in cls.instances:
            return cls.instances[name]
        instance = cls(name, *args, **kwargs)
        cls.instances[name] = instance
        return instance

    def before_start(self, func: typing.Callable) -> typing.Callable:
        """
        Decorator method for stuff to launch before starting the application.

        :param func: the function to decorate.
        :returns: the decorated function.
        """
        self.before_start_funcs.append(func)
        return func

    @property
    def request(self) -> flask.request:
        """
        Get the current request.
        """
        return flask.request

    def result(self, status_code: int, content: object=None) -> flask.Response:
        """
        Result a service response.

        :param status_code: the status code to return.
        :param content: the content to return.
        """
        if content is None:
            response = flask.Response()
        elif isinstance(content, (dict, list, tuple)):
            response = flask.jsonify(content)
        else:
            response = flask.Response()
            response.content = content
        response.status_code = status_code
        return response

    def wsgi_app(self, *args, **kwargs):
        """
        Override the WSGI handler with extra functionality.
        """
        if not self.before_start_done:
            for x in self.before_start_funcs:
                x()
            self.before_start_done = True
        return super().wsgi_app(*args, **kwargs)


class ResourceNotFoundError(NameError):
    """
    Exception raised when a resource is not found.
    """
    def __init__(self, resource_type: str, key: str):
        """
        Initialize the exception.

        :param resource_type: the resource type.
        :param key: the offending key.
        """
        super().__init__(key)
        self.resource_type = resource_type
