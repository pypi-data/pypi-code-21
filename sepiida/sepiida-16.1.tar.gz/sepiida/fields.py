import inspect
import json
import logging
import math
import urllib.parse
import uuid
from datetime import date, datetime, timezone

import arrow
import flask

import sepiida.routing
from sepiida.errors import APIException, AppError, Error

LOGGER = logging.getLogger(__name__)

class UnpackageError(Exception):
    def __init__(self, errors):
        super().__init__()
        assert isinstance(errors, list)
        self.errors = errors

class PackageError(Exception):
    def __init__(self, errors):
        super().__init__()
        assert isinstance(errors, list)
        self.errors = errors
    def __str__(self):
        return "\n".join(self.errors)

class FakeArguments():
    def __init__(self, fields):
        self.fields = FakeFieldsArgument(fields)

class FakeFieldsArgument():
    def __init__(self, values):
        self.values = values

TYPES_TO_NAME = {
    date        : 'a date',
    datetime    : 'a datetime',
    dict        : 'an object',
    list        : 'an array',
    int         : 'a number',
    float       : 'a number',
    bool        : 'a boolean',
    str         : 'a string',
    type(None)  : 'null',
    uuid.UUID   : 'a uuid',
    'URI'       : 'a uri',
    'URL'       : 'a URL',
}
def _unpackage_error_message(name, expected_type, provided_data):
    provided_type_name = TYPES_TO_NAME[type(provided_data)]
    expected_type_name = TYPES_TO_NAME[expected_type]
    return "The property '{}' must be {}. You provided {}".format(name, expected_type_name, provided_type_name)

def _raise_validation_error(title):
    errors = [Error('request-validation-error', title)]
    raise UnpackageError(errors)

def _raise_validation_type_error(name, expected_type, provided_data):
    title = _unpackage_error_message(name, expected_type, provided_data)
    errors = [Error('type-validation-error', title)]
    raise UnpackageError(errors)

def _maybe_raise_all_sub_errors(errors):
    if not errors:
        return

    sub_errors = []
    for e in errors:
        sub_errors += e.errors
    raise UnpackageError(errors=sub_errors)

class Unspecified():
    pass

class Field(): # pylint: disable=too-many-instance-attributes
    TYPE_NAME = 'raw-field'
    def __init__(self, # pylint: disable=too-many-arguments
            choices    = None,
            default    = Unspecified,
            docs       = None,
            example    = Unspecified,
            filterable = True,
            methods    = None,
            nullable   = False,
            optional   = False,
            rename     = None,
            sortable   = True,
        ):
        self.choices = choices
        if default != Unspecified:
            self.default = default
        self.docs           = docs
        self.filterable     = filterable
        self.methods        = methods if methods is not None else ['GET', 'POST', 'PUT']
        self.nullable       = nullable
        self.optional       = optional
        self.rename         = rename
        self.sortable       = sortable

        self._generate_example(example, choices)

    def _check_choices(self, name, data):
        if self.choices is None:
            return

        if data not in self.choices:
            choices = ["'{}'".format(choice) for choice in self.choices]
            choices = ", ".join(choices)
            error = Error(
                'property-value-not-in-allowed-values',
                "The property '{}' must be one of {}. You provided '{}'".format(name, choices, data)
            )
            raise UnpackageError([error])

    def _generate_example(self, example, choices):
        if example != Unspecified:
            self.example = example
        elif choices:
            self.example = '|'.join([str(choice) for choice in choices])

    def package(self, response):
        raise NotImplementedError

    def unpackage(self, name, data, method):
        raise NotImplementedError

    def get_options_description(self):
        description = {
            'type'          : self.TYPE_NAME,
            'choices'       : self.choices,
            'filterable'    : self.filterable,
            'methods'       : self.methods,
            'optional'      : self.optional,
            'sortable'      : self.sortable,
        }
        if hasattr(self, 'default'):
            description['default'] = self.default
        return description

    def get_filter_value(self, name, value): # pylint: disable=unused-argument,no-self-use
        return value

    def process_arguments(self, arguments):
        pass

    def schema(self, method='POST'):
        my_schema = {
            'description'   : self.docs,
            'filterable'    : self.filterable,
            'nullable'      : self.nullable,
            'type'          : self.TYPE_NAME,
            'sortable'      : self.sortable,
        }
        if method == 'GET':
            my_schema['optional'] = self.optional
        if method == 'POST' and hasattr(self, 'default'):
            my_schema['default'] = self.default
        if self.choices:
            my_schema['enum'] = self.choices
        if hasattr(self, 'example'):
            my_schema['example'] = json.dumps(self.example)
        return my_schema

class Anything(Field):
    TYPE_NAME = 'anything'
    def package(self, response):
        return response

    def unpackage(self, name, data, method):
        return data

class SignatureField(Field): # pylint: disable=abstract-method
    def __init__(self, s=None, **kwargs):
        super().__init__(**kwargs)
        self.signature = s
        try:
            for k, v in self.signature.items():
                if inspect.isclass(v):
                    raise Exception(("You have provided a class '{}' as part of the signature for {}."
                        "Please specify the signature using instances of the class, not the class itself".format(v, k)))
        except AttributeError:
            pass

    def _process_against_signature(self, arguments):
        errors = []
        if arguments.fields and not self.signature:
            errors.append(Error(
                status_code=400,
                error_code='unable-to-specify-fields',
                title=("You specified return fields. This resource cannot return a subset of its fields"),
            ))

        if arguments.filters and not self.signature:
            errors.append(Error(
                status_code=400,
                error_code='unable-to-specify-filters',
                title=("You specified filters. This resource cannot be filtered"),
            ))
        return errors

    def _process_fields(self, arguments):
        if not isinstance(self.signature, SignatureField):
            return []
        return self.signature._process_fields(arguments) # pylint: disable=protected-access

    def _process_filters(self, arguments):
        if not isinstance(self.signature, SignatureField):
            return []
        return self.signature._process_filters(arguments) # pylint: disable=protected-access

    def _process_sorts(self, arguments):
        if not isinstance(self.signature, SignatureField):
            return []
        return self.signature._process_sorts(arguments) # pylint: disable=protected-access

    def process_arguments(self, arguments):
        errors = self._process_against_signature(arguments)
        errors += self._process_fields(arguments)
        errors += self._process_filters(arguments)
        errors += self._process_sorts(arguments)

        if errors:
            raise APIException(errors=errors)

class Object(SignatureField):
    TYPE_NAME = 'object'
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if self.signature:
            self.example = {k: v.example for k, v in self.signature.items() if hasattr(v, 'example')}
        else:
            self.example = None
        if self.signature:
            fieldnames = set(self.signature.keys())
            for key, field in self.signature.items():
                if field.rename and field.rename in fieldnames:
                    raise Exception((
                        "You cannot rename field {} to {} because another "
                        "field is already using that name").format(key, field.rename))

    def _fieldnames(self):
        results = list(self.signature.keys())
        for name, field in self.signature.items():
            if isinstance(field, SignatureField):
                results += ["{}.{}".format(name, f) for f in field._fieldnames()] # pylint: disable=protected-access
        return results

    def _filternames(self):
        results = [name for name, field in self.signature.items() if field.filterable]
        for name, field in self.signature.items():
            if isinstance(field, SignatureField):
                results += ["{}.{}".format(name, f) for f in field._filternames()] # pylint: disable=protected-access
        return results

    def _process_fields(self, arguments):
        if not self.signature:
            return []

        errors = []
        for field in (arguments.fields.values if arguments.fields else []):
            if field not in self.signature:
                parent_field, _, child_field = field.partition('.')
                if parent_field in self.signature:
                    self.signature[parent_field]._process_fields(FakeArguments([child_field])) # pylint: disable=protected-access
                else:
                    msg = ("You specified the resource return '{}' but it is not a valid field for this resource. "
                           "Valid fields include {}").format(field, _quote(self._fieldnames()))
                    errors.append(Error('invalid-field-specified', msg))
        return errors

    def _process_filters(self, arguments):
        if not self.signature:
            return []

        errors = []
        for _filter in arguments.filters:
            try:
                field = self.signature[_filter.name]
            except KeyError:
                if self.signature:
                    title = ("Your requested filter property, '{}', is not a valid property for this endpoint. "
                            "Please choose one of {}".format(_filter.name, _quote(self._filternames())))
                else:
                    title = "You requested a filter on property '{}'. This endpoint does not allow filtering".format(_filter.name)
                errors.append(Error('invalid-filter-property', title))
                continue

            if not field.filterable:
                title = ("Your requested filter property, '{}', is not a valid property for this endpoint. "
                         "Please choose one of {}").format(_filter.name, _quote(self._filternames()))

                errors.append(Error(
                    status_code = 400,
                    error_code  = 'invalid-filter-property',
                    title       = title,
                ))
                continue

            new_values = []
            for value in _filter.values:
                try:
                    new_value = field.get_filter_value(_filter.name, value)
                    if field.choices and new_value not in field.choices:
                        title = ("You requested a filter on '{name}' to the value '{value}'. "
                                 "The property '{name}' only permits values from a particular "
                                 "set of options. Please use one of the following options for "
                                 "your filter: {values}").format(name=_filter.name, value=value, values=', '.join(field.choices))
                        errors.append(Error(
                            status_code = 400,
                            error_code  = 'invalid-filter-value',
                            title       = title,
                        ))
                        continue
                    new_values.append(new_value)
                except ValueError:
                    title = ("You requested a filter on '{name}' to the value '{value}'. "
                            "The property '{name}' is a {type} and so filters on it must "
                            "also be {type}").format(name=_filter.name, value=value, type=field.TYPE_NAME)
                    errors.append(Error(
                        status_code = 400,
                        error_code  = 'invalid-filter-value',
                        title       = title,
                    ))
                except AppError as e:
                    errors.append(Error(
                        status_code = 500,
                        error_code  = 'app-error',
                        title       = str(e)
                    ))
            _filter.values = new_values
        return errors

    def _process_sorts(self, arguments):
        errors = []
        for sort in (arguments.sorts.values if arguments.sorts else []):
            try:
                field = self.signature[sort.name]
            except KeyError:
                if self.signature:
                    title = ("Your requested sort property, '{}', is not a valid property for this endpoint. "
                            "Please choose one of {}".format(sort.name, _quote(self._sortnames())))
                else:
                    title = "You requested a sort on property '{}'. This endpoint does not allow sorting".format(sort.name)
                errors.append(Error(status_code=400, error_code='invalid-sort-property', title=title))
                continue

            if not field.sortable:
                title = ("Your requested sort property, '{}', has sorting disabled for this endpoint. "
                         "Please remove it and try again. "
                         "The following fields are allowed for sorting: {}").format(sort.name, _quote(self._sortnames()))
                errors.append(Error(status_code=400, error_code='disabled-sort-property', title=title))
                continue

        return errors

    def _sortnames(self):
        return [name for name, field in self.signature.items() if field.sortable]

    def package(self, response):
        package = {}
        if response is None:
            return None

        if self.signature is None:
            return dict(response)

        if response is None:
            return None

        errors = []
        for k, v in self.signature.items():
            try:
                if 'GET' in v.methods:
                    try:
                        newkey = k if v.rename is None else v.rename
                        package[k] = v.package(response[newkey])
                    except (TypeError, ValueError) as e:
                        errors.append("Programmer failed to provide the correct type for {}: {}".format(k, e))
            except KeyError:
                if not v.optional:
                    errors.append("Programmer failed to provide {}, which is a required value to return for this resource.".format(k))
        if errors:
            raise PackageError(errors=errors)
        return package

    def unpackage(self, name, data, method):
        if self.nullable and data is None:
            return None

        if not isinstance(data, dict):
            raise _raise_validation_type_error(name, dict, data)

        self._check_choices(name, data)

        if self.signature is None:
            return data

        package = {}
        errors = []
        for k, v in data.items():
            try:
                sub_name = "{}{}".format(name + "." if name else '', k)
                try:
                    sub_signature = self.signature[k]
                except KeyError:
                    raise _raise_validation_error("You provided '{}'. It is not a valid property for this resource".format(sub_name))
                value = sub_signature.unpackage(sub_name, v, method)
            except UnpackageError as e:
                errors.append(e)
                value = None
            package[k] = value
        for k, v in self.signature.items():
            sub_name = "{}{}".format(name + "." if name else '', k)
            if method not in v.methods and k in package:
                post_errors = [Error('cannot-set-property', "You provided '{}'. It cannot be directly set via {}".format(sub_name, method))]
                errors.append(UnpackageError(post_errors))
            if method == 'POST' and method in v.methods and k not in package:
                try:
                    package[k] = getattr(v, 'default')
                except AttributeError:
                    post_errors = [Error('missing-parameter',
                        "You did not provide the {} property. It is required when POSTing to this resource".format(sub_name)
                    )]
                    errors.append(UnpackageError(post_errors))
            if v.rename is not None:
                package[v.rename] = package.pop(k)
        _maybe_raise_all_sub_errors(errors)
        return package

    def get_options_description(self):
        base = super().get_options_description()
        if self.signature:
            base['fields'] = {k: v.get_options_description() for k, v in self.signature.items()}
        return base

    def schema(self, method='POST'):
        my_schema = super().schema(method)
        if not self.signature:
            return my_schema
        my_schema.update({
            'properties'    : {k: v.schema(method) for k, v in self.signature.items()},
        })
        if method == 'POST':
            my_schema['required'] = [k for k, v in self.signature.items() if not hasattr(v, 'default')]
        elif method == 'GET':
            my_schema['required'] = [k for k, v in self.signature.items() if not v.optional]
        return my_schema

class ObjectEnvelope(Object):
    """
    This class is essentially for sepiida internal use. It's designed to be more lenient than the regular Object
    class for use in the LIST part of endpoint. Older versions of sepiida did not enforce that various queries
    worked differently on a LIST vs a GET. This class papers over that design choice from long ago to maintain
    backwards compatibility
    """
    def __init__(self, s):
        signature = {
            'resources' : Array(s=s)
        }
        super().__init__(s=signature)

    def process_arguments(self, arguments):
        errors = self._process_against_signature(arguments)
        errors += super()._process_fields(arguments)
        errors += self.signature['resources']._process_filters(arguments) # pylint: disable=protected-access
        errors += self.signature['resources']._process_sorts(arguments) # pylint: disable=protected-access

        if errors:
            raise APIException(errors=errors)

    def _filternames(self):
        return self.signature['resources']._filternames() # pylint: disable=protected-access

    def _sortnames(self):
        return self.signature['resources']._sortnames() # pylint: disable=protected-access

    def package(self, response):
        return super().package({
            'resources' : response
        })

class Array(SignatureField):
    TYPE_NAME = 'array'
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.example  = [self.signature.example if self.signature and hasattr(self.signature, 'example') else '...']

    def _fieldnames(self):
        return self.signature._fieldnames() if isinstance(self.signature, SignatureField) else [] # pylint: disable=protected-access

    def _filternames(self):
        return self.signature._filternames() if isinstance(self.signature, SignatureField) else [] # pylint: disable=protected-access

    def package(self, response):
        if response is None:
            return None

        _convert = (lambda x: self.signature.package(x)) if self.signature else (lambda x: x) # pylint: disable=unnecessary-lambda
        return [_convert(value) for value in response]

    def unpackage(self, name, data, method):
        if self.nullable and data is None:
            return None

        if not isinstance(data, list):
            raise _raise_validation_type_error(name, list, data)

        self._check_choices(name, data)

        if self.signature is None:
            return data

        package = []
        errors = []
        for i, d in enumerate(data):
            try:
                sub_name = "{}{}".format(name + "." if name else '', i)
                value = self.signature.unpackage(sub_name, d, method)
            except UnpackageError as e:
                errors.append(e)
                value = None
            package.append(value)
        _maybe_raise_all_sub_errors(errors)
        return package

    def schema(self, method='POST'):
        my_schema = super().schema(method)
        if not self.signature:
            return my_schema
        my_schema.update({
            'items'    : self.signature.schema(method=method)
        })
        return my_schema
# Backwards compatibility with previous sepiida versions
ist = Array

class String(Field):
    TYPE_NAME = 'string'
    def package(self, response):
        return str(response) if response is not None else None

    def unpackage(self, name, data, method):
        if self.nullable and data is None:
            return None

        if not isinstance(data, str):
            raise _raise_validation_type_error(name, str, data)

        self._check_choices(name, data)

        return data

class Integer(Field):
    TYPE_NAME = 'integer'
    def package(self, response):
        return int(response) if response is not None else None

    def unpackage(self, name, data, method):
        if self.nullable and data is None:
            return None

        if not isinstance(data, int) or isinstance(data, bool):
            raise _raise_validation_type_error(name, int, data)

        self._check_choices(name, data)

        return int(data)

    def get_filter_value(self, name, value):
        parsed = float(value)
        if int(parsed) != parsed:
            raise ValueError("It's a float but not an int")
        return int(parsed)

class Float(Field):
    TYPE_NAME = 'float'
    def package(self, response):
        if isinstance(response, float) and any([math.isnan(response), math.isinf(response)]):
            raise ValueError("Programmer provided '{}' which cannot be serialized correctly".format(response))
        return float(response) if response is not None else None

    def unpackage(self, name, data, method):
        if self.nullable and data is None:
            return None

        acceptable_types = [isinstance(data, x) for x in (int, float)]
        unacceptable_types = [isinstance(data, bool)]
        if not any(acceptable_types) or any(unacceptable_types):
            raise _raise_validation_type_error(name, float, data)

        self._check_choices(name, data)

        return float(data)

    def get_filter_value(self, name, value):
        return float(value)

class Boolean(Field):
    TYPE_NAME = 'boolean'
    def package(self, response):
        return bool(response) if response is not None else None

    def unpackage(self, name, data, method):
        if self.nullable and data is None:
            return None

        if not isinstance(data, bool):
            raise _raise_validation_type_error(name, bool, data)

        self._check_choices(name, data)

        return bool(data)

    def get_filter_value(self, name, value):
        lower = value.lower()
        if lower in ('f', 'false') or lower == '0':
            return False
        elif lower in ('t', 'true') or lower == '1':
            return True
        else:
            raise ValueError("{} does not parse to a bool".format(value))

class Date(Field):
    TYPE_NAME = 'iso-8601 date'
    def package(self, response):
        if response is None:
            return None

        if isinstance(response, date):
            return response.isoformat()
        else:
            raise TypeError("{} is not a valid date".format(response))

    def unpackage(self, name, data, method):
        if self.nullable and data is None:
            return None

        if not isinstance(data, str):
            raise _raise_validation_type_error(name, date, data)

        try:
            return arrow.get(data).date()
        except arrow.parser.ParserError:
            raise _raise_validation_type_error(name, date, data)

    def get_filter_value(self, name, value):
        try:
            return arrow.get(value).date()
        except arrow.parser.ParserError:
            raise ValueError("{} does not parse to a date".format(value))

class Datetime(Field):
    TYPE_NAME = 'iso-8601 datetime'
    def package(self, response):
        if response is None:
            return None

        if isinstance(response, datetime):
            if response.tzinfo == timezone.utc:
                return response.isoformat()
            if response.tzinfo is None:
                return response.replace(tzinfo=timezone.utc).isoformat()
            return response.astimezone(tz=timezone.utc).isoformat()
        else:
            raise TypeError("{} is not a valid datetime".format(response))

    def unpackage(self, name, data, method):
        if self.nullable and data is None:
            return None

        if not isinstance(data, str):
            raise _raise_validation_type_error(name, datetime, data)

        try:
            return arrow.get(data).datetime.astimezone(tz=timezone.utc)
        except arrow.parser.ParserError:
            raise _raise_validation_type_error(name, datetime, data)

    def get_filter_value(self, name, value):
        try:
            return arrow.get(value).datetime
        except arrow.parser.ParserError:
            raise ValueError("{} does not parse to a datetime".format(value))

class UUID(Field):
    TYPE_NAME = 'uuid'
    def package(self, response):
        if response is None:
            return None

        if isinstance(response, uuid.UUID):
            return str(response)
        else:
            raise ValueError("{} is not a valid UUID".format(response))

    def unpackage(self, name, data, method):
        if self.nullable and data is None:
            return None

        if not isinstance(data, str):
            raise _raise_validation_type_error(name, uuid.UUID, data)

        try:
            return uuid.UUID(data)
        except ValueError:
            raise _raise_validation_type_error(name, uuid.UUID, data)

    def get_filter_value(self, name, value):
        return uuid.UUID(value)

def _app_has_endpoint(app, endpoint):
    for rule in app.url_map.iter_rules():
        if rule.endpoint == endpoint:
            return True
    return False

class URI(String):
    TYPE_NAME = 'URI'
    def __init__(self, endpoint, **kwargs):
        super().__init__(**kwargs)
        self.endpoint = endpoint

    def package(self, response):
        if response is None:
            return None
        elif isinstance(response, (int, uuid.UUID)):
            return sepiida.routing.uri(self.endpoint, response)
        elif isinstance(response, str):
            endpoint, _ = sepiida.routing.extract_parameters(flask.current_app, method='GET', url=response)
            assert endpoint == self.endpoint, "URI is valid but for the wrong endpoint"
            return response
        return sepiida.routing.uri(self.endpoint, **response)

    def unpackage(self, name, data, method):
        if self.nullable and data is None:
            return None
        try:
            route, parameters = sepiida.routing.extract_parameters(flask.current_app, method='GET', url=data)
            if not route:
                raise _raise_validation_error("The URI you provided for {} - {} - is not recognized as a URI".format(name, data))
            if route != self.endpoint:
                msg = (
                    "The URI you provided for {property_name} - {data} - "
                    "appears to be a URI for a {bad_route} resource, not a {good_route} resource".format(
                        property_name   = name,
                        data            = data,
                        bad_route       = route,
                        good_route      = self.endpoint,
                ))
                raise _raise_validation_error(msg)
        except AttributeError:
            raise _raise_validation_type_error(name, 'URI', data)
        parameters = parameters or {}
        parameters['uri'] = data
        return parameters

    def get_filter_value(self, name, value):
        _, params = sepiida.routing.extract_parameters(flask.current_app, method='GET', url=value)
        _uuid = params.get('uuid') or params.get('_id')
        if not _uuid:
            if _app_has_endpoint(flask.current_app, self.endpoint):
                raise ValueError("{} is not a recognized URI for {}".format(value, self.endpoint))
            else:
                raise AppError("The endpoint '{}' is not a valid endpoint for this application".format(self.endpoint))
        return _uuid

class URL(String):
    TYPE_NAME = 'URL'
    def package(self, response):
        if response is None:
            return response
        if not self._valid_url(response):
            message = "The URL supplied by the programmer '{}' is not a valid URL".format(response)
            LOGGER.error(message)
        return self._strip_credentials(response)

    def unpackage(self, name, data, method):
        if self.nullable and data is None:
            return None
        if not self._valid_url(data):
            raise _raise_validation_type_error(name, 'URL', data)
        return data

    @staticmethod
    def _valid_url(url):
        try:
            parsed = urllib.parse.urlparse(url)
            return all((
                bool(parsed.netloc),
                bool(parsed.scheme),
            ))
        except AttributeError:
            return False

    @staticmethod
    def _strip_credentials(url):
        parsed = urllib.parse.urlparse(url)
        netloc = parsed.netloc
        if parsed.username is not None:
            netloc = netloc[len(parsed.username) + 1:]
        if parsed.password is not None:
            netloc = netloc[len(parsed.password) + 1:]
        return urllib.parse.urlunparse((parsed[0], netloc, parsed[2], parsed[3], parsed[4], parsed[5]))

    def get_filter_value(self, name, value):
        if not self._valid_url(value):
            raise ValueError("{} is not a URL".format(value))
        return value

def _quote(collection):
    return ", ".join(["'{}'".format(c) for c in sorted(collection)])
