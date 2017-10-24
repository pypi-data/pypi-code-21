"""
Formatter interface

"""
from abc import ABCMeta, abstractmethod, abstractproperty
from six import add_metaclass


@add_metaclass(ABCMeta)
class Formatter(object):
    """
    A format encodes a resource to/from a dictionary.

    """
    @abstractmethod
    def load(self, data):
        """
        Load input data into a dictionary.

        """
        pass

    @abstractmethod
    def dump(self, dct):
        """
        Dump a resource dictionary into encoded data.

        """
        pass

    @abstractproperty
    def mime_types(self):
        """
        A list of legal mime types.

        The first type should be the preferred mime type.

        """
        pass

    @abstractproperty
    def extension(self):
        """
        Return the default file extension for this format.

        """
        pass

    @property
    def preferred_mime_type(self):
        return self.mime_types[0]
