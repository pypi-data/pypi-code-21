# coding: utf-8
from __future__ import absolute_import, print_function, unicode_literals, division

import six
import webob
import logging

from oslo_serialization import jsonutils
from oslo_service import wsgi

from bservices import exception

_ = (lambda v: v)
LOG = logging.getLogger(__name__)

Router = wsgi.Router

_SUPPORTED_REQUEST_CONTENT_TYPES = [
    'text/plain',
    'application/json',
    'application/xml',
]

_SUPPORTED_RESPONSE_CONTENT_TYPES = [
    'text/plain',
    'application/json',
    'application/xml',
]

_MEDIA_TYPE_MAP = {
    'text/plain': 'text',
    'application/xml': 'xml',
    'application/json': 'json',
}

# These are typically automatically created by routes as either defaults
# collection or member methods.
_ROUTES_METHODS = [
    'create',
    'delete',
    'show',
    'update',
]

_METHODS_WITH_BODY = [
    'POST',
    'PUT',
]

# name of attribute to keep version method information
VER_METHOD_ATTR = 'versioned_methods'


def utf8(value):
    """Try to turn a string into utf-8 if possible."""
    if isinstance(value, six.text_type):
        return value.encode('utf-8')
    assert isinstance(value, str)
    return value


def get_supported_request_content_types():
    return _SUPPORTED_REQUEST_CONTENT_TYPES


def add_request_content_types(types):
    """Deprecated! Please use register_content_type or register_content_types."""
    _SUPPORTED_REQUEST_CONTENT_TYPES.append(types)


def get_supported_response_content_types():
    return _SUPPORTED_RESPONSE_CONTENT_TYPES


def add_response_content_types(types):
    """Deprecated! Please use register_content_type or register_content_types."""
    _SUPPORTED_RESPONSE_CONTENT_TYPES.append(types)


def get_media_map():
    return dict(_MEDIA_TYPE_MAP.items())


def add_media_map(maps):
    """Deprecated! Please use register_content_type or register_content_types."""
    _MEDIA_TYPE_MAP.update(maps)


def register_content_type(name, _type, resp=True):
    """Register the content type into the supported request, and the pair of
    type and name into the media map.

    Register the content type into the supported response if resp is True.

    For example,
    >>> register_content_type("html", "text/html")
    """
    if _type not in _SUPPORTED_REQUEST_CONTENT_TYPES:
        _SUPPORTED_REQUEST_CONTENT_TYPES.append(_type)

    if _type not in _MEDIA_TYPE_MAP:
        _MEDIA_TYPE_MAP[_type] = name

    if resp and _type not in _SUPPORTED_RESPONSE_CONTENT_TYPES:
        _SUPPORTED_RESPONSE_CONTENT_TYPES.append(_type)


def register_content_types(types, resp=True):
    """Register the content type into the supported request, and the pair of
    type and name into the media map.

    Register the content type into the supported response if resp is True.

    Notice: the argument types must be a list or tuple, and the items of types
    are a list or tuple which has two elements of name and type, or a dict which
    has two keys of "name" and "type".

    For example,
    >>> register_content_types([("html", "text/html"), {"name": "xml", "type": "application/xml"}])
    """
    for ct in types:
        if isinstance(ct, (list, tuple)):
            name, _type = ct[0], ct[1]
        elif isinstance(_type, dict):
            name, _type = ct["name"], ct["type"]
        else:
            raise ValueError
        register_content_type(name, _type, resp=resp)


class Request(wsgi.Request):
    """Add some specific logic to the base webob.Request."""

    def __init__(self, *args, **kwargs):
        super(Request, self).__init__(*args, **kwargs)
        self._extension_data = {'db_items': {}}

    def cache_db_items(self, key, items, item_key='id'):
        """Allow API methods to store objects from a DB query to be
        used by API extensions within the same API request.

        An instance of this class only lives for the lifetime of a
        single API request, so there's no need to implement full
        cache management.
        """
        db_items = self._extension_data['db_items'].setdefault(key, {})
        for item in items:
            db_items[item[item_key]] = item

    def get_db_items(self, key):
        """Allow an API extension to get previously stored objects within
        the same API request.

        Note that the object data will be slightly stale.
        """
        return self._extension_data['db_items'][key]

    def get_db_item(self, key, item_key):
        """Allow an API extension to get a previously stored object
        within the same API request.

        Note that the object data will be slightly stale.
        """
        return self.get_db_items(key).get(item_key)

    @property
    def accept_content_type(self):
        accept = self.environ.get("wsgi.best_content_type", None)
        return accept or self.best_match_content_type()

    @accept_content_type.setter
    def accept_content_type(self, accept):
        self.environ['wsgi.best_content_type'] = accept

    def best_match_content_type(self):
        """Determine the requested response content-type."""
        if 'wsgi.best_content_type' not in self.environ:
            # Calculate the best MIME type
            content_type = None

            # Check URL path suffix
            parts = self.path.rsplit('.', 1)
            if len(parts) > 1:
                possible_type = 'application/' + parts[1]
                if possible_type in get_supported_response_content_types():
                    content_type = possible_type

            if not content_type:
                content_type = self.accept.best_match(get_supported_response_content_types())

            self.environ['wsgi.best_content_type'] = (content_type or 'application/json')

        return self.environ['wsgi.best_content_type']

    def get_content_type(self):
        """Determine content type of the request body.

        Does not do any body introspection, only checks header

        """
        if "Content-Type" not in self.headers:
            return None

        content_type = self.content_type

        # NOTE(markmc): text/plain is the default for eventlet and
        # other webservers which use mimetools.Message.gettype()
        # whereas twisted defaults to ''.
        # if not content_type or content_type == 'text/plain':
        if not content_type:
            return None

        if content_type not in get_supported_request_content_types():
            raise exception.InvalidContentType(content_type=content_type)

        return content_type

    def best_match_language(self):
        """Determine the best available language for the request.

        :returns: the best language match or None if the 'Accept-Language'
                  header was not available in the request.
        """
        if not self.accept_language:
            return None
        return self.accept_language.best_match("en_US")


class ActionDispatcher(object):
    """Maps method name to local methods through action name."""

    def dispatch(self, *args, **kwargs):
        """Find and call local method."""
        action = kwargs.pop('action', 'default')
        action_method = getattr(self, str(action), self.default)
        return action_method(*args, **kwargs)

    def default(self, data):
        raise NotImplementedError()


class TextDeserializer(ActionDispatcher):
    """Default request body deserialization."""

    def deserialize(self, datastring, action='default'):
        return self.dispatch(datastring, action=action)

    def default(self, datastring):
        return {"body": datastring}


class JSONDeserializer(TextDeserializer):

    def _from_json(self, datastring):
        try:
            return jsonutils.loads(datastring)
        except ValueError:
            msg = _("cannot understand JSON")
            raise exception.MalformedRequestBody(reason=msg)

    def default(self, datastring):
        return {'body': self._from_json(datastring)}


class TextSerializer(ActionDispatcher):
    def serialize(self, data, action="default"):
        return self.dispatch(data, action=action)

    def default(self, data):
        return str(data)


class DictSerializer(ActionDispatcher):
    """Default request body serialization."""

    def serialize(self, data, action='default'):
        return self.dispatch(data, action=action)

    def default(self, data):
        return jsonutils.dumps(data)


class JSONDictSerializer(DictSerializer):
    """Default JSON request body serialization."""
    pass


def serializers(**serializers):
    """Attaches serializers to a method.

    This decorator associates a dictionary of serializers with a
    method.  Note that the function attributes are directly
    manipulated; the method is not wrapped.
    """
    def decorator(func):
        if not hasattr(func, 'wsgi_serializers'):
            func.wsgi_serializers = {}
        func.wsgi_serializers.update(serializers)
        return func
    return decorator


def deserializers(**deserializers):
    """Attaches deserializers to a method.

    This decorator associates a dictionary of deserializers with a
    method.  Note that the function attributes are directly
    manipulated; the method is not wrapped.
    """
    def decorator(func):
        if not hasattr(func, 'wsgi_deserializers'):
            func.wsgi_deserializers = {}
        func.wsgi_deserializers.update(deserializers)
        return func
    return decorator


def response(code):
    """Attaches response code to a method.

    This decorator associates a response code with a method.  Note
    that the function attributes are directly manipulated; the method
    is not wrapped.
    """
    def decorator(func):
        func.wsgi_code = code
        return func
    return decorator


class ResponseObject(object):
    """Bundles a response object with appropriate serializers.

    Object that app methods may return in order to bind alternate
    serializers with a response object to be serialized.  Its use is
    optional.
    """

    def __init__(self, obj, code=None, headers=None, content_type=None,
                 **serializers):
        """Binds serializers with an object.

        Takes keyword arguments akin to the @serializer() decorator
        for specifying serializers.  Serializers specified will be
        given preference over default serializers or method-specific
        serializers on return.
        """
        self.obj = obj
        self.serializers = serializers
        self._default_code = 200
        self._code = code
        self._headers = headers or {}
        self.serializer = None
        self.media_type = None
        self.content_type = content_type

    def __getitem__(self, key):
        """Retrieves a header with the given name."""
        return self._headers[key.lower()]

    def __setitem__(self, key, value):
        """Sets a header with the given name to the given value."""
        self._headers[key.lower()] = value

    def __delitem__(self, key):
        """Deletes the header with the given name."""
        del self._headers[key.lower()]

    def _bind_method_serializers(self, meth_serializers):
        """Binds method serializers with the response object.

        Binds the method serializers with the response object.
        Serializers specified to the constructor will take precedence
        over serializers specified to this method.

        :param meth_serializers: A dictionary with keys mapping to
                                 response types and values containing
                                 serializer objects.
        """
        # We can't use update because that would be the wrong
        # precedence
        for mtype, serializer in meth_serializers.items():
            self.serializers.setdefault(mtype, serializer)

    def get_serializer(self, content_type, default_serializers=None):
        """Returns the serializer for the wrapped object.

        Returns the serializer for the wrapped object subject to the
        indicated content type.  If no serializer matching the content
        type is attached, an appropriate serializer drawn from the
        default serializers will be used.  If no appropriate
        serializer is available, raises InvalidContentType.
        """
        default_serializers = default_serializers or {}
        content_type = self.content_type or content_type

        try:
            mtype = get_media_map().get(content_type, content_type)
            if mtype in self.serializers:
                return mtype, self.serializers[mtype]
            else:
                return mtype, default_serializers[mtype]
        except (KeyError, TypeError):
            raise exception.InvalidContentType(content_type=content_type)

    def preserialize(self, content_type, default_serializers=None):
        """Prepares the serializer that will be used to serialize.

        Determines the serializer that will be used and prepares an
        instance of it for later call.  This allows the serializer to
        be accessed by extensions for, e.g., template extension.
        """
        mtype, serializer = self.get_serializer(content_type,
                                                default_serializers)
        self.media_type = mtype
        self.serializer = serializer()

    def serialize(self, request, content_type, default_serializers=None):
        """Serializes the wrapped object.

        Utility method for serializing the wrapped object.  Returns a
        webob.Response object.
        """
        content_type = self.content_type or content_type
        if self.serializer:
            serializer = self.serializer
        else:
            _mtype, _serializer = self.get_serializer(content_type,
                                                      default_serializers)
            serializer = _serializer()

        response = webob.Response()
        response.status_int = self.code
        for hdr, value in self._headers.items():
            response.headers[hdr] = utf8(str(value))
        response.headers['Content-Type'] = utf8(content_type)
        if self.obj is not None:
            response.body = serializer.serialize(self.obj)

        return response

    @property
    def code(self):
        """Retrieve the response status."""
        return self._code or self._default_code

    @property
    def headers(self):
        """Retrieve the headers."""
        return self._headers.copy()


def action_peek_json(body):
    """Determine action to invoke."""
    try:
        decoded = jsonutils.loads(body)
    except ValueError:
        msg = _("cannot understand JSON")
        raise exception.MalformedRequestBody(reason=msg)

    # Make sure there's exactly one key...
    if len(decoded) != 1:
        msg = _("too many body keys")
        raise exception.MalformedRequestBody(reason=msg)

    # Return the action and the decoded body...
    return decoded.keys()[0]


class ResourceExceptionHandler(object):
    """Context manager to handle Resource exceptions.

    Used when processing exceptions generated by API implementation
    methods (or their extensions).  Converts most exceptions to Fault
    exceptions, with the appropriate logging.
    """

    def __enter__(self):
        return None

    def __exit__(self, ex_type, ex_value, ex_traceback):
        if not ex_value:
            return True

        if isinstance(ex_value, exception.Forbidden):
            raise webob.exc.HTTPForbidden(explanation=ex_value.format_message())
        elif isinstance(ex_value, exception.VersionNotFoundForAPIMethod):
            raise
        elif isinstance(ex_value, exception.Invalid):
            raise exception.ConvertedException(code=ex_value.code,
                                               explanation=ex_value.format_message())
        elif isinstance(ex_value, TypeError):
            exc_info = (ex_type, ex_value, ex_traceback)
            LOG.error(_('Exception handling resource: %s'), ex_value,
                      exc_info=exc_info)
            raise webob.exc.HTTPBadRequest()
        elif isinstance(ex_value, webob.exc.HTTPException):
            LOG.info(_("HTTP exception thrown: %s"), ex_value)
            raise ex_value

        code = getattr(ex_value, "code", None)
        if code:
            raise exception.ConvertedException(code=code,
                                               explanation=ex_value.format_message())

        # We didn't handle the exception
        return False


class Resource(object):
    """WSGI app that handles (de)serialization and controller dispatch.

    WSGI app that reads routing information supplied by RoutesMiddleware
    and calls the requested action method upon its controller.  All
    controller action methods must accept a 'req' argument, which is the
    incoming wsgi.Request. If the operation is a PUT or POST, the controller
    method must also accept a 'body' argument (the deserialized request body).
    They may raise a webob.exc exception or return a dict, which will be
    serialized by requested content type.
    """

    support_api_request_version = False

    def __init__(self, controller, action_peek=None, inherits=None,
                 methods_with_body=None, **deserializers):
        """:param controller: object that implement methods created by routes lib
           :param action_peek: dictionary of routines for peeking into an
                               action request body to determine the
                               desired action
           :param inherits: another resource object that this resource should
                            inherit extensions from. Any action extensions that
                            are applied to the parent resource will also apply
                            to this resource.
        """
        self.controller = controller

        default_deserializers = dict(json=JSONDeserializer, text=TextDeserializer)
        default_deserializers.update(deserializers)

        self.default_deserializers = default_deserializers
        self.default_serializers = dict(json=JSONDictSerializer, text=TextSerializer)

        self.action_peek = dict(json=action_peek_json)
        self.action_peek.update(action_peek or {})

        # Copy over the actions dictionary
        self.wsgi_actions = {}
        if controller:
            self.register_actions(controller)

        # Save a mapping of extensions
        self.wsgi_extensions = {}
        self.wsgi_action_extensions = {}
        self.inherits = inherits
        self.methods_with_body = methods_with_body or _METHODS_WITH_BODY

    @classmethod
    def factory(cls, global_config, **local_config):
        """Used for paste app factories in paste.deploy config files.
        Any local configuration (that is, values under the [app:APPNAME]
        section of the paste config) will be passed into the `__init__` method
        as kwargs.
        A hypothetical configuration would look like:
            [app:wadl]
            latest_version = 1.3
            paste.app_factory = nova.api.fancy_api:Wadl.factory
        which would result in a call to the `Wadl` class as
            import nova.api.fancy_api
            fancy_api.Wadl(latest_version='1.3')
        You could of course re-implement the `factory` method in subclasses,
        but using the kwarg passing it shouldn't be necessary.
        """
        return cls(**local_config)

    def register_actions(self, controller):
        """Registers controller actions with this resource."""
        actions = getattr(controller, 'wsgi_actions', {})
        for key, method_name in actions.items():
            self.wsgi_actions[key] = getattr(controller, method_name)

    def register_extensions(self, controller):
        """Registers controller extensions with this resource."""
        extensions = getattr(controller, 'wsgi_extensions', [])
        for method_name, action_name in extensions:
            # Look up the extending method
            extension = getattr(controller, method_name)

            if action_name:
                # Extending an action...
                if action_name not in self.wsgi_action_extensions:
                    self.wsgi_action_extensions[action_name] = []
                self.wsgi_action_extensions[action_name].append(extension)
            else:
                # Extending a regular method
                if method_name not in self.wsgi_extensions:
                    self.wsgi_extensions[method_name] = []
                self.wsgi_extensions[method_name].append(extension)

    def get_action_args(self, request_environment):
        """Parse dictionary created by routes library."""
        # NOTE(Vek): Check for get_action_args() override in the
        # controller
        if hasattr(self.controller, 'get_action_args'):
            return self.controller.get_action_args(request_environment)

        try:
            args = request_environment['wsgiorg.routing_args'][1].copy()
        except (KeyError, IndexError, AttributeError):
            return {}

        args.pop('controller', None)
        args.pop('format', None)

        return args

    def get_body(self, request):
        try:
            content_type = request.get_content_type()
        except exception.InvalidContentType:
            LOG.debug("Unrecognized Content-Type provided in request")
            return None, ''

        return content_type, request.body

    def deserialize(self, meth, content_type, body):
        meth_deserializers = getattr(meth, 'wsgi_deserializers', {})
        try:
            mtype = get_media_map().get(content_type, content_type)
            if mtype in meth_deserializers:
                deserializer = meth_deserializers[mtype]
            else:
                deserializer = self.default_deserializers[mtype]
        except (KeyError, TypeError):
            raise exception.InvalidContentType(content_type=content_type)

        if (hasattr(deserializer, 'want_controller') and deserializer.want_controller):
            return deserializer(self.controller).deserialize(body)
        else:
            return deserializer().deserialize(body)

    def _should_have_body(self, request):
        return request.method in self.methods_with_body

    @webob.dec.wsgify(RequestClass=Request)
    def __call__(self, request):
        """WSGI method that controls (de)serialization and method dispatch."""
        # Identify the action, its arguments, and the requested
        # content type
        action_args = self.get_action_args(request.environ)
        action = action_args.pop('action', None)
        content_type, body = self.get_body(request)
        accept = request.best_match_content_type()

        # NOTE(Vek): Splitting the function up this way allows for
        #            auditing by external tools that wrap the existing
        #            function.  If we try to audit __call__(), we can
        #            run into troubles due to the @webob.dec.wsgify()
        #            decorator.
        return self._process_stack(request, action, action_args,
                                   content_type, body, accept)

    def _process_stack(self, request, action, action_args,
                       content_type, body, accept):
        """Implement the processing stack."""
        # Get the implementing method
        try:
            meth, extensions = self.get_method(request, action,
                                               content_type, body)
        except (AttributeError, TypeError):
            return webob.exc.HTTPNotFound()
        except KeyError as ex:
            msg = _("There is no such action: {0}").format(ex.args[0])
            return webob.exc.HTTPBadRequest(explanation=msg)
        except exception.MalformedRequestBody:
            msg = _("Malformed request body")
            return webob.exc.HTTPBadRequest(explanation=msg)

        # Now, deserialize the request body...
        try:
            contents = {}
            if self._should_have_body(request):
                # allow empty body with PUT and POST
                if request.content_length == 0:
                    contents = {'body': None}
                else:
                    contents = self.deserialize(meth, content_type, body)
        except exception.InvalidContentType:
            msg = _("Unsupported Content-Type")
            return webob.exc.HTTPBadRequest(explanation=msg)
        except exception.MalformedRequestBody:
            msg = _("Malformed request body")
            return webob.exc.HTTPBadRequest(explanation=msg)

        # Update the action args
        action_args.update(contents)

        response = None
        try:
            with ResourceExceptionHandler():
                action_result = self.dispatch(meth, request, action_args)
        except webob.exc.HTTPException as ex:
            response = ex

        if not response:
            # No exceptions; convert action_result into a ResponseObject
            resp_obj = None
            if isinstance(action_result, webob.Response):
                response = action_result
            elif isinstance(action_result, ResponseObject):
                resp_obj = action_result

            if isinstance(action_result, ResponseObject):
                resp_obj = action_result
            else:
                resp_obj = ResponseObject(action_result)

            # Run post-processing extensions
            if resp_obj:
                # Do a preserialize to set up the response object
                serializers = getattr(meth, 'wsgi_serializers', {})
                resp_obj._bind_method_serializers(serializers)
                if hasattr(meth, 'wsgi_code'):
                    resp_obj._default_code = meth.wsgi_code

                try:
                    resp_obj.preserialize(accept, self.default_serializers)

                    if not response:
                        response = resp_obj.serialize(request, accept,
                                                      self.default_serializers)
                except exception.InvalidContentType as err:
                    return webob.exc.HTTPBadRequest(explanation=err)

        if hasattr(response, 'headers'):
            for hdr, val in response.headers.items():
                # Headers must be utf-8 strings
                response.headers[hdr] = utf8(str(val))

        return response

    def get_method(self, request, action, content_type, body):
        meth, extensions = self._get_method(request,
                                            action,
                                            content_type,
                                            body)
        if self.inherits:
            _meth, parent_ext = self.inherits.get_method(request,
                                                         action,
                                                         content_type,
                                                         body)
            extensions.extend(parent_ext)
        return meth, extensions

    def _get_method(self, request, action, content_type, body):
        """Look up the action-specific method and its extensions."""
        # Look up the method
        try:
            if not self.controller:
                meth = getattr(self, action)
            else:
                meth = getattr(self.controller, action)
        except AttributeError:
            if (not self.wsgi_actions or
                action not in _ROUTES_METHODS + ['action']):
                # Propagate the error
                raise
        else:
            return meth, self.wsgi_extensions.get(action, [])

        if action == 'action':
            # OK, it's an action; figure out which action...
            mtype = get_media_map().get(content_type)
            action_name = self.action_peek[mtype](body)
        else:
            action_name = action

        # Look up the action method
        return (self.wsgi_actions[action_name],
                self.wsgi_action_extensions.get(action_name, []))

    def dispatch(self, method, request, action_args):
        """Dispatch a call to the action-specific method."""

        try:
            return method(req=request, **action_args)
        except exception.VersionNotFoundForAPIMethod:
            # We deliberately don't return any message information
            # about the exception to the user so it looks as if
            # the method is simply not implemented.
            return webob.exc.HTTPNotFound()


def action(name):
    """Mark a function as an action.

    The given name will be taken as the action key in the body.

    This is also overloaded to allow extensions to provide
    non-extending definitions of create and delete operations.
    """
    def decorator(func):
        func.wsgi_action = name
        return func
    return decorator


def extends(*args, **kwargs):
    """Indicate a function extends an operation.

    Can be used as either::

        @extends
        def index(...):
            pass

    or as::

        @extends(action='resize')
        def _action_resize(...):
            pass
    """
    def decorator(func):
        # Store enough information to find what we're extending
        func.wsgi_extends = (func.__name__, kwargs.get('action'))
        return func

    # If we have positional arguments, call the decorator
    if args:
        return decorator(*args)

    # OK, return the decorator instead
    return decorator


class ControllerMetaclass(type):
    """Controller metaclass.

    This metaclass automates the task of assembling a dictionary
    mapping action keys to method names.
    """

    def __new__(mcs, name, bases, cls_dict):
        """Adds the wsgi_actions dictionary to the class."""
        # Find all actions
        actions = {}
        extensions = []
        # start with wsgi actions from base classes
        for base in bases:
            actions.update(getattr(base, 'wsgi_actions', {}))

        for key, value in cls_dict.items():
            if not callable(value):
                continue
            if getattr(value, 'wsgi_action', None):
                actions[value.wsgi_action] = key
            elif getattr(value, 'wsgi_extends', None):
                extensions.append(value.wsgi_extends)

        # Add the actions and extensions to the class dict
        cls_dict['wsgi_actions'] = actions
        cls_dict['wsgi_extensions'] = extensions

        return super(ControllerMetaclass, mcs).__new__(mcs, name, bases, cls_dict)


@six.add_metaclass(ControllerMetaclass)
class Controller(object):
    """Default controller."""

    _view_builder_class = None

    def __init__(self, view_builder=None):
        """Initialize controller with a view builder instance."""
        if view_builder:
            self._view_builder = view_builder
        elif self._view_builder_class:
            self._view_builder = self._view_builder_class()
        else:
            self._view_builder = None
