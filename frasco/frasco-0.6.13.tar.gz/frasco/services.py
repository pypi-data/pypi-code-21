from .actions import (ActionFunction, ActionList, current_context, ContextExitException,\
                     ensure_context)
from .decorators import WithActionsDecorator, register_hooks, expose
from .views import Blueprint, as_view, ActionsView, full_exec_request_actions
from .marshaller import marshaller_context, marshal
from .request_params import auto_inject_request_params
from .utils import logger, preprend_base_url_to_urls
from flask import json, request, current_app, jsonify, abort, make_response
from werkzeug.local import LocalProxy
from werkzeug.exceptions import HTTPException
from werkzeug.wrappers import Response
import inspect
import functools
import copy


class ServiceActionsView(ActionsView):
    def __init__(self, *args, **kwargs):
        self.marshaller = kwargs.pop('marshaller', None)
        super(ServiceActionsView, self).__init__(*args, **kwargs)

    """View class for service views created using the ServiceLoader
    """
    def dispatch_request(self, *args, **kwargs):
        try:
            rv = super(ServiceActionsView, self).dispatch_request(*args, **kwargs)
        except ServiceError as e:
            return make_response(json.dumps({"error": e.message}), e.http_code)
        if isinstance(rv, Response):
            return rv
        # child actions can use "return" to return a value which
        # can be something else than a proper Response instance.
        # In this case we encode the return value to json
        return marshal(rv, self.marshaller)

    def _auto_render_func(self):
        # the _auto_render_func() func is only called if the actions do not
        # exit the context, thus we return an empty json response
        return jsonify()


def get_current_app_service(name):
    return current_app.services[name]


_services_proxies = {}

def service_proxy(name):
    if name not in _services_proxies:
        _services_proxies[name] = LocalProxy(lambda: get_current_app_service(name))
    return _services_proxies[name]


def pass_service(*names):
    """Injects a service instance into the kwargs
    """
    def decorator(f):
        @functools.wraps(f)
        def wrapper(*args, **kwargs):
            for name in names:
                kwargs[name] = service_proxy(name)
            return f(*args, **kwargs)
        return wrapper
    return decorator


class ServiceError(Exception):
    def __init__(self, message, http_code=500):
        self.message = message
        self.http_code = http_code


class ServiceMeta(type):
    def __init__(cls, name, bases, attrs):
        type.__init__(cls, name, bases, attrs)
        cls.current = service_proxy(attrs.get('name') or name)


def json_service_marshaller(rv):
    return json.dumps(rv), {'Content-Type': current_app.config.get(
        'SERVICES_CONTENT_TYPE', 'application/json;charset=UTF-8')}


class Service(object):
    name = None
    view_class = ServiceActionsView
    blueprint_class = Blueprint
    url_prefix = None
    marshaller = staticmethod(json_service_marshaller)
    __metaclass__ = ServiceMeta

    def __init__(self):
        self.name = self.name or self.__class__.__name__
        self.actions = ActionList()
        self.views = []
        self.hooks = []
        for attr in dir(self):
            attr = getattr(self, attr)
            if isinstance(attr, ActionFunction):
                self.actions.append(attr.action)
            if hasattr(attr, 'urls'):
                self._expose(attr, attr.urls)
            if hasattr(attr, 'hooks'):
                self.hooks.append(attr)

    def _expose(self, func, urls):
        name = func.__name__
        if isinstance(func, ActionFunction):
            name = func.unbound_func.__name__
            func = func.unbound_func if isinstance(func.unbound_func, WithActionsDecorator) else func.func
        if self.url_prefix:
            preprend_base_url_to_urls(self.url_prefix, urls)
        self.views.append(as_view(name=name,
                                  url_rules=urls,
                                  view_class=self.view_class,
                                  marshaller=self.marshaller)(func))

    @property
    def exposed(self):
        return len(self.views) > 0 or len(self.hooks) > 0

    @property
    def blueprint_name(self):
        return "%s_service" % self.name

    def as_blueprint(self):
        bp = self.blueprint_class(self.blueprint_name, self.__class__.__module__)
        for view in self.views:
            bp.add_view(view)
        for attr in self.hooks:
            register_hooks(attr, attr.hooks, bp)
        return bp


def service_mixin(cls, decorator, url_prefix=None):
    attrs = {}
    for name in dir(cls):
        attr = getattr(cls, name)
        if hasattr(attr, 'urls'):
            urls = copy.deepcopy(attr.urls)
            if url_prefix:
                preprend_base_url_to_urls(url_prefix, urls)
            decorated = decorator(attr)
            decorated.urls = urls
            attrs[attr.__name__] = decorated
    return type(cls.__name__, (cls,), attrs)
