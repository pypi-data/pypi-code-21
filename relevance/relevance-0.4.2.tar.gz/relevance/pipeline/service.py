"""
This module contains the service layer for the :mod:`.pipeline` module.
"""

from relevance.service import Service
from relevance.manager import ResourceManager
from relevance.pipeline import Pipeline
from relevance.pipeline import PipelineFactory


# Initialize the service and its dependencies
service = Service.instance('pipeline')
manager = service.data.manager = ResourceManager(Pipeline)
factory = service.data.factory = PipelineFactory(manager)

# Bootstrap
factory.load_all(service.settings, manager)


@service.route('/pipelines', methods=['GET'])
def get_pipelines():
    """
    Get a list of pipelines.

    :Method: GET
    :Path: /pipelines

    :Statuses: `200` on success.
    :Response:
        .. code-block:: json

            ["name1", "name2", "name3"...]
    """
    return service.result(200, list(manager.stack.keys()))


@service.route('/pipelines/<pipeline_name>', methods=['GET'])
def get_pipeline(pipeline_name: str):
    """
    Get information about a pipeline.

    :Method: GET
    :Path: /pipelines/`pipeline_name`
    :param pipeline_name: the name of the pipeline to get information about.

    :Statuses: `200` on success.
    :Response:
        .. code-block:: json

            {
                "components": ["component1", "component2"...],
                "worker": {
                    "is_started": True,
                    "pending_tasks": 42,
                    "type": "relevance.worker.ThreadWorker"
                }
            }
    """
    pipeline = manager.resolve(pipeline_name)
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
    Get information about a pipeline's worker.

    :Method: GET
    :Path: /pipelines/`pipeline_name`/worker
    :param pipeline_name: the name of the pipeline to get information about.

    :Statuses: `200` on success.
    :Response:
        .. code-block:: json

            {
                "is_started": True,
                "pending_tasks": 42,
                "type": "relevance.worker.ThreadWorker"
            }
    """
    pipeline = manager.resolve(pipeline_name)
    result = {
        'is_started': pipeline.worker.is_started,
        'pending_tasks': pipeline.worker.scope.qsize(),
        'type': '{0}.{1}'.format(
            pipeline.worker.__class__.__module__,
            pipeline.worker.__class__.__name__,
        ),
    }
    return service.result(200, result)


@service.route('/pipelines/<pipeline_name>/components', methods=['GET'])
def get_pipeline_components(pipeline_name: str):
    """
    Get the list of components for a pipeline.

    :Method: GET
    :Path: /pipelines/`pipeline_name`/components
    :param pipeline_name: the name of the pipeline to get information about.

    :Statuses: `200` on success.
    :Response:
        .. code-block:: json

            ["component1", "component2"...]
    """
    pipeline = manager.resolve(pipeline_name)
    result = list(pipeline.components.keys())
    return service.result(200, result)


@service.route('/pipelines/<pipeline_name>/components/<component_name>', methods=['GET'])
def get_pipeline_component(pipeline_name: str, component_name: str):
    """
    Get information about a specific component in a pipeline.

    :Method: GET
    :Path: /pipelines/`pipeline_name`/components/`component_name`
    :param pipeline_name: the name of the pipeline to get information about.
    :param component_name: the name of the component to get information about.

    :Statuses: `200` on success.
    :Response:
        .. code-block:: json

            {
                "class": "relevance.pipeline.Extractor",
                "target": "mymodule.myfunc",
                "options": {
                    "url": "some param",
                },
                "worker": {
                    "is_started": True,
                    "pending_tasks": 42,
                    "type": "relevance.worker.ThreadWorker"
                }
            }
    """
    pipeline = manager.resolve(pipeline_name)
    component = pipeline.get(component_name)

    result = {
        'class': '{0}.{1}'.format(
            component.__class__.__module__,
            component.__class__.__name__,
        ),
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


@service.route('/pipelines/<pipeline_name>/worker', methods=['PUT'])
def start_pipeline_worker(pipeline_name: str):
    """
    Start a pipeline worker.

    :Method: PUT
    :Path: /pipelines/`pipeline_name`/worker
    :param pipeline_name: the name of the pipeline to start.

    :Statuses: 202 on success.
    :Response: same as :func:`get_pipeline`.
    """
    pipeline = manager.resolve(pipeline_name)
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

    :Method: DELETE
    :Path: /pipelines/`pipeline_name`/worker
    :param pipeline_name: the name of the pipeline to stop.

    :Statuses: 202 on success.
    :Response: same as :func:`get_pipeline`.
    """
    pipeline = manager.resolve(pipeline_name)
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


if __name__ == '__main__':
    import os
    service.run(port=int(os.getenv('PORT', 55346)), debug=True)
