###############################################################################
#
# IBT: Isolated Build Tool
# Copyright (C) 2017, Richard Cook. All rights reserved.
#
# Simple wrappers around Docker etc. for fully isolated build environments
#
###############################################################################

from __future__ import print_function
import hashlib
import os
import re
import sys
import yaml

from ibt.util import check_process, get_user_info

# Detects current project directory and configuration path based on following
# strategy:
# (1) Look in current directory for Ibtfile
# (2) Look in ancestor directories for Ibtfile up until root of file system
# (3) Look in user .ibtprojects for an entry corresponding to a parent of the
# current directory
class Project(object):
    @staticmethod
    def read(search_dir, locations=[]):
        def _find_matching_config_path(locations, projects, original_dir):
            user_dir = os.path.expanduser("~")
            longest_prefix = os.path.abspath("/")
            longest_dir = None
            longest_config_path = None
            for key in projects:
                full_dir = os.path.abspath(os.path.join(user_dir, key))
                locations.append(full_dir)
                prefix = os.path.commonprefix([full_dir, original_dir])
                if prefix == full_dir and len(prefix) > len(longest_prefix):
                    longest_prefix = prefix
                    longest_dir = full_dir
                    longest_config_path = os.path.abspath(os.path.join(user_dir, projects[key]))
            return longest_dir, longest_config_path

        def _read_config(locations, original_dir):
            user_project_path = os.path.expanduser("~/.ibtprojects")
            locations.append(user_project_path)
            if not os.path.isfile(user_project_path):
                return None

            with open(user_project_path, "rt") as f:
                config = yaml.load(f)

            projects = config.get("projects", None)
            if projects is None:
                return None

            root_dir, config_path = _find_matching_config_path(locations, projects, original_dir)
            return None if root_dir is None else Project(root_dir, config_path)

        def _read_helper(locations, original_dir, search_dir):
            config_path = os.path.join(search_dir, "Ibtfile")
            locations.append(config_path)
            if os.path.isfile(config_path):
                return Project(original_dir, config_path)

            parent_dir = os.path.dirname(search_dir)
            if parent_dir == search_dir:
                return _read_config(locations, original_dir)
            else:
                return _read_helper(locations, original_dir, parent_dir)

        return _read_helper(locations, search_dir, search_dir)

    def __init__(self, root_dir, config_path):
        self._root_dir = root_dir
        self._config_path = config_path
        self._project_id = hashlib.md5(self._root_dir).hexdigest()
        self._image_id = "ibt-{}".format(self._project_id)
        self._dot_dir = os.path.join(os.path.dirname(self._config_path), ".ibt")
        self._default_container_project_dir = "/{}".format(os.path.basename(self._root_dir))
        self._container_dot_dir = "/.ibt"
        self._settings = None
        self._user_info = get_user_info(self._root_dir)

    @property
    def root_dir(self): return self._root_dir

    @property
    def config_path(self): return self._config_path

    @property
    def project_id(self): return self._project_id

    @property
    def image_id(self): return self._image_id

    @property
    def dot_dir(self): return self._dot_dir

    @property
    def default_container_project_dir(self): return self._default_container_project_dir

    @property
    def container_dot_dir(self): return self._container_dot_dir

    @property
    def settings(self):
        if self._settings is None:
            with open(self._config_path, "rt") as f:
                self._settings = yaml.load(f)
        return self._settings

    def resolve_local_path(self, path):
        return os.path.abspath(os.path.join(self._root_dir, path))

    def user_info(self): return self._user_info
