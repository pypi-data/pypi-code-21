"""
tmpld.cli.loaders
~~~~~~~~~~~~~~

Loader types and actions for argparse.

:copyright: (c) 2017 by Joe Black.
:license: Apache2.
"""

import io
import argparse
import json

import yaml

from . import util
from ..core import template


class DataDict(argparse.Action):
    def __call__(self, parser, namespace, values, option_string=None):
        self._ensure_default(namespace)
        self._add_item(namespace, values)


    @staticmethod
    def _load_item(file):
        """Should return a tuple of key, data.

        In this implementation, the key is the slug of the filename, while data
        is the deserialized contents of the file.
        """
        extension = util.get_file_extension(file.name)
        if extension in ('json', 'js'):
            return JsonLoader()(file)
        elif extension in ('yaml', 'yml'):
            return YamlLoader()(file)
        else:
            return TextLoader()(file)

    def _ensure_default(self, namespace):
        if not getattr(namespace, self.dest):
            setattr(namespace, self.dest, {})

    def _add_item(self, namespace, item):
        key, data = self._load_item(item)
        getattr(namespace, self.dest)[key] = data


class TemplateLoader(argparse.FileType):
    def __call__(self, file):
        return template.Template(file)


class YamlLoader(argparse.FileType):
    def __init__(self, Loader=yaml.loader.SafeLoader, **kwargs):
        argparse.FileType.__init__(self, **kwargs)
        self.Loader = Loader

    def __call__(self, file):
        if not isinstance(file, io.IOBase):
            file = argparse.FileType.__call__(self, file)

        slug = util.slugify_path(file.name)
        data = yaml.load(file, Loader=self.Loader)
        file.close()
        return slug, data


class JsonLoader(argparse.FileType):
    def __init__(self, cls=None, object_hook=None, object_pairs_hook=None,
                 **kwargs):
        argparse.FileType.__init__(self, **kwargs)
        self.cls = cls
        self.object_hook = object_hook
        self.object_pairs_hook = object_pairs_hook

    def __call__(self, file):
        if not isinstance(file, io.IOBase):
            file = argparse.FileType.__call__(self, file)

        slug = util.slugify_path(file.name)
        data = json.load(file,
                         cls=self.cls,
                         object_hook=self.object_hook,
                         object_pairs_hook=self.object_pairs_hook)
        file.close()
        return slug, data


class TextLoader(argparse.FileType):
    def __call__(self, file):
        if not isinstance(file, io.IOBase):
            file = argparse.FileType.__call__(self, file)

        slug = util.slugify_path(file.name)
        data = file.read()
        file.close()
        return slug, data
