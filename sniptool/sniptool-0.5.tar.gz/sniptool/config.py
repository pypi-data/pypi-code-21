##################################################
# Copyright (C) 2017, All rights reserved.
##################################################

import os

from pyprelude.file_system import make_path
from pysimplevcs.git_util import git_clone

_SNIPPETS_GIT_URL = "https://github.com/rcook/sniptool-snippets.git"

class Config(object):
    def __init__(self, dir):
        self._dir = dir
        self._repo_dir = None
        self._template_dir = None

    @property
    def repo_dir(self):
        self._ensure_template_dir()
        return self._repo_dir

    @property
    def template_dir(self):
        self._ensure_template_dir()
        return self._template_dir

    def _ensure_template_dir(self):
        if self._template_dir is None:
            self._repo_dir = make_path(self._dir, "sniptool-snippets")
            if not os.path.isdir(self._repo_dir):
                git_clone(_SNIPPETS_GIT_URL, self._repo_dir)

            self._template_dir = make_path(self._repo_dir, "_snippets")
