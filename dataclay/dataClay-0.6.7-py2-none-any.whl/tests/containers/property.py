import uuid
from .generic import ContainerGeneric
from dataclay.core.management.classmgr import AccessedProperty, Type, Property

__author__ = 'Alex Barcelo <alex.barcelo@bsc.es>'
__copyright__ = '2015 Barcelona Supercomputing Center (BSC-CNS)'


class AccessedPropertyTest(ContainerGeneric):
    params = [
        ("propertyID", uuid.uuid4()),
        ("className", "ClassA"),
        ("name", "property_one")
    ]

    mutable_params = [
        ("propertyID", uuid.uuid4()),
        ("className", "ClassB"),
        ("name", "property_newone")
    ]

    nullable_fields = ["propertyID"]

    class_under_test = AccessedProperty


class PropertyTest(ContainerGeneric):
    params = [
        ("name", "a_property"),
        ("position", 3),
        ("type", Type(typeName="name_type",
                      languageDepInfos={})),
        ("getterOperationID", uuid.uuid4()),
        ("setterOperationID", uuid.uuid4()),
        ("metaClassID", uuid.uuid4()),
        ("namespaceID", uuid.uuid4()),
        ("languageDepInfos", {})
    ]

    mutable_params = [
        ("name", "a_property_bis"),
        ("position", 5),
        ("type", Type(typeName="name_type_bis",
                      languageDepInfos={})),
        ("getterOperationID", uuid.uuid4()),
        ("setterOperationID", uuid.uuid4()),
        ("metaClassID", uuid.uuid4()),
        ("namespaceID", uuid.uuid4()),
    ]

    nullable_fields = ["getterOperationID", "setterOperationID",
                       "metaClassID", "namespaceID"]

    class_under_test = Property
