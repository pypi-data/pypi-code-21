"""
This module provides base classes for services to expose functionality via APIs.
"""

import flask
import typing
from argparse import Namespace

from relevance.settings import SettingsFactory


class Service(flask.Flask):
    """
    This class wraps the :class:`flask.Flask` application object and provides additional
    features to it, such as common error handling and response formatting.
    """
    instances = {}
    """ The service instances mapping. """

    def __init__(self, name: str, *args, **kwargs):
        """
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

        In some environments like multiprocessing, importing a global service object has
        not the intended effect. This method ensures that the instance that is retrieved
        is always the same across threads.

        If an instance `name` already exists, it will be returned. Otherwise, one will be
        created, stored and returned.

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
        :decorator: Decorator method for functions to call before starting the application.
            Useful for loading configuration files, per example.

        :param func: the function to decorate.
        :returns: the decorated function.
        """
        self.before_start_funcs.append(func)
        return func

    @property
    def request(self) -> flask.request:
        """
        Get the current request.

        :returns: the Flask request object.
        """
        return flask.request

    def result(self, status_code: int, content: object=None) -> flask.Response:
        """
        Obtain a response object.

        :param status_code: the status code to return.
        :param content: the content to return. If the content is a dictionary, a list
        or a tuple. It will be formatted to JSON. Otherwise, it will be returned as is.
        :returns: a response object.
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
