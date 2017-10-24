"""
Read/write from stdin/stdout

"""
from sys import stdin, stdout

from yaml import safe_load_all

from microcosm_resourcesync.endpoints.base import Endpoint


class PipeEndpoint(Endpoint):

    def __repr__(self):
        return "{}()".format(
            self.__class__.__name__,
        )

    def __eq__(self, other):
        # NB: allows origin to equal destination
        return False

    def read(self, schema_cls, **kwargs):
        raw_resources = safe_load_all(stdin)

        for raw_resource in raw_resources:
            yield schema_cls(raw_resource)

    def write(self, resources, formatter, **kwargs):
        """
        Write resources as YAML to the file.

        """
        for resource in resources:
            stdout.write(formatter.value.dump(resource))
