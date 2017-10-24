"""
Endpoint interface

"""
from microcosm_resourcesync.endpoints.base import Endpoint


class NullEndpoint(Endpoint):

    def read(self, schema_cls, **kwargs):
        """
        Generate resources of the given schema.

        """
        return []

    def write(self, resources, formatter, **kwargs):
        """
        Write resources using the given formatter.

        """
        pass

    def __repr__(self):
        return "{}()".format(
            self.__class__.__name__,
        )
