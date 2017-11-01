"""
Relevance search REST API.

This module provides the REST API for search.
"""

import pydoc

from flask import request
from flask import jsonify
from flask import Response
from werkzeug import exceptions

from relevance.api import register_app
from relevance.api import start_app
from relevance.query import QueryParser
from relevance.query import QueryParserError
from relevance.facet import Facet
from relevance.engine import SearchEngine
from relevance.engine import MappingEngine
from relevance.engine import EngineError
from relevance.engine import SearchError
from relevance.engine import MappingError


def _reload():
    """
    Reload the application data.
    """
    # Load the engine instances
    this_items = {}
    for name, conf in app.settings.get('engines', {}).items():
        try:
            cls_name = conf['engine']
            target = conf['target']
        except KeyError as ex:
            raise KeyError('missing configuration key {0}'.format(str(ex)))

        cls = pydoc.locate(cls_name)
        if cls is None or not issubclass(cls, SearchEngine):
            raise ImportError('cannot find engine {0}'.format(cls_name))

        facets = {}
        for facet_name, facet_conf in conf.get('facets', {}).items():
            facet_cls = pydoc.locate(facet_conf.get('type'))
            if facet_cls is None or not issubclass(facet_cls, Facet):
                raise ImportError('cannot find facet {0}'.format(facet_conf['type']))

            facet_obj = facet_cls(
                field=facet_conf.get('field'),
                path=facet_conf.get('path'),
                **facet_conf.get('options', {}),
            )

            facets[facet_name] = facet_obj

        options = conf.get('options', {})
        this_items[name] = cls(target, facets=facets, **options)

    app.data.engines.clear()
    app.data.engines.update(this_items)


# Register the application
app = register_app('search', _reload, {'engines': {}})


@app.route('/', methods=['GET'])
def get_config() -> Response:
    """
    Get the configuration.
    """
    response = jsonify(app.settings)
    response.status_code = 201
    return response


@app.route('/<engine_name>', methods=['GET'])
def do_search(engine_name: str) -> Response:
    """
    Perform a search request.

    Request arguments:
        q -- the query to run.

    :param engine_name: the name of the engine to use.
    :returns: a result set object.
    """
    try:
        engine = app.data.engines[engine_name]
    except KeyError:
        raise EngineNotFoundError(engine_name)

    query = request.args.get('q', '')
    search = QueryParser().loads(query)

    results = engine.search(search)
    data = {
        'search': search.to_dict(),
        'results': results,
        'time': results.time,
        'count': results.count,
    }

    if results.facets is not None:
        data.update({
            'facets': results.facets,
        })

    response = jsonify(data)
    response.status_code = 200
    return response


@app.route('/<engine_name>/mapping', methods=['GET'])
def get_mapping_doc_types(engine_name: str) -> Response:
    """
    Get a list of available doc types.

    :param engine_name: the name of the engine to use.
    :returns: a list of document types.
    """
    try:
        engine = app.data.engines[engine_name]

        if not isinstance(engine, MappingEngine):
            raise MappingNotSupportedError(engine_name)
    except KeyError:
        raise EngineNotFoundError(engine_name)

    data = engine.get_doc_types()
    response = jsonify(data)
    response.status_code = 200
    return response


@app.route('/<engine_name>/mapping/<doc_type>', methods=['GET'])
def get_mapping(engine_name: str, doc_type: str) -> Response:
    """
    Get a list of available doc types.

    :param engine_name: the name of the engine to use.
    :returns: a list of document types.
    """
    try:
        engine = app.data.engines[engine_name]

        if not isinstance(engine, MappingEngine):
            raise MappingNotSupportedError(engine_name)

    except KeyError:
        raise EngineNotFoundError(engine_name)

    data = engine.get_mapping(doc_type).to_dict()
    response = jsonify(data)
    response.status_code = 200
    return response


@app.after_request
def app_cors(response: Response) -> Response:
    """
    CORS request handler.

    Adds the CORS headers to all responses so that the API can be used directly from
    a web browser.
    """
    headers = {
        'Access-Control-Allow-Origin': request.headers.get('Origin', '*'),
        'Access-Control-Allow-Credentials': 'true',
        'Access-Control-Allow-Methods': 'POST, OPTIONS, GET, PUT, DELETE, HEAD, TRACE',
        'Access-Control-Allow-Headers': request.headers.get(
            'Access-Control-Request-Headers', 'Authorization'
        ),
    }

    for k, v in headers.items():
        response.headers[k] = v

    if app.debug:
        response.headers['Access-Control-Max-Age'] = '1'

    return response


class EngineNotFoundError(RuntimeError):
    """
    Exception raised when a requested engine is not found.
    """
    pass


@app.errorhandler(EngineNotFoundError)
def engine_not_found_error(e: EngineNotFoundError) -> Response:
    response = jsonify({
        'error': {
            'desc': 'engine is not configured',
            'key': str(e),
            'code': e.__class__.__name__,
        }
    })
    response.status_code = 404
    return response


class MappingNotSupportedError(RuntimeError):
    """
    Exception raised when requesting a mapping from an unsupported engine.
    """
    pass


@app.errorhandler(MappingNotSupportedError)
def mapping_not_supported_error(e: MappingNotSupportedError) -> Response:
    response = jsonify({
        'error': {
            'desc': 'engine does not support mapping',
            'key': str(e),
            'code': e.__class__.__name__,
        }
    })
    response.status_code = 501
    return response


@app.errorhandler(QueryParserError)
def query_parser_error(e: QueryParserError) -> Response:
    """
    Handle parse errors.
    """
    response = jsonify({
        'error': {
            'desc': str(e),
            'code': e.__class__.__name__,
        }
    })
    response.status_code = 400
    return response


@app.errorhandler(EngineError)
def engine_error(e: EngineError) -> Response:
    response = jsonify({
        'error': {
            'desc': str(e),
            'code': e.__class__.__name__,
        }
    })
    response.status_code = 503
    return response


@app.errorhandler(SearchError)
def search_error(e: SearchError) -> Response:
    response = jsonify({
        'error': {
            'desc': str(e),
            'code': e.__class__.__name__,
        }
    })
    response.status_code = 503
    return response


@app.errorhandler(MappingError)
def mapping_error(e: MappingError) -> Response:
    response = jsonify({
        'error': {
            'desc': str(e),
            'code': e.__class__.__name__,
        }
    })
    response.status_code = 503
    return response


@app.errorhandler(400)
@app.errorhandler(404)
@app.errorhandler(405)
@app.errorhandler(500)
@app.errorhandler(exceptions.HTTPException)
def http_error(e: exceptions.HTTPException):
    response = jsonify({
        'error': {
            'desc': '{0}: {1}'.format(e.__class__.__name__, str(e)),
            'code': 'HTTPError',
        }
    })
    response.status_code = 500
    return response


@app.errorhandler(Exception)
def exception_error(e: Exception) -> Response:
    response = jsonify({
        'error': {
            'desc': '{0}: {1}'.format(e.__class__.__name__, str(e)),
            'code': 'Exception',
        }
    })
    response.status_code = 500
    return response


if __name__ == '__main__':
    start_app(app)
    app.run(debug=True)
