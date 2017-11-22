import unittest

from hgicommon.testing import TestUsingType, create_tests, get_classes_to_test, \
    TEST_LATEST_ONLY_ENVIRONMENT_VARIABLE_SET_VALUE, TestUsingObject, create_tests_using_objects, \
    create_tests_using_types, TypeUsedInTest, ObjectTypeUsedInTest


class _ExampleTestThatUsesTypes(TestUsingType[TypeUsedInTest]):
    """
    Example test that uses types.
    """


class _ExampleTestThatUsesObjects(TestUsingObject[ObjectTypeUsedInTest]):
    """
    Example test that uses objects.
    """


class TestCreateTestsUsingTypes(unittest.TestCase):
    """
    Tests for `create_tests_using_types`.
    """
    def test_can_create_tests(self):
        test_types = {type, int, str, float}
        tests = create_tests_using_types(_ExampleTestThatUsesTypes, test_types)
        for name, test in tests.items():
            self.assertTrue(issubclass(test, TestUsingType))
            test_types.remove(test.get_type_to_test())
        self.assertEqual(0, len(test_types))

    def test_can_create_test_with_custom_naming(self):
        custom_namer = lambda *args: "MyTestName"
        tests = create_tests_using_types(_ExampleTestThatUsesTypes, {object}, custom_namer)
        self.assertEqual(1, len(tests))
        self.assertEqual(custom_namer(), list(tests.keys())[0])


class TestCreateTestsUsingObjects(unittest.TestCase):
    """
    Tests for `create_tests_using_objects`.
    """
    def test_can_create_tests(self):
        test_objects = {object(), int(1), str("2"), float(3.0)}
        tests = create_tests_using_objects(_ExampleTestThatUsesObjects, test_objects)
        for name, test in tests.items():
            self.assertTrue(issubclass(test, TestUsingObject))
            test_objects.remove(test.get_object_to_test())
        self.assertEqual(0, len(test_objects))

    def test_can_create_test_with_custom_naming(self):
        custom_namer = lambda *args: "MyTestName"
        tests = create_tests_using_objects(_ExampleTestThatUsesObjects, {object()}, custom_namer)
        self.assertEqual(1, len(tests))
        self.assertEqual(custom_namer(), list(tests.keys())[0])


class TestCreateTests(unittest.TestCase):
    """
    Tests for `create_tests`.
    """
    def test_can_create_tests_using_types(self):
        tests = create_tests(_ExampleTestThatUsesTypes, {object()})
        self.assertTrue(issubclass(list(tests.values())[0], TestUsingType))

    def test_can_create_tests_using_objects(self):
        tests = create_tests(_ExampleTestThatUsesObjects, {object()}, lambda *args: "Name")
        self.assertTrue(issubclass(list(tests.values())[0], TestUsingObject))


class TestGetClassesToTest(unittest.TestCase):
    """
    Tests for `get_classes_to_test`.
    """
    _ALL_CLASSES = {int, str, float}
    _LATEST_CLASS = str

    def test_all_returned_if_environment_variable_not_set(self):
        assert TEST_LATEST_ONLY_ENVIRONMENT_VARIABLE_SET_VALUE != ""
        to_test = get_classes_to_test(TestGetClassesToTest._ALL_CLASSES, TestGetClassesToTest._LATEST_CLASS,
                                      _environment_variable_reader=lambda str: "")
        self.assertEqual(TestGetClassesToTest._ALL_CLASSES, to_test)

    def test_all_returned_if_environment_variable_set(self):
        to_test = get_classes_to_test(TestGetClassesToTest._ALL_CLASSES, TestGetClassesToTest._LATEST_CLASS,
                                      _environment_variable_reader=lambda str: TEST_LATEST_ONLY_ENVIRONMENT_VARIABLE_SET_VALUE)
        self.assertEqual({TestGetClassesToTest._LATEST_CLASS}, to_test)

    def test_valid_return_given_current_environment_variable_setting(self):
        to_test = get_classes_to_test(TestGetClassesToTest._ALL_CLASSES, TestGetClassesToTest._LATEST_CLASS)
        if len(to_test) == 1:
            self.assertEqual({TestGetClassesToTest._LATEST_CLASS}, to_test)
        else:
            self.assertEqual(TestGetClassesToTest._ALL_CLASSES, to_test)


if __name__ == "__main__":
    unittest.main()
