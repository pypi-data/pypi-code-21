"""Tools for working with lsstsw installations."""

from __future__ import (division, absolute_import, print_function,
                        unicode_literals)
from builtins import *  # NOQA
from future.standard_library import install_aliases
install_aliases()  # NOQA
from past.builtins import basestring

import os
import git
import yaml

from .pkgdata import Manifest


class Lsstsw(object):
    """An lsstsw installation.

    Parameters
    ----------
    dirname : `str`
        Path of an ``lsstsw`` directory.
    """
    def __init__(self, dirname, probe_git=True):
        super(Lsstsw, self).__init__()
        self._dirname = dirname
        self._load_repos_yaml()
        self._probe_git = probe_git

    @property
    def manifest_path(self):
        """Path of the manifest.txt file."""
        return os.path.join(self._dirname, 'build', 'manifest.txt')

    def package_repo_path(self, package_name):
        """Path to a EUPS package repository in lsstsw/build."""
        return os.path.join(self._dirname, 'build', package_name)

    def package_branch(self, package_name):
        """Git branch of an EUPS package cloned in lsstsw/build."""
        repo = git.Repo(self.package_repo_path(package_name))
        return repo.active_branch.name

    def package_repo_url(self, package_name):
        """URL of the package's Git repository.

        This data is obtained from lsstsw/etc/repos.yaml.
        """
        s = self._repos[package_name]
        if isinstance(s, basestring):
            return s
        else:
            # For packages that have sub-documents, rather than the value
            # as the URL. See repos.yaml for format documentation.
            return s['url']

    @property
    def json(self):
        """Job JSON document, as a `dict` containing a `packages` field."""
        with open(self.manifest_path, encoding='utf-8') as f:
            manifest = Manifest(f)
        job_json = manifest.json

        # Insert git branch information
        for pkg_doc in job_json['packages']:
            if self._probe_git:
                pkg_doc['git_branch'] = self.package_branch(pkg_doc['name'])
            else:
                pkg_doc['git_branch'] = 'unknown'

        # Insert git repo URLs
        for pkg_doc in job_json['packages']:
            pkg_doc['git_url'] = self.package_repo_url(pkg_doc['name'])

        return job_json

    def _load_repos_yaml(self):
        """Load lsstsw's repos.yaml."""
        yaml_path = os.path.join(self._dirname, 'etc', 'repos.yaml')
        with open(yaml_path) as f:
            self._repos = yaml.safe_load(f)
