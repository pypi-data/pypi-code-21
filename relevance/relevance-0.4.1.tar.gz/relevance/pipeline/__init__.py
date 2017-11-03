"""
Relevance pipeline package.
"""

import abc
import pydoc
import typing
import collections

from relevance import loggers
from relevance.worker import Worker
from relevance.worker import WorkerProxy
from relevance.worker import ThreadWorker
from relevance.settings import Settings
from relevance.settings import InvalidSettingValueError


# Logging
logger = loggers.getLogger('relevance.pipeline')


class ComponentExistsError(NameError):
    """
    Exception raised when a proxy with that name already exists in the pipeline.
    """
    pass


class PipelineExistsError(NameError):
    """
    Exception raised when a proxy with that name already exists in the pipeline.
    """
    pass


class Component(WorkerProxy, metaclass=abc.ABCMeta):
    """
    Pipeline component interface.
    """
    def __init__(self, worker: Worker, target: typing.Callable, **options):
        """
        Initialize the component.

        :param target: the component's callable target.
        """
        super().__init__(worker)
        self.target = target
        self.options = options

    @abc.abstractmethod
    def __call__(self, pipeline: 'Pipeline', **kwargs) -> object:
        """
        Execute the component.

        :param: the pipeline object.
        :returns: the execution result.
        """
        kwargs.update(self.options)
        return self.target(**kwargs)


class Extractor(Component):
    """
    Extractor component.
    """
    def __call__(self, pipeline: 'Pipeline') -> object:
        """
        Extract an item and return it.
        """
        item = super().__call__(pipeline)

        if isinstance(item, StopIteration):
            return item

        pipeline.trigger('item_extracted', item=item)
        return item


class Publisher(Component):
    """
    Publisher component.
    """
    def __call__(self, pipeline: 'Pipeline', item: object) -> object:
        """
        Publish an item.
        """
        result = super().__call__(pipeline, item=item)

        if isinstance(item, StopIteration):
            return item

        pipeline.trigger('item_published', item=item, result=result)
        return item


class Processor(Component):
    """
    Processor component.
    """
    def __call__(self, pipeline: 'Pipeline', item: object) -> object:
        """
        Process an item.
        """
        item = super().__call__(pipeline, item=item)

        if isinstance(item, StopIteration):
            return item

        pipeline.trigger('item_processed', item=item)
        return item


class ProcessorStackMetaclass(abc.ABCMeta):
    """
    Processor wrapper metaclass.

    This metaclass is used by the processor wrapper class to collect the method
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
    Processor wrapper class.

    This class allows a content processor to be defined as a class rather than
    a function, and make use of inheritance.
    """
    def __init__(self, worker: Worker):
        """
        Initialize the component.
        """
        super().__init__(worker, self)

    def __call__(self, pipeline: 'Pipeline', item: object) -> object:
        """
        Execute the processor.

        :param item: the input item.
        :returns: the processed item.
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
    Pipeline class.
    """
    def __init__(self, *args, **kwargs):
        """
        Initialize the pipeline.
        """
        super().__init__(*args, **kwargs)
        self.components = {}

    def add(self, name: str, target: Component):
        """
        Add a component to the pipeline.

        :param name: the name to give the component.
        :param target: the component object.
        """
        if target.worker is not self.worker:
            self.worker.add(target.worker)

        self.components[name] = target

        if isinstance(target, Extractor):
            self.worker.listen('loop_start', target, pipeline=self)
        if isinstance(target, Processor):
            self.worker.listen('item_extracted', target, pipeline=self)
        if isinstance(target, Publisher):
            self.worker.listen('item_processed', target, pipeline=self)

    def get(self, name: str) -> Component:
        """
        Get a component by name.

        :param name: the name of the component.
        :returns: the component object.
        """
        return self.components[name]


class PipelineManager(object):
    """
    Manager class for pipelines.
    """
    def __init__(self):
        """
        Initialize the manager.
        """
        self.stack = {}

    def new(self, name: str, worker: Worker) -> Pipeline:
        """
        Create a new pipeline in the manager.

        :param name: the name to give the pipeline.
        :param worker: the worker object for the pipeline.
        :returns: a pipeline object.
        """
        if name in self.stack:
            raise PipelineExistsError(name)

        logger.info('new', manager=self, worker=worker, name=name)
        pipeline = Pipeline(worker)
        self.stack[name] = pipeline
        return pipeline

    def resolve(self, name: str) -> Pipeline:
        """
        Get an existing pipeline object.

        :param name: the name of the pipeline.
        :returns: the pipeline object.
        """
        return self.stack[name]


class PipelineFactory(object):
    """
    Factory class for pipelines.
    """
    def __init__(self, manager: PipelineManager, worker_cls: type=ThreadWorker):
        """
        Initialize the factory.

        :param manager: the manager object.
        :param worker_cls: the worker class name.
        """
        self.manager = manager
        self.worker_cls = worker_cls

    def load_component(self, settings: Settings) -> Component:
        """
        Load a component object from settings.

        :param settings: the settings object.
        :returns: the component object.
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
            raise InvalidSettingValueError(cls_name)

        if target is not None:
            func = pydoc.locate(target)
            if func is None:
                raise InvalidSettingValueError(target)
            target = func

        worker_cls = pydoc.locate(worker_cls_name)
        if worker_cls is None or not issubclass(worker_cls, Worker):
            raise InvalidSettingValueError(worker_cls_name)

        worker = worker_cls()
        if target is not None:
            component = cls(worker, target, **options)
        else:
            component = cls(worker, **options)

        return component

    def load_all_components(self, settings: Settings) -> typing.Dict[str, Component]:
        """
        Load all component objects.

        :param settings: the settings object.
        :returns: a dictionary of name and component object mappings.
        """
        result = {}
        for name, conf in settings.items():
            component = self.load_component(conf)
            result[name] = component
        return result

    def load_all(self, settings: Settings):
        """
        Load the entire configuration into the manager.

        :param settings: the settings object to load.
        """
        worker_cls_name = settings.get('default_worker', None, data_type=str)
        if worker_cls_name is not None:
            worker_cls = pydoc.locate(worker_cls_name)
            if worker_cls is None or not issubclass(worker_cls, Worker):
                raise InvalidSettingValueError(worker_cls_name)
            self.worker_cls = worker_cls

        pipeline_cls_name = settings.get('pipeline_worker', None, data_type=str)
        if pipeline_cls_name is not None:
            pipeline_cls = pydoc.locate(pipeline_cls_name)
            if pipeline_cls is None or not issubclass(pipeline_cls, Worker):
                raise InvalidSettingValueError(pipeline_cls_name)
        else:
            pipeline_cls = self.worker_cls

        conf = settings.get('components', {}, data_type=dict)
        components = self.load_all_components(conf)

        for name, conf in settings.get('pipelines', {}, data_type=dict).items():
            pipeline = self.manager.new(name, pipeline_cls())

            for key, target in conf.items():
                try:
                    component = components[target]
                except KeyError:
                    raise InvalidSettingValueError(target)

                pipeline.add(key, component)
