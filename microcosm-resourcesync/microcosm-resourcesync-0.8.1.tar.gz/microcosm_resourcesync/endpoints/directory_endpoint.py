"""
Read/write from a directory tree.

"""
from os import walk
from os.path import exists, isdir, join, splitext
from shutil import rmtree

from click import ClickException

from microcosm_resourcesync.endpoints.base import Endpoint
from microcosm_resourcesync.formatters import Formatters


class DirectoryEndpoint(Endpoint):
    """
    Read and write resources for a single directory tree.

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
        Read all YAML documents from the directory.

        """
        for dirpath, dirnames, filenames in walk(self.path):
            for filename in filenames:
                if filename.startswith("."):
                    continue
                _, ext = splitext(filename)
                formatter = Formatters.for_extension(ext).value
                with open(join(dirpath, filename), "r") as file_:
                    data = file_.read()
                    dct = formatter.load(data)
                    yield schema_cls(dct)

    def write(self, resources, formatter, remove=False, **kwargs):
        """
        Write resources to the directory tree.

        """
        for resource in resources:
            assert resource.type is not None
            assert resource.id is not None

            dirname = join(self.path, resource.type)
            basename = "{}{}".format(resource.id, formatter.value.extension)
            self.mkdir(dirname)
            path = join(dirname, basename)
            with open(path, "w") as file_:
                file_.write(formatter.value.dump(resource))

    def validate_for_read(self, schema_cls, **kwargs):
        if not exists(self.path) or not isdir(self.path):
            raise ClickException("Not such directory: {}".format(self.path))

    def validate_for_write(self, formatter, remove=False, **kwargs):
        if exists(self.path) and not isdir(self.path):
            raise ClickException("Not a directory: {}".format(self.path))

        if exists(self.path) and remove:
            # remove tree
            rmtree(self.path)
