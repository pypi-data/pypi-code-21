"""
Relevance engine core.

This package provides a unified interface for interacting with the different storage
and search backends.
"""

import abc
import pydoc
import typing

from relevance import loggers
from relevance.settings import Settings
from relevance.query import Search
from relevance.facet import Facet
from relevance.mapping import Mapping
from relevance.document import Document
from relevance.document import ResultSet


# Logging
logger = loggers.getLogger('relevance.engine')


class EngineError(RuntimeError):
    """
    Exception class for engine errors.
    """
    pass


class MappingError(EngineError):
    """
    Exception class for mapping errors.
    """
    pass


class SearchError(EngineError):
    """
    Exception class for mapping errors.
    """
    pass


class IngestionError(EngineError):
    """
    Exception class for mapping errors.
    """
    pass


class Engine(object, metaclass=abc.ABCMeta):
    """
    Engine interface.

    Base interface for all engines.
    """
    def __init__(self, target: str, *, facets: typing.Dict[str, Facet]=None,
                 auto_filters: bool=True, **kwargs):
        """
        Initialize the engine.

        :param target: the storage engine target.
        :param facets: a dictionary of facets definitions.
        :param auto_filters: whether to enable automatic filter definitions.
        """
        logger.info('init', inst=self, target=target, auto_filters=auto_filters,
                    facets=facets)
        self.target = target
        self.facets = facets if facets is not None else {}
        self.auto_filters = auto_filters

    @abc.abstractmethod
    def search(self, search: Search) -> ResultSet:
        """
        Perform a search request on the engine.

        :param search: the request to execute.
        :returns: a result set object.
        """
        pass

    @abc.abstractmethod
    def start(self):
        """
        Start the engine.
        """
        pass

    @abc.abstractmethod
    def stop(self):
        """
        Stop the engine.
        """
        pass

    @abc.abstractmethod
    def get_doc_types(self) -> typing.List[str]:
        """
        Get a list of available document types.

        :returns: a list of document type strings.
        """
        pass

    @abc.abstractmethod
    def get_mapping(self, doc_type: str) -> Mapping:
        """
        Get the mapping object for a specific document type.

        :param doc_type: the document type.
        :returns: the mapping object.
        """
        pass

    @abc.abstractmethod
    def put_mapping(self, doc_type: str, mapping: Mapping):
        """
        Update the mapping for a specific document type.

        :param doc_type: the document type.
        :param mapping: the mapping object.
        """
        pass

    @abc.abstractmethod
    def publish(self, doc: Document) -> Document:
        """
        Index a document.

        :param doc: the document object to index.
        :returns: the updated, indexed document object.
        """
        pass

    @abc.abstractmethod
    def unpublish(self, schema: str, doc_type: str, uid: object):
        """
        Delete a document.

        :param schema: the document schema.
        :param doc_type: the document type.
        :param uid: the unique identifier for the document.
        """
        pass


class EngineFactory(object):
    """
    Factory for engines.
    """
    def load_facet(self, settings: Settings) -> Facet:
        cls_name = settings.get_type('class', data_type=str)
        field = settings.get('field', data_type=str)
        path = settings.get('path', data_type=str)
        options = settings.get('options', {}, data_type=dict)

        # locate the facet class
        cls = pydoc.locate(cls_name)
        if cls is None or not issubclass(cls, Facet):
            raise ImportError(cls_name)

        result = cls(field=field, path=path, **options)
        return result

    def load_all_facets(self, settings: Settings) -> typing.Dict[str, Facet]:
        result = {}
        for name, conf in settings.items():
            result[name] = self.load_facet(conf)
        return result

    def load_engine(self, settings: Settings) -> Engine:
        cls_name = settings.get_type('class', data_type=str)
        target = settings.get_type('target', data_type=str)
        options = settings.get('options', {}, data_type=dict)
        facets = settings.get('facets', {}, data_type=dict)

        # locate the engine class
        cls = pydoc.locate(cls_name)
        if cls is None or not issubclass(cls, Engine):
            raise ImportError(cls_name)

        # load the facets
        facets_map = self.load_all_facets(facets)

        result = cls(target, facets=facets_map, **options)
        return result

    def load_all_engines(self, settings: Settings) -> typing.Dict[str, Engine]:
        result = {}
        for name, conf in settings.items():
            result[name] = self.load_engine(conf)
        return result
