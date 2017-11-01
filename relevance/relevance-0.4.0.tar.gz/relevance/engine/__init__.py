"""
Relevance engine core.

This package provides a unified interface for interacting with the different storage
and search backends.
"""

import abc
import typing
import logging

from relevance.query import Search
from relevance.facet import Facet
from relevance.mapping import Mapping
from relevance.document import Document
from relevance.document import ResultSet


# Logging
logger = logging.getLogger('relevance.engine')


class EngineError(RuntimeError):
    """
    Exception class for engine errors.
    """
    pass


class Engine(object, metaclass=abc.ABCMeta):
    """
    Engine interface.

    Base interface for all engines.
    """
    def __init__(self, target: str):
        """
        Initialize the engine.

        :param target: the engine target (url, etc.).
        """
        self.target = target

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


class MappingError(RuntimeError):
    """
    Exception class for mapping errors.
    """
    pass


class MappingEngine(Engine, metaclass=abc.ABCMeta):
    """
    Abstract class for engines that support mapping.

    This class provides the interface for storage and search engines to support
    mapping definitions.
    """
    def __init__(self, target: str, **kwargs):
        """
        Initialize the engine.

        :param target: the storage engine target.
        """
        logger.info('initialize mapping engine {0} at {1}'.format(
            self, target,
        ))
        self.target = target

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


class SearchError(RuntimeError):
    """
    Exception class for mapping errors.
    """
    pass


class SearchEngine(Engine, metaclass=abc.ABCMeta):
    """
    Search Engine abstract class.

    This class provides the abstract interface for storage engines to implement search
    functionality.
    """
    def __init__(self, target: str, *, facets: typing.Dict[str, Facet]=None,
                 auto_filters: bool=True, **kwargs):
        """
        Initialize the engine.

        :param target: the storage engine target.
        :param facets: a dictionary of facets definitions.
        :param auto_filters: whether to enable automatic filter definitions.
        """
        logger.info('initialize search engine {0} at {1}, auto_filters={2}, facets={3}'.format(
            self, target, int(auto_filters), facets,
        ))
        super().__init__(target)
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


class IngestionError(RuntimeError):
    """
    Exception class for ingestion errors.
    """
    pass


class IngestionEngine(Engine, metaclass=abc.ABCMeta):
    """
    Ingestion Engine abstract class.

    This class provides the abstract interface for storage engines to implement indexing
    functionality.
    """
    def __init__(self, target: str, **kwargs):
        """
        Initialize the engine.

        :param target: the storage engine target.
        """
        logger.info('initialize ingestion engine {0} at {1}'.format(
            self, target,
        ))
        super().__init__(target)

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
