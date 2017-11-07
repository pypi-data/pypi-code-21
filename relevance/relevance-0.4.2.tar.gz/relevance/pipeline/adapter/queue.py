"""
This pipeline adapter module exposes queues to be used as extractors or publishers.
They can be populated or retrieved via service routes.
"""

import pickle
from queue import Queue
from queue import Empty
from queue import Full
from werkzeug.exceptions import NotFound

from relevance.pipeline import Extractor
from relevance.pipeline import Publisher
from relevance.pipeline import Pipeline
from relevance.worker import Worker
from relevance.service import Service
from relevance.manager import ResourceNotFoundError


# Get the service instance
service = Service.instance('pipeline')


class QueueExtractor(Extractor):
    """
    This class exposes a queue object within a worker that can be used as an
    extractor. Items can be put in the queue via the service route.
    """
    def __init__(self, worker: Worker, size: int=0, timeout: float=0):
        """
        :param worker: the worker object for the extractor.
        :param size: the maximum size of the queue. Once the queue has been
            filled, further put calls will hang until there is room or the
            timeout is expired.
        :param timeout: a timeout, in seconds, after which requests to and
            from the queue expire and raise an exception.
        """
        self.queue = Queue(maxsize=size)
        self.timeout = timeout
        super().__init__(worker, self.queue.__class__)

    def __call__(self, pipeline: Pipeline) -> object:
        """
        Implementation of :meth:`Extractor.__call__`.
        """
        try:
            item = self.queue.get(timeout=self.timeout)
            self.queue.task_done()
        except Empty:
            return StopIteration()

        pipeline.trigger('item_extracted', item=item)
        return item

    def put(self, item: object):
        """
        Put an item in the queue.

        :param item: the item to put.
        :raises: :class:`queue.Full`: if the timeout specified in the initializer
            is reached when the queue is full.
        """
        self.queue.put(item, timeout=self.timeout)


@service.route('/pipelines/<pipeline_name>/components/<component_name>/queue',
               methods=['POST'])
def put_pipeline_queue_item(pipeline_name: str, component_name: str):
    """
    Put an item into an input queue.

    :Method: POST
    :Path: /pipelines/`pipeline_name`/components/`component_name`/queue
    :Headers: requires a proper `Content-Type` header to be set.
    :param pipeline_name: the name of the pipeline.
    :param pipeline_name: the name of the component.

    :Statuses: 201 on success.
    :Response:
        .. code-block:: json

            {
                "content_type": "application/json",
                "pending_tasks": 42,
                "size": 129
            }
    :raises: :class:`UnsupportedContentTypeError`: if the `Content-Type` header does
        not contain a supported mime type.
    """
    manager = service.data.manager

    try:
        pipeline = manager.resolve(pipeline_name)
    except KeyError as e:
        raise ResourceNotFoundError('pipeline', eval(str(e)))

    try:
        component = pipeline.get(component_name)
    except KeyError as e:
        raise ResourceNotFoundError('component', eval(str(e)))

    if not isinstance(component, QueueExtractor):
        raise NotFound()

    content_type = service.request.headers.get('Content-Type', 'text/plain')

    if content_type == 'text/plain':
        item = service.request.get_data()
    elif content_type == 'application/json':
        item = service.request.get_json()
    elif content_type == 'application/octet-stream':
        item = service.request.get_data()
        item = pickle.loads(item)
    else:
        raise UnsupportedContentTypeError(content_type)

    component.put(item)

    result = {
        'content_type': content_type,
        'pending_tasks': component.queue.qsize(),
        'size': len(pickle.dumps(item)),
    }
    return service.result(201, result)


class QueuePublisher(Publisher):
    """
    The queue publisher is a pipeline component implementation that allows a document to
    be published to an output queue.
    """
    def __init__(self, worker: Worker, size: int=0, timeout: float=0):
        """
        :param worker: the worker object for the publisher.
        :param size: the maximum size of the queue. Once the queue has been
            filled, further calls will hang until there is room or the
            timeout is expired.
        :param timeout: a timeout, in seconds, after which requests to and
            from the queue expire and raise an exception.
        """
        self.queue = Queue(maxsize=size)
        self.timeout = timeout
        super().__init__(worker, self.queue.__class__)

    def __call__(self, pipeline: Pipeline, item: object) -> object:
        """
        Implementation of :meth:`Extractor.__call__`.
        """
        try:
            self.queue.put(item, timeout=self.timeout)
        except Full:
            return StopIteration()

        pipeline.trigger('item_published', item=item)
        return item

    def get(self) -> object:
        """
        Get an item from the queue.

        :returns: the retrieved item.
        :raises: :class:`queue.Empty`: if the queue is empty and the timeout is
            reached.
        """
        return self.queue.get(timeout=self.timeout)


@service.route('/pipelines/<pipeline_name>/components/<component_name>/queue',
               methods=['GET'])
def get_pipeline_queue_item(pipeline_name: str, component_name: str):
    """
    Get an item from an output queue.

    :Method: GET
    :Path: /pipelines/`pipeline_name`/components/`component_name`/queue
    :Headers: requires a proper `Accept` header to be set.
    :param pipeline_name: the name of the pipeline.
    :param pipeline_name: the name of the component.

    :Statuses: 200 on success, 204 if the queue is empty.
    :Response: the raw document in the format specified by the `Accept` header.
    :raises: :class:`UnsupportedContentTypeError`: if the `Accept` header does
        not contain a supported mime type.
    """
    manager = service.data.manager

    try:
        pipeline = manager.resolve(pipeline_name)
    except KeyError as e:
        raise ResourceNotFoundError('pipeline', eval(str(e)))

    try:
        component = pipeline.get(component_name)
    except KeyError as e:
        raise ResourceNotFoundError('component', eval(str(e)))

    if not isinstance(component, QueuePublisher):
        raise NotFound()

    content_type = service.request.headers.get('Accept', 'text/plain')

    if content_type == 'text/plain':
        parser = None
    elif content_type == 'application/json':
        parser = None
    elif content_type == 'application/octet-stream':
        parser = pickle.dumps
    else:
        raise UnsupportedContentTypeError(content_type)

    try:
        item = component.get()
    except Empty:
        return service.result(204)

    if parser is not None:
        item = parser(item)

    return service.result(200, item)


class UnsupportedContentTypeError(TypeError):
    """
    This exception is raised when the specified mime type in the `Content-Type` or
    `Accept` header of a queue component request is not supported.
    """
    pass


@service.errorhandler(UnsupportedContentTypeError)
def _error_unsupported_content_type(e):
    """
    Handle :class:`UnsupportedContentTypeError` errors.
    """
    return service.result(415, {
        'error': {
            'type': e.__class__.__name__,
            'desc': 'the content type specified in the requested is not supported',
            'content_type': str(e),
        }
    })
