# coding=utf-8

"""
One part of meta programming is being able to handle when an object doesn't respond to a message.  It could be
incompatible object, dynamically handled method (ex, for a DSL), typo, etc.

Python calls an object's __getattr__(name) method when it does not find an attribute that matches the name.  __getattr__
returns a method reference if it finds the attribute, raises AttributeError otherwise.

This module provides a mixin that adds two methods, method_messing for handling missing instance methods, and
class_method_missing for handling missing class methods.  The intent is for your class to simply override these
methods.
"""

from six import add_metaclass

__docformat__ = 'restructuredtext en'
__author__ = 'wrighroy'


# noinspection PyDocstring
class MethodMissingClassHook(type):
    def __getattr__(cls, item):
        """
        Hook in the class method_missing method.
        """
        print("MethodMissingClassHook.__getattr__({item})".format(item=str(item)))

        def delegator(*argv, **kwargs):
            """called when the class dispatcher can not find the given attribute name"""
            return cls.class_method_missing(item, *argv, **kwargs)
        return delegator


# noinspection PyDocstring
@add_metaclass(MethodMissingClassHook)
class MethodMissingHook(object):

    def __getattr__(self, item):
        """
        Hook in the instance method_missing method.
        """
        def delegator(*argv, **kwargs):
            return self.method_missing(item, *argv, **kwargs)
        return delegator

    @classmethod
    def class_method_missing(cls, name, *argv, **kwargs):
        """
        Called when normal class dispatching fails to resolve the called method.

        The default behavior is to raise AttributeError.  The change this behavior, override this method.

        :param name: method name called
        :type name: str
        :param argv: positional arguments passed on the method call
        :type argv: list
        :param kwargs: keyword arguments passed on the method call
        :type kwargs: dict
        :return: None
        :raises: AttributeError
        """
        print('class_method_missing')
        raise AttributeError(MethodMissingClassHook.method_as_string(name, *argv, **kwargs))

    # noinspection PyMethodMayBeStatic
    def method_missing(self, name, *argv, **kwargs):
        """
        Called when normal instance dispatching fails to resolve the called method.

        The default behavior is to raise AttributeError.  The change this behavior, override this method.

        :param name: method name called
        :type name: str
        :param argv: positional arguments passed on the method call
        :type argv: list
        :param kwargs: keyword arguments passed on the method call
        :type kwargs: dict
        :return: None
        :raises: AttributeError
        """
        raise AttributeError(MethodMissingClassHook.method_as_string(name, *argv, **kwargs))

    @staticmethod
    def method_as_string(name, *argv, **kwargs):
        """
        Format the method name and arguments into a human readable string.

        :param name: method name
        :type name: str
        :param argv: positional arguments passed on the method call
        :type argv: list
        :param kwargs: keyword arguments passed on the method call
        :type kwargs: dict
        :return: the formatted string
        :rtype: str
        """
        args = []
        if argv:
            args.append(', '.join(str(arg) for arg in argv))
        if kwargs:
            for k in sorted(kwargs.keys()):
                args.append('{key}={value}'.format(key=str(k), value=str(kwargs[k])))
        return "{name}({args})".format(name=name, args=', '.join(args))
