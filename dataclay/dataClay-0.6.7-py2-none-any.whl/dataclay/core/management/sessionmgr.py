from .baseclass import ManagementObject


class SessionInfo(ManagementObject):
    _fields = ["sessionID",
               "accountID",
               "propertiesOfClasses",
               "sessionContracts",
               "sessionDataContracts",
               "dataContractIDforStore",
               "language",
               "ifaceBitmaps",
               "endDate",
               ]

    _internal_fields = []


class SessionContract(ManagementObject):
    _fields = ["id",
               "contractID",
               "sessionInterfaces",
               ]

    _internal_fields = []


class SessionInterface(ManagementObject):
    _fields = ["id",
               "interfaceID",
               "sessionProperties",
               "sessionOperations",
               "classOfInterface",
               "importOfInterface",
               ]

    _internal_fields = []


class SessionProperty(ManagementObject):
    _fields = ["id",
               "propertyID",
               ]

    _internal_fields = []


class SessionOperation(ManagementObject):
    _fields = ["id",
               "operationID",
               "sessionLocalImplementation",
               "sessionRemoteImplementation",
               ]

    _internal_fields = []


class SessionDataContract(ManagementObject):
    _fields = ["id",
               "dataContractID",
               "dataSetOfProvider",
               ]

    _internal_fields = []


class SessionImplementation(ManagementObject):
    _fields = ["id",
               "implementationID",
               "namespaceID",
               "respAccountID",
               ]

    _internal_fields = []
