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
from pybuilder.core import before, init, use_plugin

from pybuilder_cram_console_scripts import utils


__author__ = 'Alexey Sanko'
__version__ = "1.0.4"

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
    utils.generate_cram_console_scripts(project, logger)
