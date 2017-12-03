"""
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
logger = loggers.getLogger('relevance.engine')  # pylint: disable=invalid-name


class Engine(object, metaclass=abc.ABCMeta):
    """
    This is the interface for search engines. Implementing this interface allows
    a search engine to be queried and documents to be indexed to it.
    """
    def __init__(self, target: str, *, facets: typing.Dict[str, Facet] = None,  # pylint: disable=unused-argument
                 auto_filters: bool = True, **kwargs) -> None:
        """
        :param target: the storage engine target, typically a URL or DSN.
        :param facets: a dictionary of facets definitions. The key is the how the
            facet will be named when queried, the value is a :class:`.facet.Facet`
            object.
        :param auto_filters: whether to enable automatic filter definitions. When
            enabled, if a facet has not been defined, and one is specified in the
            search request, whether as a filter or in the returned facets list,
            it is assumed to be a :class:`.facet.TermFacet`. Even when enabled,
            undefined facets will not be returned by default, and will have to
            be specified manually in the search request. When disabled, specifying
            an undefined facet in a request will raise a
            :class:`.facet.FacetNotDefinedError`.
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

        An implementation of this method should accept a search object, and return
        a result set object on completion.

        :param search: the request to execute.
        :return: a result set object.
        """
        pass

    @abc.abstractmethod
    def get_doc_types(self) -> typing.List[str]:
        """
        Get a list of available document types.

        Most engines can support multiple "document types". For more database-like
        engines, this could be a table name or an object type.

        :return: a list of document type strings supported by the engine.
        """
        pass

    @abc.abstractmethod
    def get_mapping(self, doc_type: str) -> Mapping:
        """
        Get the mapping object for a specific document type.

        Given a specific document type as argument, this method should construct a
        :class:`.mapping.Mapping` object from :class:`.mapping.Field` objects and
        return it based on the mapping in the search backend.

        :param doc_type: the document type.
        :return: the mapping object.
        """
        pass

    @abc.abstractmethod
    def put_mapping(self, doc_type: str, mapping: Mapping):
        """
        Update the mapping for a specific document type.

        Calling this method should update the mapping on the search backend.

        :param doc_type: the document type.
        :param mapping: the mapping object.
        """
        pass

    @abc.abstractmethod
    def publish(self, doc: Document) -> Document:
        """
        Index a document.

        This method should return a copy of the original document, with auto fields
        (e.g.: id) populated automatically.

        :param doc: the document object to index.
        :return: the updated, indexed document object.
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

    def start(self):
        """
        Start the engine.

        Some backends are not stateless and require setup and teardown. The setup part
        can be implemented here.
        """
        pass

    def stop(self):
        """
        Stop the engine.

        Some backends are not stateless and require setup and teardown. The teardown part
        can be implemented here.
        """
        pass


class EngineFactory(object):
    """
    This factory class allows to create :class:`Engine` objects from :class:`.settings.Settings`
    objects.
    """
    def load_facet(self, settings: Settings) -> Facet:  # pylint: disable=no-self-use
        """
        Obtain a facet object from settings.

        :param settings: the settings object to load.
        :return: the facet object.
        :raises: :class:`ImportError`: if the facet class is invalid.
        """
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
        """
        Obtain a mapping of facets from settings.

        :param settings: the settings object to load.
        :return: a dicionary of facets. It can then be passed directly to the
            :class:`Engine` initializer.
        """
        result = {}
        for name, conf in settings.items():
            result[name] = self.load_facet(conf)
        return result

    def load_engine(self, settings: Settings) -> Engine:
        """
        Obtain an engine object from settings.

        :param settings: the settings object to load.
        :return: the engine object.
        :raises: :class:`ImportError`: if the engine class is invalid.
        """
        cls_name = settings.get_type('class', data_type=str)
        target = settings.get_type('target', data_type=str)
        options = settings.get('options', {}, data_type=dict)
        facets = settings.get('facets', {}, data_type=dict)

        # locate the engine class
        cls = pydoc.locate(cls_name)
        if cls is None or not issubclass(cls, Engine):
            raise ImportError(cls_name)

        # load the facets
        facets_map = self.load_all_facets(facets)  # type: ignore

        result = cls(target, facets=facets_map, **options)
        return result

    def load_all_engines(self, settings: Settings) -> typing.Dict[str, Engine]:
        """
        Obtain a mapping of engine objects.

        :param settings: the settings object to load.
        :return: a dictionary object mapping the engine objects to names. This can
            then be fed into a :class:`.manager.ResourceManager` object.
        """
        result = {}
        for name, conf in settings.items():
            result[name] = self.load_engine(conf)
        return result


class EngineError(RuntimeError):
    """
    This is the base exception class when an engine encounters an error.
    """
    pass


class SearchError(EngineError):
    """
    This exception type is raised when an error occurs trying to execute a search
    request.
    """
    pass


class MappingError(EngineError):
    """
    This exception type is raised when trying to get or update mapping in a
    search backend and an error occurs.
    """
    pass


class IngestionError(EngineError):
    """
    This exception type is raised when an error occurs trying to publish or unpublish
    documents in a search backend.
    """
    pass
