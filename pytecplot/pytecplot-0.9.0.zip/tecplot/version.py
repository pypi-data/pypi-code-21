"""Version information of the tecplot Python module can be obtained as a `string
<str>` of the form "Major.Minor.Build"::

    tecplot.__version__

or as a `namedtuple <collections.namedtuple>` with attributes: "major",
"minor", "revision", "build" in that order::

    tecplot.version_info

The underlying |Tecplot 360| installation has its own version which can be
obtained as a `string <str>`::

    tecplot.sdk_version

or as a `namedtuple <collections.namedtuple>`::

    tecplot.sdk_version_info
"""
from collections import namedtuple

from .tecutil import _tecutil_connector

Version = namedtuple('Version', ['major', 'minor', 'revision', 'build'])

version = '0.9.0'
build = '84694'
version_info = Version(*[int(x) for x in version.split('.')], build=build or 0)

sdk_version_info = _tecutil_connector.sdk_version_info
sdk_version = _tecutil_connector.sdk_version
