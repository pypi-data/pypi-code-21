"""
Endpoint interface

"""
from abc import ABCMeta, abstractmethod
from os import makedirs
from six import add_metaclass

from microcosm_resourcesync.formatters import Formatters


@add_metaclass(ABCMeta)
class Endpoint(object):
    """
    An endpoint is able to read and write resources.

    """
    @property
    def default_formatter(self):
        """
        The default formatter to use for this endpoint.

        """
        return Formatters.YAML.name

    @abstractmethod
    def read(self, schema_cls, **kwargs):
        """
        Generate resources of the given schema.

        """
        pass

    @abstractmethod
    def write(self, resources, formatter, **kwargs):
        """
        Write resources using the given formatter.

        """
        pass

    def validate_for_read(self, schema_cls, **kwargs):
        """
        Validate that reading is possible.

        """
        pass

    def validate_for_write(self, formatter, **kwargs):
        """
        Validate that writing is possible.

        """
        pass

    def mkdir(self, path):
        # create directories
        try:
            makedirs(path)
        except OSError:
            pass
