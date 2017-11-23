import uuid
from io import BytesIO
from unittest import TestCase

from dataclay.core.management.classmgr import Type, Property
from dataclay.core.management.stubs import StubInfo, ImplementationStubInfo, PropertyStubInfo
from .generic import ContainerGeneric

__author__ = 'Alex Barcelo <alex.barcelo@bsc.es>'
__copyright__ = '2015 Barcelona Supercomputing Center (BSC-CNS)'


class StubInfoClassTest(ContainerGeneric):
    params = [
        ("namespace", u"a_namespace"),
        ("className", u"a_class"),
        ("parentClassName", u"a_parentClassName"),
        ("applicantID", uuid.uuid4()),
        ("classID", uuid.uuid4()),
        ("namespaceID", uuid.uuid4()),
        ("contracts", {uuid.uuid4(), uuid.uuid4(), uuid.uuid4()}),
        ("implementationsByID", dict()),
        ("implementations", {u"first_impl": ImplementationStubInfo(namespace="I",
                                                                   className="c_name",
                                                                   signature="sign"),
                             u"second_impl": ImplementationStubInfo(namespace="I",
                                                                    className="c_name",
                                                                    signature="sign"),
                             }),
        ("properties", [
            Property(name="a_property",
                     position=3,
                     type=Type(typeName="name_type",
                               languageDepInfos={}),
                     getterOperationID=uuid.uuid4(),
                     setterOperationID=uuid.uuid4(),
                     metaClassID=uuid.uuid4(),
                     namespaceID=uuid.uuid4(),
                     languageDepInfos={},
                     namespace="test_namespace"),
            Property(name="b_property",
                     position=5,
                     type=Type(typeName="name_type",
                               languageDepInfos={},
                               descriptor="type_prop_descr"),
                     getterOperationID=uuid.uuid4(),
                     setterOperationID=uuid.uuid4(),
                     metaClassID=uuid.uuid4(),
                     namespaceID=uuid.uuid4(),
                     languageDepInfos={},
                     className="class_name")
        ]),
        ("propertyListWithNulls", list())
    ]

    mutable_params = [
        ("className", u"mutation_class"),
        ("namespace", u"mutation_namespace"),
        ("parentClassName", u"mutation_parentClassName"),
    ]

    nullable_fields = ["parentClassName"]

    class_under_test = StubInfo


class PropertyStubInfoClassTest(ContainerGeneric):
    params = [
        ("namespace", u"a_namespace"),
        ("propertyName", u"a_prop"),
        ("namespaceID", uuid.uuid4()),
        ("propertyID", uuid.uuid4()),
        ("propertyType", Type(typeName="name_type", languageDepInfos={}, descriptor="desc")),
        ("getterOperationID", uuid.uuid4()),
        ("setterOperationID", uuid.uuid4())
    ]

    mutable_params = [
        ("propertyName", u"mutation_prop"),
        ("namespace", u"mutation_namespace"),
        ("parentClassName", u"mutation_parentClassName"),
    ]

    nullable_fields = ["propertyType"]

    class_under_test = PropertyStubInfo


class ImplementationStubInfoClassTest(ContainerGeneric):
    params = [
        ("namespace", u"a_namespace"),
        ("className", u"a_class"),
        ("signature", u"a_sign"),
        ("parameters", {u"first_param": Type(typeName="I",
                                             languageDepInfos=dict()),
                        u"second_param": Type(typeName="I",
                                              languageDepInfos=dict()),
                        }),
        ("paramsOrder", [u"first_param", u"second_param"]),
        ("returnType", Type(typeName="name_type", languageDepInfos={}, signature="sign")),
        ("namespaceID", uuid.uuid4()),
        ("operationID", uuid.uuid4()),
        ("localImplID", uuid.uuid4()),
        ("remoteImplID", uuid.uuid4()),
        ("contractID", uuid.uuid4()),
        ("interfaceID", uuid.uuid4()),
        ("responsibleRemoteAccountID", uuid.uuid4()),
        ("implPosition", 3),
    ]

    mutable_params = [
        ("className", u"mutation_class"),
        ("namespace", u"mutation_namespace"),
    ]

    nullable_fields = ["parameters", "paramsOrder"]

    class_under_test = ImplementationStubInfo
