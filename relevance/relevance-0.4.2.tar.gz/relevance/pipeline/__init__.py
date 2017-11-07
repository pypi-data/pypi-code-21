"""
This package provides the utilities and interfaces needed to ingest content into a
search backend.
"""

import abc
import pydoc
import typing
import collections

from relevance import loggers
from relevance.worker import Worker
from relevance.worker import WorkerProxy
from relevance.worker import ThreadWorker
from relevance.manager import ResourceManager
from relevance.manager import ResourceExistsError
from relevance.manager import ResourceNotFoundError
from relevance.settings import Settings
from relevance.settings import InvalidSettingValueError


# Logging
logger = loggers.getLogger('relevance.pipeline')


class Component(WorkerProxy, metaclass=abc.ABCMeta):
    """
    The component class is a unit of a pipeline. A pipeline contains multiple components
    that have different roles, such as extracting content, post-processing it and
    publishing it to a queue or search backend. Components are isolated from one another
    and each have their own worker.
    """
    def __init__(self, worker: Worker, target: typing.Callable, **options):
        """
        :param worker: the worker object to wrap the component into.
        :param target: the component's callable. Most components are wrappers for
            existing functions. Whenever the data is ready, the target callable will
            be executed and the component will run.
        :param **options: the component's options. For simple callables, this is usually
            a dictionary of keyword arguments. If the component is a class, it would be
            a dictionary of keyword arguments to pass to the class initializer. For
            custom component implementations, it is component-specific.
        """
        super().__init__(worker)
        self.target = target
        self.options = options

    @abc.abstractmethod
    def __call__(self, pipeline: 'Pipeline', **kwargs) -> object:
        """
        Execute the component.

        This is the main entry point into the component.

        :param pipeline: the pipeline object in which the component is currently being
            executed.
        :param **kwargs: additional arguments to pass to the component at execution time.
        :returns: the result of the component execution.
        """
        kwargs.update(self.options)
        return self.target(**kwargs)


class Extractor(Component):
    """
    An extractor is a component that pulls content from a data source for further
    processing. Per example, it could be an in-memory queue, a message broker, a
    database or a web crawler.

    This implementation simply accepts a callable that will be executed at each run
    in the worker's event loop, pulling content (if available) at each iteration. If
    an item is available, the `item_extracted` signal will be sent to the pipeline with
    the extracted item.
    """
    def __call__(self, pipeline: 'Pipeline') -> object:
        """
        Implementation of :meth:`Component.__call__`.
        """
        item = super().__call__(pipeline)

        if isinstance(item, StopIteration):
            return item

        pipeline.trigger('item_extracted', item=item)
        return item


class Publisher(Component):
    """
    A publisher is a component that pushes content into a backend (such as a different
    queue, a database or a search backend) once it has finished processing.

    This implementation simply accepts a callable that will be executed whenever an
    `item_processed` signal is received. It then executes the callable, and triggers an
    `item_published` signal to the pipeline with the result of the publication.
    """
    def __call__(self, pipeline: 'Pipeline', item: object) -> object:
        """
        Implementation of :meth:`Component.__call__`.
        """
        result = super().__call__(pipeline, item=item)

        if isinstance(item, StopIteration):
            return item

        pipeline.trigger('item_published', item=item, result=result)
        return item


class Processor(Component):
    """
    A processor is a component that modifies the original document before publishing it.

    This implementation accepts a callable that is executed when a `item_extracted` signal
    is received. The callable is executed, the document is modified and an `item_processed`
    signal is broadcasted with the new version of the document.
    """
    def __call__(self, pipeline: 'Pipeline', item: object) -> object:
        """
        Implementation of :meth:`Component.__call__`.
        """
        item = super().__call__(pipeline, item=item)

        if isinstance(item, StopIteration):
            return item

        pipeline.trigger('item_processed', item=item)
        return item


class ProcessorStackMetaclass(abc.ABCMeta):
    """
    This metaclass is used by the processor stack wrapper class to collect the method
    objects to execute in the order they were defined.
    """
    @classmethod
    def __prepare__(metacls: type, name: str, bases: tuple, **kwds):
        """
        Prepare the class namespace.
        """
        return collections.OrderedDict()

    def __new__(cls: type, name: str, bases: tuple, namespace: dict, **kwds):
        """
        Create a new instance of the class.
        """
        result = type.__new__(cls, name, tuple(bases), dict(namespace))

        members = []
        for name, func in namespace.items():
            if hasattr(func, '__call__') and name[0] != '_':
                members.append(func)

        result.members = tuple(members)
        return result


class ProcessorStack(Processor, metaclass=ProcessorStackMetaclass):
    """
    The processor stack is a variant of the :class:`Processor` processor class, that
    allows a class to be executed as a processor rather than a callable. The processor
    stack basically checks all the public methods defined in the class and executes
    them in order. This is useful when a lot of different logic or code paths are
    necessary to process a document, to reduce bloat in the underlying code.
    """
    def __init__(self, worker: Worker):
        """
        :param worker: the worker object to wrap the component into.
        """
        super().__init__(worker, self)

    def __call__(self, pipeline: 'Pipeline', item: object) -> object:
        """
        Implementation of :meth:`Component.__call__`.
        """
        for x in self.members:
            result = x(self, item)

            if isinstance(result, StopIteration):
                return result

        if isinstance(result, StopIteration):
            return result

        pipeline.trigger('item_processed', item=item)
        return item


class Pipeline(WorkerProxy):
    """
    The pipeline class is responsible for managing and executing components. Like
    components, it proxies a worker object.
    """
    def __init__(self, *args, **kwargs):
        """
        :param worker: the worker object to wrap the pipeline into.
        """
        super().__init__(*args, **kwargs)
        self.components = {}

    def add(self, name: str, target: Component):
        """
        Add a component to the pipeline.

        :param name: the name to give the component.
        :param target: the component object.
        :raises: :class:`ResourceExistsError`: if a component of the same
            name already exists.
        """
        if target.worker is not self.worker:
            self.worker.add(target.worker)

        if name in self.components:
            raise ResourceExistsError(name)
        self.components[name] = target

        if isinstance(target, Extractor):
            self.worker.listen('loop_start', target, pipeline=self)
        if isinstance(target, Processor):
            self.worker.listen('item_extracted', target, pipeline=self)
        if isinstance(target, Publisher):
            self.worker.listen('item_processed', target, pipeline=self)

    def get(self, name: str) -> Component:
        """
        Get a component by its name.

        :param name: the name of the component.
        :returns: the component object.
        :raises: :class:`ResourceNotFoundError`: if a component of the specified
            name does not exist.
        """
        try:
            return self.components[name]
        except KeyError:
            raise ResourceNotFoundError(name)


class PipelineFactory(object):
    """
    The pipeline factory is responsible for creating pipeline and component objects
    from settings objects.
    """
    def __init__(self, worker_cls: type=ThreadWorker):
        """
        :param worker_cls: the worker class name.
        """
        self.worker_cls = worker_cls

    def load_component(self, settings: Settings) -> Component:
        """
        Load a component object from settings.

        :param settings: the settings object.
        :returns: the component object.
        :raises: :class:`ImportError`: when the component class, the target or the
            worker class is invalid.
        """
        cls_name = settings.get_type('class', data_type=str)
        target = settings.get('target', None, data_type=str)
        options = settings.get('options', {}, data_type=dict)
        worker_cls_name = settings.get('worker',
                                       '{0}.{1}'.format(
                                           self.worker_cls.__module__,
                                           self.worker_cls.__name__
                                       ),
                                       data_type=str)

        cls = pydoc.locate(cls_name)
        if cls is None or not issubclass(cls, Component):
            raise ImportError(cls_name)

        if target is not None:
            func = pydoc.locate(target)
            if func is None:
                raise ImportError(target)
            target = func

        worker_cls = pydoc.locate(worker_cls_name)
        if worker_cls is None or not issubclass(worker_cls, Worker):
            raise ImportError(worker_cls_name)

        worker = worker_cls()
        if target is not None:
            component = cls(worker, target, **options)
        else:
            component = cls(worker, **options)

        return component

    def load_all_components(self, settings: Settings) -> typing.Dict[str, Component]:
        """
        Load all component objects into a dictionary.

        :param settings: the settings object to load from.
        :returns: a dictionary of name and component object mappings.
        """
        result = {}
        for name, conf in settings.items():
            component = self.load_component(conf)
            result[name] = component
        return result

    def load_all(self, settings: Settings, manager: ResourceManager):
        """
        Load an entire configuration into a manager.

        :param settings: the settings object to load.
        :param manager: the manager object to load it into.
        :raises: :class:`ImportError`: when the pipeline class, or the worker
            classes are invalid.
        """
        worker_cls_name = settings.get('default_worker', None, data_type=str)
        if worker_cls_name is not None:
            worker_cls = pydoc.locate(worker_cls_name)
            if worker_cls is None or not issubclass(worker_cls, Worker):
                raise ImportError(worker_cls_name)
            self.worker_cls = worker_cls

        pipeline_cls_name = settings.get('pipeline_worker', None, data_type=str)
        if pipeline_cls_name is not None:
            pipeline_cls = pydoc.locate(pipeline_cls_name)
            if pipeline_cls is None or not issubclass(pipeline_cls, Worker):
                raise ImportError(pipeline_cls_name)
        else:
            pipeline_cls = self.worker_cls

        conf = settings.get('components', {}, data_type=dict)
        components = self.load_all_components(conf)

        for name, conf in settings.get('pipelines', {}, data_type=dict).items():
            pipeline = manager.new(name, pipeline_cls())

            for key, target in conf.items():
                try:
                    component = components[target]
                except KeyError:
                    raise InvalidSettingValueError(target)

                pipeline.add(key, component)
