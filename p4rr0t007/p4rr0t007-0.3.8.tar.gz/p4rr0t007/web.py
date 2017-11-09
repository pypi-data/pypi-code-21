# -*- coding: utf-8 -*-

import os
import sys
import json
import logging
import traceback

import htmlmin
from collections import OrderedDict
from flask import Flask
from flask import Response
from flask import render_template
from flask import request
from flask import url_for
from flask import session as flask_session
from flask_session import Session
from flask_reggie import Reggie
from flask_compress import Compress
from plant import Node
from jinja2.exceptions import TemplateError

from p4rr0t007 import settings
from p4rr0t007.lib.core import get_logger
from p4rr0t007.lib.local import get_etc_hosts
from p4rr0t007.lib.local import hostname_seems_ipv4_address


logger = get_logger('p4rr0t007')


class MissingSecretKey(Exception):
    def __init__(self, key):
        super(MissingSecretKey, self).__init__('Application.update_secret_key() received {}'.format(repr(key)))


def full_url_for(*args, **kw):
    return "/".join([
        settings.BASE_URL.rstrip('/'),
        url_for(*args, **kw).lstrip('/'),
    ])


ETC_HOSTS = get_etc_hosts()


class Application(Flask):
    """High-level server class that extends :py:class:`flask.Flask` adding
    methods to handle ``application/json`` requests and responses.
    """
    FLASK_EXTENSIONS = [Session, Reggie, Compress]

    def __init__(self, app_node=None, static_folder=None, template_folder=None, settings_module='p4rr0t007.settings', error_template_name='500.html', logger_name=None, logger=None, secret_key=None, **kw):
        if app_node is None:
            app_node = Node(os.getcwd())

        template_folder = os.path.expanduser(template_folder or app_node.dir.join('templates'))
        static_folder = os.path.expanduser(static_folder or app_node.dir.join('static/dist'))
        super(Application, self).__init__(
            __name__,
            static_folder=static_folder,
            template_folder=template_folder,
            **kw
        )
        # self.static_folder = static_folder
        # self.template_folder = template_folder
        self.error_template_name = error_template_name
        self.config.from_object(settings_module)
        self.app_node = app_node
        self.secret_key = secret_key or self.config['SECRET_KEY']
        if isinstance(logger, logging.Logger):
            self.log = logger
        else:
            self.log = get_logger(logger_name or self.__class__.__module__)

        self.initialize_extensions()
        self.check_etc_hosts()

    def initialize_flask_extensions(self):
        for Extension in self.FLASK_EXTENSIONS:
            name = "ext_{}".format(Extension.__name__.lower())
            ext = Extension()
            ext.init_app(self)
            try:
                setattr(self, name, ext)
            except AttributeError as e:
                raise AttributeError('failed to set attribute "{}" with the extension {}: {}'.format(name, repr(ext), e))

    def initialize_extensions(self):
        self.initialize_flask_extensions()

    def update_secret_key(self, key):
        if not key:
            raise MissingSecretKey(key)

        self.secret_key = key
        self.ext_session = Session(self)
        self.ext_session.init_app(self)
        return key

    def check_etc_hosts(self):
        domain = self.config.get('DOMAIN')
        if self.config.get('LOCAL') and not hostname_seems_ipv4_address(domain):
            if domain not in ETC_HOSTS.keys():
                self.log.warning('your local server uses the domain %s but it is not present in /etc/hosts', domain)

    @property
    def session(self):
        """access the global session dictionary. For configuration info check out the `flask-session <https://pythonhosted.org/Flask-Session/>`_ documentation.
        """
        return flask_session

    def json_handle_weird(self, obj):
        self.log.warning("failed to serialize %s", obj)
        return bytes(obj)

    def json_response(self, data, code=200, indent=2, headers={}):
        """Useful for restful APIs
        :param data: a native python object, must be json serialiable, otherwise will be handled by :py:meth:`Application.json_handle_weird`
        :param code: the http status code
        :param indent: how many characters to indent when generating the json
        :param headers: a dict with optional headers
        :returns: a :py:class:`flask.Response` with the option of prettifying
        the json response
        """
        headers = headers.copy()
        headers['Content-Type'] = 'application/json'
        payload = json.dumps(data, indent=indent, default=self.json_handle_weird)
        return Response(payload, status=code, headers=headers)

    def template_response(self, name, context=None, content_type='text/html', code=200, minify=True):
        """
        :param name: the name of the template file, must exist inside of the configured ``template_folder`` parameter of the class constructor.
        :param context: a dictionary whose keys will be available within the target template file.
        :param content_type: a string with the content-type. Defaults to ``text/html`` but can be modified when serving a ``plain/text`` for example.
        :param code: the http status code
        :param minify: bool - whether to minify the final html.
        """
        context = OrderedDict(context or {})
        context['json'] = json
        context['full_url_for'] = full_url_for

        utf8 = render_template(name, **context)
        if minify:
            mini = htmlmin.minify(utf8, remove_comments=True, remove_empty_space=True, remove_all_empty_space=True, reduce_boolean_attributes=True, remove_optional_attribute_quotes=True)
        else:
            mini = utf8

        return Response(mini, headers={
            'Content-Type': content_type,
            'Content-Encoding': 'UTF-8',
        }, status=code)

    def text_response(self, contents, code=200, headers={}):
        """shortcut to return simple plain/text messages in the response.

        :param contents: a string with the response contents
        :param code: the http status code
        :param headers: a dict with optional headers
        :returns: a :py:class:`flask.Response` with the ``text/plain`` **Content-Type** header.
        """
        return Response(contents, status=code, headers={
            'Content-Type': 'text/plain'
        })

    def get_json_request(self):
        """
        friendly method to parse a proper json request (i.e.: **application/json** or **text/json**)
        :returns: a dict with the parsed data, unless the request data does not contain a valid json string or the content-type do not portray a json request.
        """
        content_type = request.headers.get('Content-Type', 'text/plain')
        if content_type not in ('application/json', 'text/json'):
            self.log.error('get_json_request() called in a request that does not have a json content-type: %s. Refusing to parse the request data', content_type)
            return {}

        if not request.data:
            return {}

        try:
            data = json.loads(request.data)
        except ValueError as e:
            self.log.warning(
                "Trying to parse json body in the %s to %s raised %s",
                request.method, request.url, e
            )
            data = {}

        return data

    def handle_exception(self, e):
        """called by flask when an exception happens. p4rr0t007 always returns
        a 500.html response that must exist under the given
        ``template_folder`` constructor param.
        """
        sys.stderr.write("p4rr0t007 handled an error:")
        sys.stderr.write(traceback.format_exc(e))
        sys.stderr.flush()

        self.log.exception('failed to handle {} {}'.format(request.method, request.url))
        try:
            return self.template_response(self.error_template_name, code=500)
        except TemplateError as e:
            sys.stderr.write('failed render the {}/{}'.format(self.template_folder, self.error_template_name))
            sys.stderr.write(traceback.format_exc(e))

        sys.stderr.flush()
        return self.text_response('5ERV3R 3RR0R')

    def route(self, pattern, append_slash=False, remove_slash=False, *args, **kw):
        if append_slash:
            pattern = '{}/'.format(pattern.rstrip('/'))
        if remove_slash:
            pattern = pattern.rstrip('/') or '/'
        return super(Application, self).route(pattern, *args, **kw)
