from .baseclass import ManagementObject


class StorageLocation(ManagementObject):
    _fields = ["dataClayID",
               "hostname",
               "name",
               "storageTCPPort",
               ]

    _internal_fields = []
    
class ExecutionEnvironment(ManagementObject):
    _fields = ["dataClayID",
               "hostname",
               "name",
               "port",
               "lang"
               ]

    _internal_fields = []

class MetaDataInfo(ManagementObject):
    _fields = ["dataClayID",
               "isReadOnly",
               "datasetID",
               "metaclassID",
               "locations",
               "aliases",
               "ownerID"]

    _internal_fields = []
