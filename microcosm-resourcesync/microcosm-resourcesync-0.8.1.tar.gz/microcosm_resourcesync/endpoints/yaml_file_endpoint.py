"""
Read/write from a YAML file.

"""
from os import unlink
from os.path import dirname, exists

from click import ClickException
from yaml import safe_load_all

from microcosm_resourcesync.endpoints.base import Endpoint
from microcosm_resourcesync.formatters import Formatters


class YAMLFileEndpoint(Endpoint):
    """
    Read and write resources for a single YAML file.

    For small data sizes, using a single YAML file results in a well-encapsulated,
    human-readable endpoint. For large data sizes, a directory endpoint is recommended instead.

    """
    def __init__(self, path):
        self.path = path

    def __repr__(self):
        return "{}('{}')".format(
            self.__class__.__name__,
            self.path,
        )

    def __eq__(self, other):
        return self.__class__ == other.__class__ and self.path == other.path

    def read(self, schema_cls, **kwargs):
        """
        Read all YAML documents from the file.

        """
        with open(self.path) as file_:
            raw_resources = safe_load_all(file_)

            for raw_resource in raw_resources:
                yield schema_cls(raw_resource)

    def write(self, resources, formatter, remove=False, **kwargs):
        """
        Write resources as YAML to the file.

        """
        with open(self.path, "a") as file_:
            for resource in resources:
                file_.write(formatter.value.dump(resource))

    def validate_for_write(self, formatter, remove=False, **kwargs):
        # must use the correct formatter (JSON doesn't support multi-document files)
        if formatter != Formatters.YAML:
            raise ClickException("Cannot use {} format YAMLFileEndpoint".format(
                formatter.name
            ))

        # handle existing files
        if exists(self.path):
            if remove:
                # remove
                unlink(self.path)
            else:
                raise ClickException("File already exists: {}; perhaps you mean to use '--rm'?".format(
                    self.path,
                ))

        # create directories
        self.mkdir(dirname(self.path))
