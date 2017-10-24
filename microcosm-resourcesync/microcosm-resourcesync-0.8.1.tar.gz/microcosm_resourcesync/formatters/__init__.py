"""
Supported formatters

"""
from enum import Enum, unique

from microcosm_resourcesync.formatters.json_formatter import JSONFormatter
from microcosm_resourcesync.formatters.yaml_formatter import YAMLFormatter


@unique
class Formatters(Enum):
    JSON = JSONFormatter()
    YAML = YAMLFormatter()

    @classmethod
    def for_content_type(cls, content_type):
        for formatter in cls:
            if content_type in formatter.value.mime_types:
                return formatter

        raise Exception("Unsupported content type: {}".format(content_type))

    @classmethod
    def for_extension(cls, ext):
        for formatter in cls:
            if ext == formatter.value.extension:
                return formatter

        raise Exception("Unsupported extension: {}".format(ext))
