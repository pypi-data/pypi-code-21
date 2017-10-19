import collections
import inspect
import json
import logging

import accept_types
import flask
import yaml

import sepiida.errors
import sepiida.session

LOGGER = logging.getLogger(__name__)

def schema(resource, method):
    if not resource.SIGNATURE:
        return
    my_schema = {
        "$schema": "http://json-schema.org/draft-03/schema",
    }
    my_schema.update(resource.SIGNATURE.schema(method=method))
    return json.dumps(my_schema, default=str)

def example(resource):
    if not resource.SIGNATURE:
        return
    return json.dumps(resource.SIGNATURE.example)

def responses(resource, method):
    if method in ('LIST', 'GET'):
        my_schema = schema(resource, 'POST')
        my_example = example(resource)
        result = {'200': {
            'body'  : {
                'application/json'  : {
                    'example'       : my_example,
                    'schema'        : my_schema,
                },
            },
            'description'   : 'The request was successful',
        }}
    elif method == 'POST':
        result = {'204': {
            'description'   : 'The request was successful'
        }}
    else:
        raise Exception("Unrecognized method {}".format(method))

    descriptions = collections.defaultdict(lambda: [])
    for spec in resource.ERRORS:
        if spec.docs:
            description = spec.docs
        elif spec.error_code and spec.title:
            description = "`{}`: {}".format(spec.error_code, spec.title)
        elif spec.title:
            description = spec.title
        elif spec.error_code:
            description = "`{}`".format(spec.error_code)
        else:
            description = "{} raised".format(spec.exception_class.__name__)
        descriptions[str(spec.status_code or 400)].append(description)
    for k, v in descriptions.items():
        result[k] = {'description'   : '\n'.join(v)}
    return result

def method_description(resource, method):
    handler = getattr(resource, method.lower(), None)
    if not handler:
        return
    docstring = inspect.getdoc(handler)
    my_example = example(resource)
    result = {
        'description'   : docstring,
        'responses'     : responses(resource, method),
        'body'          : {
            'application/json'  : {
            }
        }
    }
    if my_example:
        result['body']['application/json']['example'] = my_example
    my_schema = schema(resource, 'POST')
    if my_schema:
        result['body']['application/json']['schema'] = my_schema
    return result

def collection_descriptions(resource):
    description = {
        'description'   : inspect.getdoc(resource),
    }
    if hasattr(resource, 'list'):
        description['get'] = method_description(resource, method='LIST')
    if hasattr(resource, 'post'):
        description['post'] = method_description(resource, method='POST')
    return description

def single_descriptions(resource):
    return {
        'description'   : inspect.getdoc(resource),
        'uriParameters' : {
            'uuid'      : {
                'description'   : "The UUID of the resource",
            }
        },
        'get'   : method_description(resource, method='GET'),
    }

def get_description(resource):
    LOGGER.debug("Getting description of %s", resource)
    descriptions = {}
    if sepiida.endpoints.has_collection_methods(resource):
        descriptions[resource.ENDPOINT] = collection_descriptions(resource)
        LOGGER.debug("Added %s: %s", resource.ENDPOINT, descriptions[resource.ENDPOINT])
    if sepiida.endpoints.has_single_methods(resource):
        uri = resource.ENDPOINT + "{uuid}/"
        descriptions[uri] = single_descriptions(resource)
        LOGGER.debug("Added %s: %s", uri, descriptions[uri])
    return descriptions

def handle_raml_request(name, baseURL, documentation, version):
    descriptions = {}
    for resource in flask.current_app.endpoints.values():
        descriptions.update(get_description(resource))
    descriptions.update({
        'title'         : name,
        'documentation' : documentation or [{'content': '', 'title': ''}],
        'version'       : version,
        'baseUri'       : baseURL,
        'mediaType'     : 'application/json',
    })
    content = yaml.dump(descriptions, default_style='|')
    return flask.make_response('#%RAML 0.8\n{}'.format(content), 200, {'Content-Type': 'application/raml+yaml'})

def handle_request(name, baseURL, documentation, version):
    accept = flask.request.headers.get('Accept', 'text/raml')
    matched_type = accept_types.get_best_match(accept, ('application/raml+yaml', 'text/raml'))
    LOGGER.debug("Handling OPTIONS request for %s", matched_type)
    if matched_type in ('text/raml', 'application/raml+yaml'):
        return handle_raml_request(name, baseURL, documentation, version)
    error = sepiida.errors.APIException(errors=[sepiida.errors.UnableToSerialize()])
    return flask.make_response(error.get_body(), error.code, error.get_headers())

def enable(app, name, baseURL, version, documentation=None):
    app.add_url_rule('/', 'root', handle_request, methods=['OPTIONS'], defaults={
        'baseURL'       : baseURL,
        'documentation' : documentation,
        'name'          : name,
        'version'       : version
    })
    sepiida.session.public_endpoint(app, 'root.options')
