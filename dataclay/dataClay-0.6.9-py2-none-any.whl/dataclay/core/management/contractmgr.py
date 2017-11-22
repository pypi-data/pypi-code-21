from .baseclass import ManagementObject


class Contract(ManagementObject):
    _fields = ["dataClayID", 
               "namespace",
               "providerAccountName",
               "applicantsNames",
               "beginDate",
               "endDate",
               "publicAvailable",
               "interfacesInContractSpecs",
               ]
    _internal_fields = ["providerAccountID",
                        "namespaceID",
                        "applicantsAccountsIDs",
                        "interfacesInContract",
                        ]


class InterfaceInContract(ManagementObject):
    _fields = ["id",
               "iface",
               "implementationsSpecPerOperation",
               ]

    _internal_fields = ["interfaceID",
                        "accessibleImplementations",
                        ]


class OpImplementations(ManagementObject):
    _fields = ["id", 
               "operationSignature",
               "numLocalImpl",
               "numRemoteImpl",
               ]

    _internal_fields = ["localImplementationID",
                        "remoteImplementationID",
                        ]
