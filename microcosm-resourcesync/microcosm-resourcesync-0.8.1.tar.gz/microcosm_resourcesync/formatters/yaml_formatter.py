"""
YAML Formatter

"""
from yaml import dump, load
try:
    from yaml import CSafeDumper as SafeDumper, CSafeLoader as SafeLoader
except ImportError:
    from yaml import SafeDumper, SafeLoader

from microcosm_resourcesync.formatters.base import Formatter


class YAMLFormatter(Formatter):

    def load(self, data):
        return load(data, Loader=SafeLoader)

    def dump(self, dct):
        return dump(
            dict(dct),
            # show every document in its own block
            default_flow_style=False,
            # start a new document (via "---") before every resource
            explicit_start=True,
            # follow (modern) PEP8 max line length and indent
            width=99,
            indent=4,
            Dumper=SafeDumper,
        )

    @property
    def extension(self):
        return ".yaml"

    @property
    def mime_types(self):
        return [
            "application/yaml",
            "application/x-yaml",
            "text/vnd.yaml",
            "text/yaml",
            "text/x-yaml",
        ]
