##################################################
# Copyright (C) 2017, All rights reserved.
##################################################

import os

from pyprelude.file_system import make_path
from pysimplevcs.git_util import git_clone

class Config(object):
    def __init__(self, dir):
        self._dir = dir
        self._template_dir = None

    @property
    def template_dir(self):
        if self._template_dir is None:
            template_repo_dir = make_path(self._dir, "sniptool-snippets")
            if not os.path.isdir(template_repo_dir):
                git_clone("https://github.com/rcook/sniptool-snippets.git", template_repo_dir)

            self._template_dir = make_path(template_repo_dir, "_snippets")

        return self._template_dir
