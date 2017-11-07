#   -*- coding: utf-8 -*-
#
#   Copyright 2017 Alexey Sanko
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

"""
    Plugin which extends PyBuilder Cram plugin with console scripts usage
    based on distutils plugin properties
"""
from os import environ, path

from pip._vendor.distlib.scripts import ScriptMaker
from pybuilder.core import before, init, use_plugin
from pybuilder.errors import BuildFailedException
from pybuilder.plugins.python import cram_plugin


__author__ = 'Alexey Sanko'
__version__ = "1.0.3"

use_plugin("python.core")
use_plugin("python.cram")


@init
def initialize_cram_console_scripts(project):
    """ Init default plugin project properties. """
    # set default plugin properties
    project.set_property_if_unset('cram_generate_console_scripts', True)
    # sub-directory for generated scripts
    project.set_property_if_unset('cram_generate_console_scripts_dir',
                                  'generated')


@before("run_integration_tests")
def generate_cram_console_scripts(project, logger):
    """ Generate console scripts according distutils properties"""
    # "cram_run_test_from_target" with True is needed
    if not project.get_property('cram_run_test_from_target'):
        raise BuildFailedException(
            "Please enable cram_run_test_from_target property "
            "or disable plugin cram_console_scripts")
    logger.debug("Generating console scripts.")
    # get list of console scripts from distutils properties
    if project.get_property('distutils_console_scripts'):
        console_scripts = project.get_property('distutils_console_scripts')
    elif (project.get_property('distutils_entry_points')
          and ('console_scripts' in
               project.get_property('distutils_entry_points'))):
        console_scripts = (
            project.get_property(
                'distutils_entry_points')['console_scripts'])
    else:
        raise BuildFailedException(
            "Please provide console scripts with distutils_console_scripts "
            "or with distutils_entry_points `console_scripts` section. "
            "Or disable plugin cram_console_scripts")
    generated_script_dir_dist = path.join(
        project.expand_path("$dir_target/dist/pybuilder_cram_console_scripts-1.0.3"),
        project.get_property('dir_dist_scripts'),
        project.get_property('cram_generate_console_scripts_dir'))
    maker = ScriptMaker(None, generated_script_dir_dist)
    generated_console_scripts = maker.make_multiple(console_scripts)
    cram_plugin._prepend_path(environ, "PATH", generated_script_dir_dist)
    logger.debug(
        "Generated console scripts: %s" % generated_console_scripts)
