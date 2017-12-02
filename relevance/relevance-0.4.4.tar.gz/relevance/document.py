"""
Relevance document module.

This module provides the interface for representing documents, search results, and
result sets.
"""

import typing
import datetime


class Document(dict):
    """
    Document class.

    This class represents a document that can be searched for or indexed using an engine
    implementation. Documents are dictionaries with a schema name, a type and a unique
    identifier attached.
    """
    def __init__(self, schema: str, doc_type: str, uid: object) -> None:
        """
        Initialize the document.

        :param schema: the document schema, typically an index name.
        :param doc_type: the document type, usually a table name or similar.
        :param uid: a unique identifier for this document.
        """
        super().__init__()
        self.schema = schema
        self.doc_type = doc_type
        self.uid = uid

    def __eq__(self, other: object):
        """
        Overload operator for comparison.

        Documents are considered equal if they have the same content, document type and
        unique identifier.
        """
        return (
            dict(self) == dict(other) and  # type: ignore
            self.uid == other.uid and  # type: ignore
            self.doc_type == other.doc_type  # type: ignore
        )


class Result(Document):
    """
    Result class.

    This class provides the interface for handling single search results. Results are
    documents that are returned by a search query. They have the same attributes as
    documents with an extra relevancy score attached to them.
    """
    def __init__(self, *args, score: float) -> None:
        """
        Initialize the result.

        :param score: the relevancy score returned from the query result.
        """
        super().__init__(*args)
        self.score = score


class ResultSet(list):
    """
    Result set class.

    This class provides the interface for handling search result lists. Result sets
    are basically list of documents with some additional information such as a
    dictionary of facets and a number of total matches in the schema.
    """
    def __init__(self) -> None:
        """
        Initialize the result set.
        """
        super().__init__()
        self.time_start = datetime.datetime.now()
        self.time_end = None
        self.facets: typing.Dict[str, dict] = None
        self.total_count = 0

    @property
    def time(self) -> float:
        """
        Get the total amount of time the request took.
        """
        if self.time_end is None:
            return 0
        return (self.time_end - self.time_start).total_seconds()  # type: ignore
