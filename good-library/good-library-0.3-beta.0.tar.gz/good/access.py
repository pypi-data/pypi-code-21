"""
The Good Library

The Good Library is a collection of programming and syntax tools that makes your
python code more expressive and easier to work with.

Author:  Anshul Kharbanda
Created: 10 - 6 - 2017
"""
class Const:
    """
    A constant attribute.

    Author:  Anshul Kharbanda
    Created: 11 - 9 - 2017
    """
    def __init__(self, value):
        """
        Initializes the Const with the given value

        :param value: the value to save
        """
        self._value = value

    def __get__(self, instance, klass=None):
        """
        Returns the saved value

        :param instance: the instance that contains the descriptor
        :param klass: the class that contains the descriptor

        :return: the saved value
        """
        return self._value

    def __set__(self, instance, value):
        """
        Raises Exception if trying to set constant value

        :param instance: the instance that contains the descriptor
        :param value: the value to "set" to

        :raises Exception: if trying to set constant value
        """
        # TODO: Create custom error for Accessor
        raise Exception('Constant value {0} cannot be set'.format(self._value))

class GetSet:
    """
    A get-set attribute.

    Author:  Anshul Kharbanda
    Created: 10 - 6 - 2017
    """
    def __init__(self, key):
        """
        Initializes the Get with the given key

        :param key: the key to read from
        """
        self._key = key

    def __get__(self, instance, owner=None):
        """
        Returns the value of the key in the instance

        :param instance: the instance being accessed
        :param owner: the owner or class of the instance

        :return: the value of the key in the instance
        """
        return instance.__getattribute__(self._key)

    def __set__(self, instance, value):
        """
        Sets the value of the key in the instance

        :param instance: the instance being set in
        :param value: the value being set to
        """
        instance.__setattr__(self._key, value)

class Get(GetSet):
    """
    A get-only attribute. Cannot be set.

    Author:  Anshul Kharbanda
    Created: 10 - 6 - 2017
    """
    def __set__(self, instance, value):
        """
        Raises an error because Get's cannot be set

        :param instance: the instance being set in
        :param value: the value being set to

        :raises Exception: Get's cannot be set
        """
        # TODO: Create custom error for Accessor
        raise Exception('Get access {0} cannot be set'.format(self._key))

class Set(GetSet):
    """
    A set-only attribute. Cannot be get.

    Author:  Anshul Kharbanda
    Created: 10 - 6 - 2017
    """
    def __get__(self, instance, owner=None):
        """
        Raises an error because Set's cannot be get

        :param instance: the instance being accessed
        :param owner: the owner or class of the instance

        :raises Exception: Set's cannot be get
        """
        # TODO: Create custom error for Accessor
        raise Exception('Set access {0} cannot be get'.format(self._key))
