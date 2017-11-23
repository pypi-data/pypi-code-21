import yaml

from .baseclass import ManagementObject
from .classmgr import Type
from . import Loader


# Added implPosition
class ImplementationStubInfo(ManagementObject):
    _fields = ["namespace",
               "className",
               "signature",
               "parameters",
               "paramsOrder",
               "returnType",
               "namespaceID",
               "operationID",
               "localImplID",
               "remoteImplID",
               "contractID",
               "interfaceID",
               "responsibleRemoteAccountID",
               "implPosition",
               ]

    _internal_fields = list()

    _typed_fields = {"returnType": Type}


class PropertyStubInfo(ManagementObject):
    _fields = ["namespace",
               "propertyName",
               "namespaceID",
               "propertyID",
               "propertyType",
               "getterOperationID",
               "setterOperationID",
               "beforeUpdate",
               "afterUpdate"
               ]

    _internal_fields = list()

    _typed_fields = {"propertyType": Type}


# Added implementationsByID and removed implementationsBySignature and implementationsByOpNameAndNumParams
class StubInfo(ManagementObject):
    _fields = ["namespace",
               "className",
               "parentClassName",
               "applicantID",
               "classID",
               "namespaceID",
               "contracts",
               "implementationsByID",
               "implementations",
               "properties",
               "propertyListWithNulls",
               ]

    _internal_fields = list()


def babel_stubs_load(stream):
    # Note the explicit list, just in case the caller wants to close the provided file/buffer
    map_babel_stubs = yaml.load(stream, Loader=Loader)
    result = list()
    for k, v in map_babel_stubs.iteritems():
        result.append(yaml.load(v))
    return result
