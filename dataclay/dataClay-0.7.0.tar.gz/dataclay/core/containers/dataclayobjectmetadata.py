from dataclay.core.containers.baseclass import GenericContainer
from dataclay.core.primitives import *

__author__ = 'Alex Barcelo <alex.barcelo@bsc.es>'
__copyright__ = '2015 Barcelona Supercomputing Center (BSC-CNS)'


class DataClayObjectMetaData(GenericContainer):
    _fields = [("map_oids", Dict(Int(32),
                                 Tuple(DCID(), DCID(), Int(32)),
                                 size_by_vlq=True)),
               ("map_class_ids", Dict(Int(32), DCID(), size_by_vlq=True)),
               ("map_proxies", Dict(Int(32), Bool(), size_by_vlq=True))]

    _nullable_fields = set()
    _hashable_fields = set()

    def get_object_id(self, tag):
        """Return an ObjectID from its tag."""
        return self.map_oids[tag][0]

    def get_dataset_id(self, tag):
        """Return a DataSetID for a certain object given its tag."""
        return self.map_oids[tag][1]

    def get_metaclass_id_of_object(self, tag):
        """Return the MetaClassID for a certain object given its tag."""
        return self.map_class_ids[self.map_oids[tag][2]]

    def is_proxy(self, tag):
        """Tell if a certain object (given its tag) is a Proxy Instance."""
        return self.map_proxies[tag]

    def get_all_object_info(self, tag):
        """Obtain all the fields for a certain object, given its tag.

        Note that this method has no counterpart in Java, but is implemented in
        Python to make things easier (and reduce the number of slow lookups).
        """
        object_id, dataset_id, class_tag = self.map_oids[tag]
        is_proxy = self.map_proxies[tag]
        metaclass_id = self.map_class_ids[class_tag]

        return object_id, dataset_id, is_proxy, metaclass_id