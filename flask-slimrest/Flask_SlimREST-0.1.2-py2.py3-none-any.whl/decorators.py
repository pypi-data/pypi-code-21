"""Decorators providing the main functionality on flask_slimrest"""

from functools import wraps
from flask import request, Response
from marshmallow import Schema

from .utils import make_api_error_response, make_api_response
from .exceptions import NoMatchingSchemaError
from .pagination import PaginationResult


def load(schema, handle_validation_errors=True):
    """ Deserialize JSON data with the given marshmallow schema

    This decorator extracts the JSON payload from the request body and attempts to deserialize it using the given instance of :class:`marshmallow.Schema`.
    A :class:`flask.Response` object with an error message is returned if there is no JSON data in the request. Otherwise the JSON data is passed to the
    schema instance for deserialization.

    The ``handle_validation_errors`` parameter controls the decorator's behaviour when the schema validation fails. If it is set to ``True``, it will
    automatically return an error message if any validation errors are encountered. If it is set to ``False``, validation errors are ignored.

    The :class:`marshmallow.UnmarshalResult` object returned by the marshmallow schema is then passed as the ``data`` kwarg to the decorated function for
    further processing. The return value of the decorated function is returned without any changes.

    :param schema: The marshmallow schema used to deserialize the JSON payload
    :param handle_validation_errors: Whether or not to automatically respond with an error message when validation of the payload fails
    :type schema: marshmallow.Schema
    :type handle_validation_errors: bool

    """
    def real_decorator(function):
        @wraps(function)
        def wrapper(self, *args, **kwargs):
            data = request.get_json()
            if not data:
                return make_api_error_response('NO JSON data payload in request. Make sure to set the Content-Type header to application/json')
            result = schema.load(data)
            if handle_validation_errors and any(result.errors):
                return make_api_error_response('Validation of payload data failed.', extra_dict_values={'errors': result.errors})
            kwargs['data'] = result
            return function(self, *args, **kwargs)
        return wrapper
    return real_decorator


def _dump_single(obj, schema_or_dict):
    if isinstance(schema_or_dict, Schema):
        return schema_or_dict.dump(obj)
    elif isinstance(schema_or_dict, dict):
        if obj.__class__.__name__ not in schema_or_dict:
            raise NoMatchingSchemaError('None of the provided schemas matches the objects type: ' + obj.__class__.__name__)
        schema = schema_or_dict[obj.__class__.__name__]
        return schema.dump(obj)
    else:
        raise TypeError('Invalid type provided to dump function. Must provide either an instance of marshmallow.Schema or a dictionary.')


def dump(schema_or_dict, paginated=False, return_code=200):
    """ Serialize an object to the JSON representation with the given marshmallow schema(s)

    The ``schema_or_dict`` parameter may either be an instance of :class:`marshmallow.Schema` or a dictionary containing a schema mapping.
    If a single schema instance is provided, this schema is always used to serialize any object(s) returned by the decorated functions.
    If a dictionary is provided, the *class name* of each returned object is analyzed and the schema which is identified by a key similar to
    the class name is selected. This is an example of a valid schema mapping:

    .. code-block:: python

        mapping = {
            'ClassA': ClassASchema,
            'ClassB': ClassBSchema
        }

    The ``paginated`` parameter defines whether or not the return value of the decorated function is a paginated set of objects.

    The return value of this decorator is always of the type :class:`flask.Response`. The HTTP status code for the response can be specified
    by the ``return_code`` parameter. Please note that if the decorated function already returns an instance of :class:`flask.Response`
    (e.g. an error message due to a malformed request), this decorator will simply return this value without any changes.

    :param schema_or_dict: Either an instance of :class:`marshmallow.Schema` or a dictionary containing a schema mapping (see example)
    :param paginated: Whether or not the return value of the decorated function is paginated
    :param return_code: The HTTP status code which is returned
    :type paginated: bool
    :type return_code: int
    :returns: The serialized JSON representation of the return value of the decorated function
    :rtype: flask.Response
    """
    def real_decorator(function):
        @wraps(function)
        def wrapper(self, *args, **kwargs):
            obj = function(self, *args, **kwargs)
            if isinstance(obj, Response):
                return obj
            if paginated:
                if not isinstance(obj, PaginationResult):
                    raise TypeError('Input must be of type PaginationResult when paginated=True.')
                result = {
                    'results': [_dump_single(result, schema_or_dict).data for result in obj.results],
                    'page': obj.page,
                    'page_count': obj.page_count,
                    'next': obj.next_page_url,
                    'previous': obj.previous_page_url
                }
                return make_api_response(result, return_code)
            else:
                dump = _dump_single(obj, schema_or_dict)
                return make_api_response(dump.data, return_code)
        return wrapper
    return real_decorator


def load_json(function):
    """ Extract the JSON payload from the request, but do not deserialize with a marshmallow schema. Passes the resulting dict to the decorated function.

    Sometimes it may be necessary to do some manual processing instead of just using the :func:`load` decorator to deserialize the JSON data to an object.
    In this case it may still be desirable to do some preprocessing of the request. This is exactly what this decorator does.
    It extracts the JSON payload using Flask's :func:`flask.request.get_json` function. If this fails (e.g. because the Content-Type is not ``application/json`` or there is no request body at all),
    it will respond with an error message. If everything goes well, the resulting dictionary is passed as the ``data`` kwarg to the decorated function.

    :returns: The return value of the decorated function or an error message of type :class:`flask.Response` if there is no valid JSON payload in the request
    """
    @wraps(function)
    def wrapper(self, *args, **kwargs):
        data = request.get_json()
        if not data:
            return make_api_error_response('NO JSON data payload in request. Make sure to set the Content-Type header to application/json')
        kwargs['data'] = data
        return function(self, *args, **kwargs)
    return wrapper


def catch(exception, error_message, error_code=500):
    """ Conveniently handle a specific exception and respond with an error message

    Properly handling exceptions is an important task. If for example your ORM does not find the requested object and throws an exception,
    you want to return a 404 error together with an informative message rather than failing with a generic server error. This decorator
    simplifies this task. For each exception type, you can define a custom error message and the intended HTTP error code. The decorator
    may be used multiple times on each endpoint to catch different exception types.

    :param exception: The exception type which should be catched
    :param error_message: The message which is used in the response when the exception is raised
    :param error_code: The HTTP status code used in the response when the exception is raised
    :type exception: exceptions.Exception
    :type error_message: str
    :type error_code: int
    """
    def real_decorator(function):
        @wraps(function)
        def wrapper(self, *args, **kwargs):
            try:
                return function(self, *args, **kwargs)
            except exception:
                return make_api_error_response(error_message, error_code)
        return wrapper
    return real_decorator


def paginate(pagination_helper):
    """ Paginate the return value of the decorated function using a pagination_helper callback function

    When a lot of objects need to be serialized it is a common practice to use pagination in order to keep the size and duration of each request within reasonable bounds.
    The :func:`dump` decorator can automatically handle a paginated set of objects, but requires certain metadata to produce the appropriate result (see :func:`dump` for details).
    Depending on the underlying data source (e.g. an ORM, a simple list structure, ... ) the implementation of pagination may vary significantly. Since flask_slimrest is
    designed to work independently of the data source, the paginate decorator does not implement any specific paging method. Instead you have to provide a callback function, which
    will be called by this decorator. The callback function must return an instance of :class:`flask_slimrest.pagination.PaginationResult`, which provides the necessary metadata for
    producing the API response in the :func:`dump` decorator.

    :param pagination_helper: The callback function which actually does the paging
    :type pagination_helper: types.FunctionType
    :returns: The return value of the pagination_helper function
    :rtype: flask_slimrest.pagination.PaginationResult
    """
    def real_decorator(function):
        @wraps(function)
        def wrapper(self, *args, **kwargs):
            return pagination_helper(function(self, *args, **kwargs))
        return wrapper
    return real_decorator


def filter_results(filter_function, filter_args=[]):
    """ Filter the returned values of the decorated function using a filter function

    When retrieving a collection of objects from a given data source, you may want to allow filtering of the returned objects by using appropriate query arguments.
    The filter decorator allows you to specify a list of allowed query arguments which will be passed to a filter function that processes the result of the decorated function with these arguments.
    Depending on the underlying data source (e.g. an ORM, a simple list structure, ... ) the implementation of the filtering process may vary significantly. Since flask_slimrest is
    designed to work independently of the data source, the filter decorator does not implement any specific filtering method. Instead you have to provide a filter function, which
    will be called by this decorator. The filter function will receive the unfiltered input as well as the query arguments provided by the user. It must return the filtered result.
    Please note that if you additionally want to paginate the results, the filter decorator should be applied before the :func:`paginate` decorator is applied.

    :param filter_function: The function which actually does the filtering
    :type filter_function: types.FunctionType
    :param filter_args: A list of allowed (whitelisted) query arguments that will be passed to the filter function when provided in the request
    :returns: The return value of the filter function
    """
    def real_decorator(function):
        @wraps(function)
        def wrapper(self, *args, **kwargs):
            passed_args = {}
            for arg in request.args:
                if arg in filter_args:
                    passed_args[arg] = request.args[arg]
            return filter_function(function(self, *args, **kwargs), **passed_args)
        return wrapper
    return real_decorator


def add_endpoint(path, methods=['GET']):
    """ Add the decorated function as an endpoint in the given namespace.

    :param path: The path (relative to the path of the namespace) which is used for registering the route to this endpoint
    :param methods: The HTTP methods allowed for this endpoint
    :type path: str
    :type methods: collections.list

    """
    def real_decorator(function):
        @wraps(function)
        def wrapper(self, *args, **kwargs):
            return function(self, *args, **kwargs)

        wrapper.__endpoint = {
            'path': path,
            'methods': methods
        }
        return wrapper

    return real_decorator
