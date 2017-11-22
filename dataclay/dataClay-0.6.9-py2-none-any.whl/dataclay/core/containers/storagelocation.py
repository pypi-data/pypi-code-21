from .baseclass import GenericContainer
from dataclay.core.primitives import *

__author__ = 'Alex Barcelo <alex.barcelo@bsc.es>'
__copyright__ = '2015 Barcelona Supercomputing Center (BSC-CNS)'


class StorageLocation(GenericContainer):
    _fields = [("dataclay_id", DCID()),
               ("hostname", Str("utf-16")),
               ("name", Str("utf-16")),
               ("port", Int(32))]

    _nullable_fields = {"dataclay_id"}
    _hashable_fields = {"hostname", "name", "port"}
