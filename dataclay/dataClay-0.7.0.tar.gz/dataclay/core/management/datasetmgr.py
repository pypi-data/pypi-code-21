from .baseclass import ManagementObject


class DataSet(ManagementObject):
    _fields = ["dataClayID", 
               "providerAccountName",
               "name"
               ]

    _internal_fields = ["providerAccountID",
                        ]
