"""Tools for obtaining data about lsstsw-installed packages."""

from __future__ import (division, absolute_import, print_function,
                        unicode_literals)
from builtins import *  # NOQA
from future.standard_library import install_aliases
install_aliases()  # NOQA


class Manifest(object):
    """lsstsw manifest.txt dataset."""
    def __init__(self, manifest_stream):
        super(Manifest, self).__init__()
        self._build_id = None
        self._packages = []

        self._parse_manifest_stream(manifest_stream)

    def _parse_manifest_stream(self, manifest_stream):
        for manifest_line in manifest_stream.readlines():
            manifest_line = manifest_line.strip()
            if manifest_line.startswith('#'):
                continue
            elif manifest_line.startswith('BUILD'):
                self._build_id = manifest_line.split('=')[-1]
                continue
            parts = manifest_line.split()
            package_name = parts[0]
            git_commit = parts[1]
            eups_version = parts[2]

            pkg_json = {
                'name': package_name,
                'git_commit': git_commit,
                'build_version': eups_version
            }
            self._packages.append(pkg_json)

    @property
    def json(self):
        """Job JSON as a `dict`, including the `packages` field."""
        return {'packages': self._packages}

    @property
    def build(self):
        """Build number (bNNNN)."""
        return self._build_id
