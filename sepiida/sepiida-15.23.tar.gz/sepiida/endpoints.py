import collections
import inspect
import json
import logging
import re
import time

import flask
import flask.views
import werkzeug.urls
from werkzeug.wrappers import Response as ResponseBase

import sepiida.errors
import sepiida.log
import sepiida.parsing
import sepiida.serialization
from sepiida import fields
from sepiida.errors import APIException, Error

LOGGER = logging.getLogger(__name__)

class APIEndpoint(flask.views.View):
    ENDPOINT            = None
    ENVELOPE            = fields.ObjectEnvelope
    ERRORS              = []
    PUBLIC_METHODS      = []
    SIGNATURE           = None
    CACHING             = {'GET': 'max-age=10'}

    def __init__(self):
        self.fields = []
        self.filters = {}
        self.limit = None
        self.offset = None
        self.order = []
        self.sorts = {}

    @classmethod
    def endpoint_with_id(cls):
        return cls.ENDPOINT + '<int:_id>/'

    @classmethod
    def endpoint_with_uuid(cls):
        return cls.ENDPOINT + '<uuid:uuid>/'

    @classmethod
    def signature_envelope(cls):
        return cls.ENVELOPE(cls.SIGNATURE)

    def _map_request_to_method(self, request, single_resource):
        if single_resource:
            if request.method == 'POST':
                raise AttributeError("POSTs not allowed on single resource URLs")
            return getattr(self, request.method.lower())
        else:
            if request.method == 'GET':
                return getattr(self, 'list')
            elif request.method == 'PUT':
                raise AttributeError("PUTs are not allowed on collection URLs")
            else:
                return getattr(self, request.method.lower())

    def _fixup_response(self, request, response):
        if isinstance(response, ResponseBase):
            return response, response.status_code, response.headers
        elif isinstance(response, tuple):
            return response
        elif response is None:
            headers = {
                'Content-Type': 'text/plain',
                'Cache-Control': self.CACHING.get(request.method)
            }
            return flask.make_response('', 204, headers), 204, headers
        elif request.method == 'POST':
            return response, 201, {}
        return response, 200, {}

    def _convert_exception(self, e):
        for handler_spec in self.get_error_handlers():
            try:
                raise handler_spec.translate(e)
            except TypeError:
                continue

    @staticmethod
    def _filter_fields(selected_fields, response):
        if not selected_fields:
            return response
        selectors = _fields_to_selectors(selected_fields.values)
        return _get_response_by_field_selectors(response, selectors)

    def _apply_envelope(self, response):
        return self.signature_envelope().package(response)

    def _package_response(self, request, method, response, selected_fields):
        response, status, headers = self._fixup_response(flask.request, response)
        if 'Cache-Control' not in headers:
            headers['Cache-Control'] = self.CACHING.get(request.method)
        if response is None or response == '':
            response, headers = sepiida.serialization.prepare_response(flask.request, response, headers, None)
            return flask.make_response('', 204, headers)

        if not isinstance(response, ResponseBase):
            if self.SIGNATURE:
                if method == getattr(self, 'list', None):
                    response = self._apply_envelope(response)
                else:
                    response = self.SIGNATURE.package(response)
                response = self._filter_fields(selected_fields, response)
            response, headers = sepiida.serialization.prepare_response(flask.request, response, headers, self.SIGNATURE)
            response = flask.make_response(response, status, headers)
        return response

    def get_error_handlers(self):
        handlers = [getattr(parent, 'ERRORS', []) for parent in self.__class__.__mro__]
        handlers = getattr(self, 'ERRORS', []) + [handler for parent_handlers in handlers for handler in parent_handlers]
        return [handler for handler in handlers if isinstance(handler, sepiida.errors.Specification)]

    @classmethod
    def authenticate(cls):
        return

    @staticmethod
    def get_arguments(request):
        if request.method == 'GET':
            body = request.data
            if not body:
                return request.args
            try:
                return werkzeug.urls.url_decode(body, charset='utf-8', errors='strict')
            except UnicodeDecodeError as e:
                raise sepiida.parsing.ParseErrors(errors=[sepiida.parsing.ParseError(error_code='bad-querystring-body', message=str(e))])
            return request.data.decode('utf-8') or request.args
        return request.args

    def parse_arguments(self, request):
        try:
            arguments = self.get_arguments(request)
            return sepiida.parsing.parse_arguments(arguments)
        except sepiida.parsing.ParseErrors as parse_errors:
            errors = [Error(error_code=e.error_code, title=str(e), status_code=400) for e in parse_errors.errors]
            raise APIException(errors=errors)

    def process_arguments(self, arguments, single_resource):
        if not self.SIGNATURE:
            return
        if single_resource:
            self.SIGNATURE.process_arguments(arguments)
        else:
            self.signature_envelope().process_arguments(arguments)
        self.fields = arguments.fields.values if arguments.fields else []
        self.filters = {}
        self.limit = arguments.limit
        self.order = arguments.order
        self.offset = arguments.offset
        self.sorts = {}
        self.sorts = arguments.sorts.values if arguments.sorts else []
        for _filter in arguments.filters:
            self.filters.setdefault(_filter.name, []).append(_filter)

    def dispatch_request(self, *args, **kwargs): # pylint: disable=arguments-differ
        start = time.time()
        arguments = self.parse_arguments(flask.request) if self.SIGNATURE else sepiida.parsing.RequestArguments([])
        single_resource = kwargs.pop('_single_resource')
        try:
            method = self._map_request_to_method(flask.request, single_resource)
        except AttributeError:
            return flask.make_response('', 404)


        self.process_arguments(arguments, single_resource)
        message =  "{} {} with filters {}".format(flask.request.method, flask.request.path, self.filters)
        with sepiida.log.warning_timer(10, message, start=start):
            try:
                if self.SIGNATURE and flask.request.method in ('PUT', 'POST'):
                    decoded = sepiida.serialization.loads(flask.request)
                    try:
                        payload = self.SIGNATURE.unpackage(None, decoded, flask.request.method)
                        if not payload and flask.request.method == 'PUT':
                            msg = "You supplied an empty payload for your PUT request. This will do nothing"
                            raise sepiida.errors.EmptyPayload(title=msg)
                    except fields.UnpackageError as e:
                        raise sepiida.errors.APIException(errors=e.errors)
                    kwargs['payload'] = payload

                my_exceptions = tuple([handler.exception_class for handler in self.get_error_handlers()])
                try:
                    inspect.getcallargs(method, *args, **kwargs) # pylint: disable=deprecated-method
                except TypeError:
                    title = ("You attempted to request a {method} on {path}. "
                        "You must call {method} on a specific resource rather "
                        "than the collection. You can do this by requesting a URL "
                        "of the pattern {path}<uuid>/").format(method=flask.request.method, path=flask.request.path)
                    raise Error('invalid-method', title, status_code=405)

                try:
                    response = method(*args, **kwargs)
                except my_exceptions as e: # pylint: disable=catching-non-exception
                    response = self._convert_exception(e)

                response = self._package_response(flask.request, method, response, arguments.fields)

                return response
            except Error as e:
                raise APIException(errors=[e])

    def options(self, _id=None, uuid=None): # pylint: disable=unused-argument
        if self.SIGNATURE is None:
            return '', 204, {}
        description = {
            'signature': self.SIGNATURE.get_options_description(),
        }
        return flask.make_response(json.dumps(description), 200, {})


NAME_EXTRACTOR = re.compile(r"<class '(?P<name>.+)'>")
def _extract_name(resource):
    # I can't for the life of me figure out how to get the classes'
    # definition heirarchy programmatically. So we'll cheat. Badly.
    # forgive me.
    base = repr(resource)
    match = NAME_EXTRACTOR.match(base)
    if not match:
        raise Exception("Our name extractor doesn't work right and couldn't match '{}'".format(base))
    return match.group('name')

def _fields_to_selectors(_fields):
    field_parts = [f.partition('.') for f in _fields]
    roots = [root for root, _, child in field_parts if not child]
    branches = [(root, child) for root, _, child in field_parts if child]
    result = {root: True for root in roots}
    selectors = collections.defaultdict(list)
    for root, child in branches:
        selectors[root].append(child)
    for k, subfields in selectors.items():
        result[k] = _fields_to_selectors(subfields)
    return result

def _get_response_by_field_selectors(response, selectors):
    if isinstance(response, dict):
        result = {}
        for k, v in selectors.items():
            if v is True:
                result[k] = response[k]
            else:
                result[k] = _get_response_by_field_selectors(response[k], v)
        return result
    return [_get_response_by_field_selectors(r, selectors) for r in response]


def has_collection_methods(resource):
    return any([hasattr(resource, method) for method in ('delete', 'list', 'post')])

def has_single_methods(resource):
    return any([hasattr(resource, method) for method in ('get', 'put', 'patch', 'delete')])

def get_collection_methods(resource):
    methods = ['HEAD', 'OPTIONS']
    if hasattr(resource, 'post'):
        methods.append('POST')
    if hasattr(resource, 'list'):
        methods.append('GET')
    if hasattr(resource, 'delete'):
        methods.append('DELETE')
    return methods

def get_single_methods(resource):
    methods = ['HEAD', 'OPTIONS']
    for method in ('PUT', 'GET', 'PATCH', 'DELETE'):
        if hasattr(resource, method.lower()):
            methods.append(method)
    return methods

def _check_error_handlers(resource):
    for errorhandler in resource.ERRORS:
        if isinstance(errorhandler, tuple):
            LOGGER.warning((
                "The error handler %s for %s is a tuple. It should be converted to a sepiida.error.Specification. "
                " Until then, it will be ignored"), errorhandler, resource
            )

def add_resource(app, resource, endpoint=None):
    setattr(app, 'endpoints', getattr(app, 'endpoints', {}))

    # This check is to help people transitioning from sepiida pre-7. Remove in sepiida 8
    _check_error_handlers(resource)

    name = _extract_name(resource) if endpoint is None else endpoint
    if resource.ENDPOINT is None:
        raise Exception("You must specify an ENDPOINT for {}".format(resource))
    for public_method in resource.PUBLIC_METHODS:
        if public_method not in ['delete', 'get', 'list', 'post', 'put']:
            raise Exception(
                "Method {} is not supported as PUBLIC_METHOD. "
                "Supported methods are ['delete', 'get', 'list', 'post', 'put']."
                .format(public_method))
        sepiida.session.public_endpoint(app, name + '.' + public_method)

    view_func = resource.as_view(name)
    app.endpoints[name] = resource
    if has_collection_methods(resource):
        collection_methods = get_collection_methods(resource)
        app.add_url_rule(resource.ENDPOINT,
            name,
            view_func,
            methods=collection_methods,
            defaults={'_single_resource': False})

    if has_single_methods(resource):
        single_methods = get_single_methods(resource)
        app.add_url_rule(resource.endpoint_with_uuid(),
            name,
            view_func,
            methods=single_methods,
            defaults={'_single_resource': True})
        app.add_url_rule(resource.endpoint_with_id(),
            name,
            view_func,
            methods=single_methods,
            defaults={'_single_resource': True})
