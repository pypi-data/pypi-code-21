"""
tmpld.core.frontmatter
~~~~~~~~~~~~~~

YAML Frontmatter loader for tmpld.

:copyright: (c) 2017 by Joe Black.
:license: Apache2.
"""

import yaml

from . import util

class FrontMatterFile:
    def __init__(self, file):
        self.file = file
        self._load_file(self.file)

    def _load_file(self, file):
        with util.smart_open(file, 'rt') as fd:
            self.metadata = self._parse_metadata(fd)
            self.content = fd.read().lstrip()

    @staticmethod
    def _parse_metadata(fd):
        pointer = fd.tell()
        line = fd.readline()
        if line != '---\n':
            fd.seek(pointer)
            return {}
        lines = []
        for line in fd:
            if line != '---\n':
                lines.append(line)
            else:
                lines = ''.join(lines)
                return yaml.load(lines) or {}

    def print(self, as_string=False):
        contents = self.content.strip() + '\n'
        if as_string:
            return contents
        else:
            print(contents)
