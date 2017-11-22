import os
from abc import ABCMeta, abstractmethod
from typing import TypeVar, Generic, Dict, Iterable, Type, Set, Callable
from unittest import TestCase

TEST_LATEST_ONLY_ENVIRONMENT_VARIABLE_NAME = "TEST_LATEST_ONLY"
TEST_LATEST_ONLY_ENVIRONMENT_VARIABLE_SET_VALUE = "1"

TypeUsedInTest = TypeVar("TestType")
ObjectTypeUsedInTest = TypeVar("ObjectType")


class _TestUsing(TestCase, metaclass=ABCMeta):
    """
    Superclass for tests that use a particular type or object.
    """


class TestUsingType(Generic[TypeUsedInTest], _TestUsing, metaclass=ABCMeta):
    """
    A test using a type that can be retrieved using the `get_type_to_test` method.
    """
    @staticmethod
    @abstractmethod
    def get_type_to_test() -> TypeUsedInTest:
        """
        Gets the class type to use in test.
        :return: the type of class to use in test
        """


class TestUsingObject(Generic[ObjectTypeUsedInTest], _TestUsing, metaclass=ABCMeta):
    """
    A test using a object that can be retrieved using the `get_object_to_test` method.
    """
    @staticmethod
    @abstractmethod
    def get_object_to_test() -> ObjectTypeUsedInTest:
        """
        Gets the object to use in test.
        :return: the object to use in test
        """


def create_tests_using_types(superclass: Type[TestUsingType], types: Iterable[type],
                             test_namer: Callable[[str, str], str]=
                             lambda superclass_name, test_type: "Test%s" % test_type.__name__) \
        -> Dict[str, TestUsingType]:
    """
    Creates tests classes that are subclasses of the given superclass, each of which uses a of different type.
    :param superclass: the test superclass
    :param types: the types to test with
    :param test_namer: function used to generate the name of the test
    :return: dictionary with the names of the tests as keys and the tests as values
    """
    tests = dict()      # type: Dict[str, TestUsingType]
    for test_type in types:
        name = test_namer(superclass, test_type)
        test = type(
            name,
            (superclass[test_type], ),
            # Confusing lambda magic explained here: http://stackoverflow.com/a/2295368
            {"get_type_to_test": staticmethod((lambda test_type: lambda: test_type)(test_type))}
        )
        tests[name] = test
    return tests


def create_tests_using_objects(superclass: Type[TestUsingObject], objects: Iterable[object],
                               test_namer: Callable[[str, str], str]=
                               lambda superclass_name, test_type: "Test%s" % test_type) \
        -> Dict[str, TestUsingObject]:
    """
    Creates tests classes that are subclasses of the given superclass, each of which uses a of different object.
    :param superclass: the test superclass
    :param objects: the objects to test with
    :param test_namer: function used to generate the name of the test
    :return: dictionary with the names of the tests as keys and the tests as values
    """
    tests = dict()      # type: Dict[str, TestUsingObject]
    for test_object in objects:
        name = test_namer(superclass, test_object)
        test = type(
            name,
            (superclass[type(test_object)], ),
            # Confusing lambda magic explained here: http://stackoverflow.com/a/2295368
            {"get_object_to_test": staticmethod((lambda test_type: lambda: test_type)(test_object))}
        )
        tests[name] = test
    return tests


def create_tests(superclass, test_with, test_namer=None):
    """
    Creates tests classes that are subclasses of the given superclass, each of which uses a of different object or type.
    :param superclass: the test superclass
    :param test_with: the variables to test with
    :param test_namer: function used to generate the name of the test
    :return: dictionary with the names of the tests as keys and the tests as values
    """
    test_with_example = list(test_with)[0]
    if isinstance(test_with_example, type):
        create_test_fn = create_tests_using_types
    elif isinstance(test_with_example, object):
        create_test_fn = create_tests_using_objects
    else:
        raise ValueError("Unknown type of variable to test with: %s" % type(test_with))
    if test_namer is None:
        return create_test_fn(superclass, test_with)
    else:
        return create_test_fn(superclass, test_with, test_namer)


def get_classes_to_test(all_classes: Set[type], latest_class: type,
                        _environment_variable_reader: Callable[[str], str]=os.environ.get) -> Set[type]:
    """
    Gets the classes of all those given that are to be tested, where the environment variable
    `TEST_LATEST_ONLY_ENVIRONMENT_VARIABLE_NAME` can be used to limit testing to the given latest only.
    :param all_classes: all classes that can be tested
    :param latest_class: the latest of the given classes
    :param _environment_variable_reader: not to be used - for use in testing only
    :return: classes to be tested
    """
    test_latest_only = _environment_variable_reader(TEST_LATEST_ONLY_ENVIRONMENT_VARIABLE_NAME)
    if test_latest_only == TEST_LATEST_ONLY_ENVIRONMENT_VARIABLE_SET_VALUE:
        return {latest_class}
    else:
        return all_classes
