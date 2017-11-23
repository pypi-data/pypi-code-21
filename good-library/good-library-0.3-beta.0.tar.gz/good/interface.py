"""
The Good Library

The Good Library is a collection of programming and syntax tools that makes your
python code more expressive and easier to work with.

Author:  Anshul Kharbanda
Created: 10 - 6 - 2017
"""
from inspect import getfullargspec

class ISpec(dict):
    """
    Interface Spec. Contains a set of method specs for the created object.

    Author:  Anshul Kharbanda
    Created: 10 - 19 - 2017
    """
    @staticmethod
    def specdict(item):
        """
        Returns the dictionary of method specs in the given item

        :param item: the item to spec

        :return: the dictionary of method specs in the given item
        """
        return {
            entry[0]:getfullargspec(entry[1])
            for entry in item.__dict__.items()
            if callable(entry[1])
        }

    def __init__(self, item):
        """
        Initializes the spec with the given item

        :param item: the item to spec (or the spec if is dict)
        """
        super(ISpec, self).__init__(
            item if type(item) is dict else ISpec.specdict(item)
        )

    def implemented(self, other):
        """
        Returns true if the given spec is implemented in the other spec

        :param other: the other spec being checked

        :Returns true if the given spec is implemented in the other spec
        """
        return all(item in other.items() for item in self.items())

class Interface:
    """
    A set of methods to be implemented in a class

    Author:  Anshul Kharbanda
    Created 10 - 19 - 2017
    """
    # Instantiate method names
    INSTANTIATE_METHODS = ('__init__', '__new__')

    def __init__(self, infc):
        """
        Creates the interface

        :param infc: the interface object to analyze
        """
        self.__name__ = infc.__name__
        self.__spec__ = ISpec(infc)

    def implemented(self, impl):
        """
        Returns true if the interface is implemented in the given class

        :param impl: the implementing class to check

        :return: true if the interface is implemented in the given class
        """
        return self.__spec__.implemented(ISpec(impl))

    def assert_implemented(self, impl):
        """
        Asserts that the given class implements the Interface else errors

        :param impl: the class to check

        :return: the class if it implements the interface

        :raises Exception: if class does not implement the Interface
        """
        if self.implemented(impl): return impl
        else:
            raise Exception('Interface {infc} not implemented in {impl}'.format(
                infc=self.__name__,
                impl=impl.__name__
            ))

    def __repr__(self):
        """
        Returns the string representation of the interface

        :return: the string representation of the Interface
        """
        return '<interface {} at {}>'.format(self.__name__, id(self))

def Implements(Interface):
    """
    Returns the assert_implemented method of the given interface (used for
    decorator syntax)

    :param Interface: the interface to be implemented

    :return: the assert_implemented method of the given interface
    """
    return Interface.assert_implemented
