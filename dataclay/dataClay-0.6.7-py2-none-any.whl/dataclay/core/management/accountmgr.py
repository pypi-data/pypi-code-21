from .baseclass import ManagementObject


class Account(ManagementObject):
    _fields = ["username",
               "credential",
               "role",
               ]


class Credential(ManagementObject):
    _fields = list()


class PasswordCredential(Credential):
    _fields = ["password",
               ]