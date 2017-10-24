"""
Schema interface.

"""
from abc import ABCMeta, abstractmethod, abstractproperty
from collections import namedtuple
from six import add_metaclass


Link = namedtuple("Link", ["relation", "uri"])


@add_metaclass(ABCMeta)
class Schema(dict):
    """
    A schema wraps a dictionary and defines a `uri`, `id`, `type`, etc.

    """
    @property
    def id(self):
        """
        The dictionary is assumed to have an "id" attribute.

        """
        return self["id"]

    @abstractproperty
    def embedded(self):
        """
        The resource may contain embedded sources.

        This property is expected for paginated results.

        """
        pass

    @abstractmethod
    def links(self, follow_mode):
        """
        The resource should be able to extract appropriate `Links` for the `follow_mode`.

        """
        pass

    @abstractproperty
    def parents(self):
        """
        The resource may have parent resource URIs for topological sorting.

        """
        pass

    @abstractproperty
    def type(self):
        """
        The resource should have a string-valued type.

        """
        pass

    @abstractproperty
    def uri(self):
        """
        The resource should know its own URI.

        """
        pass
