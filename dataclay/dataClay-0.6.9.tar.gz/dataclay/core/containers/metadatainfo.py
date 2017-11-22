from .baseclass import GenericContainer
from .storagelocation import StorageLocation
from .executionenvironment import ExecutionEnvironment
from dataclay.core.primitives import *

__author__ = 'Alex Barcelo <alex.barcelo@bsc.es>'
__copyright__ = '2015 Barcelona Supercomputing Center (BSC-CNS)'


class MetaDataInfo(GenericContainer):
    _fields = [("is_read_only", Bool()),
               ("metaclass_id", DCID()),
               ("dataset_id", DCID()),
               ("locations", Dict(DCID(), StorageLocation())),
               ("environments", Dict(DCID(), ExecutionEnvironment())),
               ("aliases", List(Str("utf-16")))]

    _hashable_fields = {"metaclass_id", "dataset_id"}
    _defaults = {"is_read_only": False,
                 "locations": dict(),
                 "environments": dict(),
                 "aliases": list()}
