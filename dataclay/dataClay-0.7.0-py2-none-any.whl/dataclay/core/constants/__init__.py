"""Global constants holder and discover.

This module is responsible of holding general application-wide constants, and
also provide some basic mechanisms for the Java .properties constant loading.

Note that the package available here (properties) is a placeholder folder which
contains hard links to the properties' files.
"""
from .propertyclasses import (LangCodes,
                              MethodIds,
                              PythonTypeSignatures,
                              ErrorCodes)
from . import properties

__author__ = 'Alex Barcelo <alex.barcelo@bsc.es>'
__copyright__ = '2015 Barcelona Supercomputing Center (BSC-CNS)'

PROPERTIES_DIR = properties.__path__[0]

# General global application constants
lang_codes = LangCodes(PROPERTIES_DIR)

method_ids = MethodIds(PROPERTIES_DIR)

python_type_signatures = PythonTypeSignatures(PROPERTIES_DIR)

error_codes = ErrorCodes(PROPERTIES_DIR)
