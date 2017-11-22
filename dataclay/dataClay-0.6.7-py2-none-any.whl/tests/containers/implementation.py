import unittest
import uuid

from .generic import ContainerGeneric

from dataclay.core.management.classmgr import AccessedImplementation

__author__ = 'Alex Barcelo <alex.barcelo@bsc.es>'
__copyright__ = '2015 Barcelona Supercomputing Center (BSC-CNS)'


class AccessedImplementationTest(ContainerGeneric):
    params = [
        ("namespace", "impl_namespace"),
        ("opSignature", "first_signature"),
        ("className", "ClassA"),
        ("implPosition", 1)
    ]

    mutable_params = [
        ("namespace", "new_impl_namespace"),
        ("opSignature", "first_signature_again"),
        ("className", "ClassB")
    ]

    nullable_field = []

    class_under_test = AccessedImplementation


if __name__ == '__main__':
    unittest.main()
