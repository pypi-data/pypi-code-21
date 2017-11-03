"""
Relevance search REST API.

This module provides the REST API for search.
"""

from relevance.service import Service
from relevance.settings import SettingsFactory
from relevance.manager import ResourceManager
from relevance.query import QueryParser
from relevance.engine import Engine
from relevance.engine import EngineFactory


# Initialize the service
service = Service.instance('search')
manager = service.data.manager = ResourceManager(Engine)


@service.before_start
def bootstrap():
    """
    Bootstrap the service.
    """
    factory = EngineFactory()
    loader = SettingsFactory(['/etc/relevance', './etc'])
    settings = service.data.settings = loader.load('search')

    engines = settings.get('engines', {}, data_type=dict)
    engines = factory.load_all_engines(engines)

    for x in engines.values():
        x.start()

    manager.save_all(engines)


@service.route('/', methods=['GET'])
def get_config():
    """
    Get the configuration.
    """
    return service.result(200, service.data.settings)


@service.route('/<engine_name>', methods=['GET'])
def do_search(engine_name: str):
    """
    Perform a search request.

    Request arguments:
        q -- the query to run.

    :param engine_name: the name of the engine to use.
    :returns: a result set object.
    """
    engine = manager.resolve(engine_name)

    query = service.request.args.get('q', '')
    parser = QueryParser()
    search = parser.loads(query)

    result_set = engine.search(search)
    result = {
        'search': search.to_dict(),
        'results': result_set,
        'time': result_set.time,
        'count': result_set.count,
    }

    if result_set.facets is not None:
        result.update({
            'facets': result_set.facets,
        })

    return service.result(200, result)


if __name__ == '__main__':
    import os
    service.run(port=int(os.getenv('PORT', 55345)), debug=True)
