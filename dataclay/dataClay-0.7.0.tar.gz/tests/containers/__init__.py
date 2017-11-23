from unittest import TestSuite, defaultTestLoader

from type import TypeTest, UserTypeTest
from implementation import AccessedImplementationTest
from property import PropertyTest, AccessedPropertyTest
from operation import OperationTest
from metaclass import MiniMetaClassTest, MetaClassTest
from stubs import StubInfoClassTest, PropertyStubInfoClassTest, ImplementationStubInfoClassTest

__author__ = 'Alex Barcelo <alex.barcelo@bsc.es>'
__copyright__ = '2015 Barcelona Supercomputing Center (BSC-CNS)'

test_cases = (MiniMetaClassTest, TypeTest, UserTypeTest,
              AccessedPropertyTest, AccessedImplementationTest,
              MetaClassTest, OperationTest, PropertyTest,
              PropertyStubInfoClassTest, ImplementationStubInfoClassTest,
              StubInfoClassTest,
              )


container_suite = TestSuite()
for test_class in test_cases:
    tests = defaultTestLoader.loadTestsFromTestCase(test_class)
    container_suite.addTests(tests)
