import uuid
from io import BytesIO
from unittest import TestCase

from dataclay.core.management.classmgr import MetaClass, Property, Type, Operation
from .generic import ContainerGeneric

__author__ = 'Alex Barcelo <alex.barcelo@bsc.es>'
__copyright__ = '2015 Barcelona Supercomputing Center (BSC-CNS)'


class MiniMetaClassTest(ContainerGeneric):
    params = [
        ("name", u"a_class"),
        ("namespace", u"a_namespace"),
        ("parentType", None),
        ("properties", list()),
        ("operations", set()),
        ("isAbstract", False),
        ("languageDepInfos", dict())
    ]

    mutable_params = [
        ("name", u"mutation_class"),
        ("namespace", u"mutation_namespace"),
        ("parentType", None),
    ]

    nullable_fields = ["parentType"]

    class_under_test = MetaClass


class MetaClassTest(ContainerGeneric):
    params = [
        ("name", "a_class"),
        ("namespace", "a_namespace"),
        ("parentType", Type(typeName="I", languageDepInfos=dict(), descriptor="test_descr")),
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
        ("operations", {
            Operation(metaClassID=uuid.uuid4(),
                      name="a_operation",
                      params={u"first_param": Type(typeName="I",
                                                   languageDepInfos=dict()),
                              u"second_param": Type(typeName="I",
                                                    languageDepInfos=dict()),
                              },
                      paramOrder=[u"first_param", u"second_param"],
                      returnType=Type(typeName="F", languageDepInfos=dict(), descriptor="op_t_descr"),
                      namespaceID=uuid.uuid4(),
                      languageDepInfos={},
                      isAbstract=False),
            Operation(metaClassID=uuid.uuid4(),
                      name="b_operation",
                      params={u"first_param": Type(typeName="F", languageDepInfos=dict()),
                              u"second_param": Type(typeName="F", languageDepInfos=dict()),
                              u"third_param": Type(typeName="Z", languageDepInfos=dict()),
                              },
                      paramOrder=[u"first_param", u"second_param", u"third_param"],
                      returnType=Type(typeName="F", languageDepInfos=dict()),
                      implementations=[],
                      namespaceID=uuid.uuid4(),
                      languageDepInfos={}),
        }),
        ("isAbstract", False),
        ("languageDepInfos", {})
    ]

    mutable_params = [
        ("name", "mutation_class"),
        ("namespace", u"mutation_namespace"),
        ("parentType", Type(typeName="float", languageDepInfos=dict()))
    ]

    nullable_fields = ["parentType"]

    class_under_test = MetaClass
