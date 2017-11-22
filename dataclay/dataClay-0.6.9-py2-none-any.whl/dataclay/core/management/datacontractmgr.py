from .baseclass import ManagementObject


class DataContract(ManagementObject):
    _fields = ["dataClayID", 
               "providerAccountName",
               "dataSetProvidedName",
               "applicantsNames",
               "beginDate",
               "endDate",
               "publicAvailable",
               ]

    _internal_fields = ["providerAccountID",
                        "providerDataSetID",
                        "applicantsAccountsIDs",
                        ]
