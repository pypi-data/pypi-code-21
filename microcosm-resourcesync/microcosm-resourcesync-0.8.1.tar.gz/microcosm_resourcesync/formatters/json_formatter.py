"""
JSON Formatter

"""
from json import dumps, loads

from microcosm_resourcesync.formatters.base import Formatter


class JSONFormatter(Formatter):

    def load(self, data):
        return loads(data)

    def dump(self, dct):
        # ensure deterministic output order for easier diffs
        return dumps(dct, sort_keys=True) + "\n"

    @property
    def extension(self):
        return ".json"

    @property
    def mime_types(self):
        return [
            "application/json",
            "text/json",
        ]
