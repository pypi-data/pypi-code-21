import unittest
import uuid

from .generic import ContainerGeneric
from dataclay.core.management.classmgr import Type, UserType

__author__ = 'Alex Barcelo <alex.barcelo@bsc.es>'
__copyright__ = '2015 Barcelona Supercomputing Center (BSC-CNS)'


class TypeTest(ContainerGeneric):
    params = [
        ("typeName", u"MyName"),
        ("languageDepInfos", {})
    ]

    mutable_params = [
        ("typeName", u"ChangeName")
    ]

    nullable_field = ["descriptor"]

    class_under_test = Type


class UserTypeTest(ContainerGeneric):
    params = [
        ("namespace", u"MyNamespace"),
        ("classID", uuid.uuid4())
    ]

    mutable_params = [
        ("namespace", u"ChangedNamespace")
    ]

    nullable_fields = []

    class_under_test = UserType

if __name__ == '__main__':
    unittest.main()
