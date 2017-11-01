"""
Relevance pipeline service module.
"""

from relevance.service import Service
from relevance.service import ResourceNotFoundError
from relevance.pipeline import PipelineManager
from relevance.pipeline import PipelineFactory


# Initialize the service and its dependencies
service = Service.instance('pipeline')
manager = service.data.manager = PipelineManager()
factory = service.data.factory = PipelineFactory(manager)

# Bootstrap
factory.load_all(service.settings)


@service.route('/pipelines', methods=['GET'])
def get_pipelines():
    """
    Get a list of pipelines.
    """
    return service.result(200, list(manager.stack.keys()))


@service.route('/pipelines/<pipeline_name>', methods=['GET'])
def get_pipeline(pipeline_name: str):
    """
    Get information about a pipeline.
    """
    try:
        pipeline = manager.resolve(pipeline_name)
    except KeyError as e:
        raise ResourceNotFoundError('pipeline', eval(str(e)))

    result = {
        'components': list(pipeline.components.keys()),
        'worker': {
            'is_started': pipeline.worker.is_started,
            'pending_tasks': pipeline.worker.scope.qsize(),
            'type': '{0}.{1}'.format(
                pipeline.worker.__class__.__module__,
                pipeline.worker.__class__.__name__,
            ),
        },
    }
    return service.result(200, result)


@service.route('/pipelines/<pipeline_name>/worker', methods=['GET'])
def get_pipeline_worker(pipeline_name: str):
    """
    Get information about a pipeline.
    """
    try:
        pipeline = manager.resolve(pipeline_name)
    except KeyError as e:
        raise ResourceNotFoundError('pipeline', eval(str(e)))

    result = {
        'is_started': pipeline.worker.is_started,
        'pending_tasks': pipeline.worker.scope.qsize(),
        'type': '{0}.{1}'.format(
            pipeline.worker.__class__.__module__,
            pipeline.worker.__class__.__name__,
        ),
    }
    return service.result(200, result)


@service.route('/pipelines/<pipeline_name>/worker', methods=['PUT'])
def start_pipeline_worker(pipeline_name: str):
    """
    Start a pipeline worker.
    """
    try:
        pipeline = manager.resolve(pipeline_name)
    except KeyError as e:
        raise ResourceNotFoundError('pipeline', eval(str(e)))

    pipeline.start()

    result = {
        'is_started': pipeline.worker.is_started,
        'pending_tasks': pipeline.worker.scope.qsize(),
        'type': '{0}.{1}'.format(
            pipeline.worker.__class__.__module__,
            pipeline.worker.__class__.__name__,
        ),
    }
    return service.result(202, result)


@service.route('/pipelines/<pipeline_name>/worker', methods=['DELETE'])
def stop_pipeline_worker(pipeline_name: str):
    """
    Stop a pipeline worker.
    """
    try:
        pipeline = manager.resolve(pipeline_name)
    except KeyError as e:
        raise ResourceNotFoundError('pipeline', eval(str(e)))

    pipeline.stop()

    result = {
        'is_started': pipeline.worker.is_started,
        'pending_tasks': pipeline.worker.scope.qsize(),
        'type': '{0}.{1}'.format(
            pipeline.worker.__class__.__module__,
            pipeline.worker.__class__.__name__,
        ),
    }
    return service.result(202, result)


@service.route('/pipelines/<pipeline_name>/components', methods=['GET'])
def get_pipeline_components(pipeline_name: str):
    """
    Get a pipeline components.
    """
    try:
        pipeline = manager.resolve(pipeline_name)
    except KeyError as e:
        raise ResourceNotFoundError('pipeline', eval(str(e)))

    result = list(pipeline.components.keys())
    return service.result(200, result)


@service.route('/pipelines/<pipeline_name>/components/<component_name>', methods=['GET'])
def get_pipeline_component(pipeline_name: str, component_name: str):
    """
    Get information about a pipeline components.
    """
    try:
        pipeline = manager.resolve(pipeline_name)
    except KeyError as e:
        raise ResourceNotFoundError('pipeline', eval(str(e)))

    try:
        component = pipeline.get(component_name)
    except KeyError as e:
        raise ResourceNotFoundError('component', eval(str(e)))

    result = {
        'target': '{0}.{1}'.format(
            component.target.__module__,
            component.target.__name__,
        ),
        'options': component.options,
        'worker': {
            'is_started': component.worker.is_started,
            'pending_tasks': component.worker.scope.qsize(),
            'type': '{0}.{1}'.format(
                component.worker.__class__.__module__,
                component.worker.__class__.__name__,
            ),
        },
    }
    return service.result(200, result)


if __name__ == '__main__':
    import os
    service.run(port=int(os.getenv('PORT', 55346)), debug=True)
