"""
This service module provides the API for searchers and engines.
"""

from relevance.service import Service
from relevance.settings import SettingsFactory
from relevance.manager import ResourceManager
from relevance.query import Search
from relevance.query import QueryParser
from relevance.engine import Engine
from relevance.engine import EngineFactory


# Initialize the service
service = Service.instance('search')  # pylint: disable=invalid-name
manager = service.data.manager = ResourceManager(Engine)  # pylint: disable=invalid-name


@service.before_first_request
def _bootstrap():
    """
    Bootstrap the service.
    """
    factory = EngineFactory()
    loader = SettingsFactory(['/etc/relevance', './etc'])
    settings = service.data.settings = loader.load('search')

    engines = settings.get('engines', {}, data_type=dict)
    engines = factory.load_all_engines(engines)

    for item in engines.values():
        item.start()

    manager.save_all(engines)


@service.route('/<engine_name>', methods=['GET'])
def do_search(engine_name: str):
    """
    Perform a search request.

    :Method: GET
    :Path: /engines/`engine_name`
    :Query Arguments: **q** - the search request to execute. See :mod:`relevance.query`.
    :param engine_name: the name of the engine to query.

    :Statuses: `200` on success.
    :Response:
        .. code-block:: json

            {
                "search": {
                    "query": "foo==\"bar\"",
                },
                "results": [
                    {"text": "my test document"},
                    ...
                ],
                "facets": {
                    "foo": {
                        "bar": 42,
                        "baz": 12
                    }
                },
                "time": 0.0432,
                "count": 143
            }
    """
    engine: Engine = manager.resolve(engine_name)  # type: ignore

    query = service.request.args.get('q', '')
    parser = QueryParser()
    search: Search = parser.loads(query)  # type: ignore
    result_set = engine.search(search)

    results = []
    for row in result_set:
        item = {
            '_id': row.uid,
            '_score': row.score,
            '_schema': row.schema,
            '_type': row.doc_type,
        }
        item.update(row)
        results.append(item)

    result = {
        'search': search.to_dict(),
        'results': results,
        'time': result_set.time,
        'count': result_set.total_count,
    }

    if result_set.facets is not None:
        result.update({
            'facets': result_set.facets,
        })

    return service.result(200, result)


if __name__ == '__main__':
    import os
    service.run(port=int(os.getenv('PORT', 55345)), debug=True)
