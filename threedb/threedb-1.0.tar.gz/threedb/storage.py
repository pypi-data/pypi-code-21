
from os.path import join, exists, basename
from .filter import SetFilter
from .config import Config
from .utils import *
import json
import yaml
import os
import re


METADATA = "metadata.yaml"


def _read_tags(metadata):
    if exists(metadata):
        with open(metadata, "r") as fd:
            metadata = yaml.load(fd)
            tags = metadata["tags"]
            return tags


class DataItem:

    def __init__(self, root, fp):
        self._root = root
        self._fp = fp

    def _handler(self):
        return open(join(self._root, self._fp), 'r')

    @property
    def text(self):
        return self._handler().read()

    def json(self):
        return json.load(self._handler())


class Record(dict):

    def __init__(self, index, ref, tags, **data):
        super(Record, self).__init__(self)
        self["index"] = index
        self["ref"] = ref
        self["tags"] = tags or []
        self.update((field, DataItem(ref, data[field])) for field in data)

    @property
    def index(self):
        return self["index"]

    @property
    def tags(self):
        return self["tags"]

    @property
    def ref(self):
        return self["ref"]

Element = Record


class _BaseStorage:

    def __init__(self, storage_path, schema=None):
        self._storage_path = storage_path
        self._schema = schema


class SimpleStorage(_BaseStorage):

    def __init__(self, *args, **kwargs):
        _BaseStorage.__init__(self, *args, **kwargs)

    def _impose_scheme(self, root, files):
        res = {}
        if self._schema:
            for field in self._schema:
                p = "|".join(self._schema[field]["match"])
                for file in files:
                    data_fields = re.findall(p, file)
                    if data_fields:
                        res[field] = data_fields[0]
                        break
        else:
            res = dict((file.replace(".", "_"), file) for file in files)
        return res

    def read(self):
        records = []
        for root, _, files in os.walk(self._storage_path):
            if files:
                fields = self._impose_scheme(root, files)

                elem = Element(
                    index=basename(root),
                    ref=root,
                    tags=_read_tags(join(root, METADATA)),
                    **fields
                )

                records.append(elem)
        return records

simple_storage = SimpleStorage


class ThreeDB:

    def __init__(self, path, config=None, schema=None,
                 storage_type=simple_storage):
        self._config = config or Config()
        self._path = path
        self._schema = schema or self._config.get("schema")
        self._storage = storage_type(self._path, schema=self._schema)
        self._filter = SetFilter()

    def search(self, strict=False, *tags):
        records = self._storage.read()
        if not tags:
            return records
        return self._filter.apply_filter(records, strict, tags)


connect = ThreeDB
