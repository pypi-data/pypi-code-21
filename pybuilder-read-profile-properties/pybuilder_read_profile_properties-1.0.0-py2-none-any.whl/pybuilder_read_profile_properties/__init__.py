#   -*- coding: utf-8 -*-
#
#   Copyright 2016 Alexey Sanko
#
#   Licensed under the Apache License, Version 2.0 (the "License");
#   you may not use this file except in compliance with the License.
#   You may obtain a copy of the License at
#
#       http://www.apache.org/licenses/LICENSE-2.0
#
#   Unless required by applicable law or agreed to in writing, software
#   distributed under the License is distributed on an "AS IS" BASIS,
#   WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
#   See the License for the specific language governing permissions and
#   limitations under the License.

from os.path import join as dir_join, isfile
from yaml import load as yaml_load

from pybuilder.core import (before,
                            use_plugin,
                            init)
from pybuilder.errors import BuildFailedException

__author__ = 'Alexey Sanko'

use_plugin("python.core")

DEFAULT_ROOT_ELEMENT = ''


@init
def initialize_read_profile_properties_plugin(project):
    project.plugin_depends_on('PyYAML')
    """ Init default plugin project properties. """
    project.set_property_if_unset('profile', 'dev')
    project.set_property_if_unset('read_profile_properties_dir', '')
    project.set_property_if_unset('read_profile_properties_file_mask', 'properties_%s.yaml')
    # In future we should implement BaseConfig reader type
    # project.set_property_if_unset('read_properties_file_type', 'yaml')


def __add_to_prop(root, elem):
    if root == DEFAULT_ROOT_ELEMENT:
        return elem
    else:
        return root + '_' + elem


def __dict_tree_to_flat(d, path_to_root=DEFAULT_ROOT_ELEMENT):
    return_dict = {}
    if any([isinstance(v, dict) for k, v in d.items()]):
        for k, v in d.items():
            if isinstance(v, dict):
                tmp = __dict_tree_to_flat(v, __add_to_prop(path_to_root, k))
                return_dict.update(tmp)
            else:
                return_dict.update({__add_to_prop(path_to_root, k): v})
    else:
        for k, v in d.items():
            return_dict.update({__add_to_prop(path_to_root, k): v})
    return return_dict


@before("prepare", only_once=True)
def read_profile_properties_from_file(project, logger):
    try:
        prop_file_name = project.get_property('read_profile_properties_file_mask') \
                         % project.get_property('profile')
    except Exception:
        raise
    properties_path = dir_join(project.expand_path('$read_profile_properties_dir'),
                               prop_file_name
                               )
    if not isfile(properties_path):
        raise BuildFailedException(
            "Properties file doesn't exists: {path}".format(path=properties_path))
    with open(properties_path, 'r') as yamlfile:
        prop = yaml_load(yamlfile)
    prop_from_file = __dict_tree_to_flat(prop)
    formatted = ""
    for key in sorted(prop_from_file):
        formatted += "\n%40s : %s%s" % (key,
                                        prop_from_file[key],
                                        " (overwritten)" if project.get_property(key) is not None else "")
    logger.debug("External project properties from file: {output}"
                 .format(output=formatted))
    for key, v in prop_from_file.items():
        project.set_property(key, v)
