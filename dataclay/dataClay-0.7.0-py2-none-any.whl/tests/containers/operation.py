import uuid

from .generic import ContainerGeneric
from dataclay.core.management.classmgr import Operation, Type

__author__ = 'Alex Barcelo <alex.barcelo@bsc.es>'
__copyright__ = '2015 Barcelona Supercomputing Center (BSC-CNS)'


class OperationTest(ContainerGeneric):
    params = [
        ("metaClassID", uuid.uuid4()),
        ("name", u"a_operation"),
        # ("params", {
        #     u"first_param": Type(typeName=u"int", languageDepInfos={}),
        #     u"second_param": Type(typeName=u"int", languageDepInfos={}),
        # }),
        ("paramOrder", [u"first_param", u"second_param"]),
        ("returnType", Type(typeName=u"float", languageDepInfos={})),
        ("implementations", []),
        ("namespaceID", uuid.uuid4()),
        ("languageDepInfos", {})
    ]

    mutable_params = [
        ("metaClassID", uuid.uuid4()),
        ("name", u"b_operation"),
        ("returnType", Type(typeName=u"None", languageDepInfos={})),
        ("namespaceID", uuid.uuid4()),
    ]

    nullable_fields = ["metaClassID", "returnType", "namespaceID"]

    class_under_test = Operation
