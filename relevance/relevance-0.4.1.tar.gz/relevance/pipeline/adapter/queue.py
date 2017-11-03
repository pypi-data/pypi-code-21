"""
Relevance queue pipeline module.
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
from relevance.service import ResourceNotFoundError


# Get the service instance
service = Service.instance('pipeline')
manager = service.data.manager


class UnsupportedContentTypeError(TypeError):
    """
    Exception raised when an unsupoorted content type is requested.
    """
    pass


class QueueExtractor(Extractor):
    """
    Extractor for queues.
    """
    def __init__(self, worker: Worker, size: int=0, timeout: float=0):
        """
        Initialize the extractor.

        :param size: the maximum size of the queue.
        """
        self.queue = Queue(maxsize=size)
        self.timeout = timeout
        super().__init__(worker, self.queue.__class__)

    def __call__(self, pipeline: Pipeline) -> object:
        """
        Execute the extractor.
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
        """
        self.queue.put(item, timeout=self.timeout)


@service.route('/pipelines/<pipeline_name>/components/<component_name>/queue',
               methods=['POST'])
def put_pipeline_queue_item(pipeline_name: str, component_name: str):
    """
    Push an item into the pipeline queue.
    """
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
    Extractor for queues.
    """
    def __init__(self, worker: Worker, size: int=0, timeout: float=0):
        """
        Initialize the extractor.

        :param size: the maximum size of the queue.
        """
        self.queue = Queue(maxsize=size)
        self.timeout = timeout
        super().__init__(worker, self.queue.__class__)

    def __call__(self, pipeline: Pipeline, item: object) -> object:
        """
        Execute the extractor.
        """
        try:
            self.queue.put(item, timeout=self.timeout)
        except Full:
            return StopIteration()

        pipeline.trigger('item_published', item=item)
        return item

    def get(self, timeout: float=0) -> object:
        """
        Put an item in the queue.
        """
        return self.queue.get(timeout=self.timeout)


@service.route('/pipelines/<pipeline_name>/components/<component_name>/queue',
               methods=['GET'])
def get_pipeline_queue_item(pipeline_name: str, component_name: str):
    """
    Get an item from the pipeline queue.
    """
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


@service.errorhandler(UnsupportedContentTypeError)
def error_unsupported_content_type(e):
    return service.result(415, {
        'error': {
            'type': e.__class__.__name__,
            'desc': 'the content type specified in the requested is not supported',
            'content_type': str(e),
        }
    })
