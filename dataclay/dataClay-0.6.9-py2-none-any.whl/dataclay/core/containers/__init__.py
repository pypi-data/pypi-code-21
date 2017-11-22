"""Submodule with all the dataClay containers logic and definitions.

For specific information about the containers, see the Java implementation
--it is used as the authoritative implementation of the containers methods,
including serialization and deserialization.

Each container defines the dataClay fields in a _fields method, and some
required extra information (defaults, nullable, etc.).

For more information of the internal magic, see "baseclass.py" file.
"""

# All containers defined in files in this package:
from .storagelocation import StorageLocation
from .executionenvironment import ExecutionEnvironment
from .metadatainfo import MetaDataInfo
from .dataclayobjectmetadata import DataClayObjectMetaData

__author__ = 'Alex Barcelo <alex.barcelo@bsc.es>'
__copyright__ = '2015 Barcelona Supercomputing Center (BSC-CNS)'

__all__ = [
    "StorageLocation", "ExecutionEnvironment", "MetaDataInfo",
    "DataClayObjectMetaData",
]
