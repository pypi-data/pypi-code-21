"""
Relevance API package.

This package provides some common interfaces for the different REST APIs to use.
"""

import os
import pydoc
import typing
import logging
import anyconfig
from argparse import Namespace
from flask import Flask
from flask import request


def load_app_settings(app: Flask) -> dict:
    """
    Load or reload a configuration.

    :param app: the application object.
    :returns: the loaded settings dictionary.
    """
    app_name = app.name.split('.')[-1]
    env_name = os.environ.get('PYTHON_ENV', 'development')

    search_paths = [
        '/etc/relevance/{0}.json'.format(app_name),
        '/etc/relevance/{0}.{1}.json'.format(app_name, env_name),
        './etc/{0}.json'.format(app_name),
        './etc/{0}.{1}.json'.format(app_name, env_name),
    ]

    app.settings = anyconfig.load(search_paths, ignore_missing=True)

    return app.settings


def load_app_plugins(app: Flask):
    """
    Load or reload the application plugins.
    """
    for plugin in app.settings.get('plugins', []):
        func = pydoc.locate(plugin)
        if func is None:
            raise ImportError('cannot load plugin {0}'.format(plugin))
        func(app)


def init_app_logger(app: Flask):
    """
    Enable the API logger.

    :param app: the application object.
    """
    logger = logging.getLogger(app.name)

    @app.before_request
    def logger_before():
        logger.info('received {0} "{1}" with {2} bytes of {3}'.format(
            request.method, request.full_path, len(request.data),
            request.headers.get('Content-Type', 'unknown'),
        ))
        logger.debug('received {0} "{1}": {2}'.format(
            request.method, request.url, request.data,
        ))

    @app.after_request
    def logger_after(response):
        if response.status_code >= 500:
            log_func = logger.error
        elif response.status_code >= 400:
            log_func = logger.warn
        else:
            log_func = logger.info

        log_func('response {0} "{1}" {2} with {3} bytes of {4}'.format(
            request.method, request.full_path, response.status_code, len(response.data),
            response.headers.get('Content-Type', 'unknown'),
        ))
        logger.debug('response {0} "{1}" {2}: {3}'.format(
            request.method, request.url, response.status_code, response.data,
        ))
        return response


def register_app(name: str, loader: typing.Callable, app_data: dict) -> Flask:
    """
    Register an application.

    :param name: the name of the application.
    :param loader: a loader function for the application.
    :param app_data: data to store in the application object.
    :returns: an application object.
    """
    app_name = '{0}.{1}'.format(register_app.__module__, name)
    app = Flask(app_name)
    app.settings = {}
    app.data = Namespace(**app_data)
    app.reload = loader
    return app


def start_app(app: Flask):
    """
    Start an API application.

    :param app: the application object.
    :returns: the application object.
    """
    init_app_logger(app)
    load_app_settings(app)
    load_app_plugins(app)
    app.reload()
    return app
