# coding=utf-8

"""
Unit tests for method_missing mixin.

We create two classes, Foo, and Bar.  Foo is our control, we apply the mixin but do not override the default
method missing behavior.  While Bar is our class with new behavior where we override both instance and class
method_missing methods.
"""
import collections
from fullmonty.method_missing_hook import MethodMissingHook

__docformat__ = 'restructuredtext en'
__author__ = 'wrighroy'


# noinspection PyMethodMayBeStatic
class Foo(MethodMissingHook):
    """
    Foo class does not implement method_missing method and is our test control to make sure we don't break anything.
    """
    CHARLEY = 'Brown'

    def __init__(self):
        self.davidson = 'Harley'

    def live_to_ride(self):
        return 'Ride to Live'


# noinspection PyMethodMayBeStatic
class Bar(MethodMissingHook):
    """Bar class overrides method_missing and class_method_missing methods."""
    WILLIEG = 'Davidson'

    def __init__(self):
        self.hog = 'wild'

    def live_to_ride(self):
        return 'Ride to Live'

    # override default method_missing method
    def method_missing(self, name, *argv, **kwargs):
        if name in ['FLSTC', 'Heritage', 'Softtail']:
            return "FLSTC Heritage Softtail"
        return Bar.method_as_string(name, *argv, **kwargs)

    # override default class_method_missing method
    @classmethod
    def class_method_missing(cls, name, *argv, **kwargs):
        return cls.method_as_string(name, *argv, **kwargs)


# noinspection PyMethodMayBeStatic
class TestClass(object):
    def test_attribute_accessor(self):
        """make sure didn't break attribute accessors"""
        foo = Foo()
        foo.alpha = 1
        assert foo.alpha == 1
        assert foo.davidson == 'Harley'
        assert foo.live_to_ride() == 'Ride to Live'

        bar = Bar()
        assert bar.hog == 'wild'
        assert bar.live_to_ride() == 'Ride to Live'

    def test_class_accessor(self):
        """make sure didn't break constants"""
        assert Foo.CHARLEY == 'Brown'
        assert Bar.WILLIEG == 'Davidson'

    def test_method_missing(self):
        """didn't break default missing method behavior"""
        foo = Foo()
        try:
            foo.alpha()
            assert False, 'did not raise expected AttributeError'
        except AttributeError as ex:
            assert True, 'raised expected AttributeError %s' % str(ex)

    def test_handing_method_missing(self):
        """use Bar's method_missing with no args to the missing method"""
        bar = Bar()
        try:
            result = bar.beta()
            assert result == 'beta()', 'did not return method name (%s)' % result
        except AttributeError as ex:
            assert False, 'was not found %s' % str(ex)

    def test_handing_method_missing_with_args(self):
        """use Bar's method_missing with just args to the missing method"""
        bar = Bar()
        try:
            result = bar.beta(1, 2, 3)
            assert result == 'beta(1, 2, 3)', 'did not return method name (%s)' % result
        except AttributeError as ex:
            assert False, 'was not found %s' % str(ex)

    def test_handing_method_missing_with_kwargs(self):
        """use Bar's method_missing with just kwargs to the missing method"""
        bar = Bar()
        try:
            result = bar.beta(a=4, b=5, c=6)
            assert result == 'beta(a=4, b=5, c=6)', 'did not return method name (%s)' % result
        except AttributeError as ex:
            assert False, 'was not found %s' % str(ex)

    def test_handing_method_missing_with_both(self):
        """use Bar's method_missing with both args and kwargs to the missing method"""
        bar = Bar()
        try:
            result = bar.beta(1, 2, 3, a=4, b=5, c=6)
            assert result == 'beta(1, 2, 3, a=4, b=5, c=6)', 'did not return method name (%s)' % result
        except AttributeError as ex:
            assert False, 'was not found %s' % str(ex)

    def test_allow_specific_missing_methods(self):
        bar = Bar()
        assert bar.FLSTC() == 'FLSTC Heritage Softtail'
        assert bar.Heritage() == 'FLSTC Heritage Softtail'
        assert bar.Softtail() == 'FLSTC Heritage Softtail'
        assert bar.WLA() == 'WLA()'

    def test_handling_missing_class_method(self):
        try:
            Foo.alpha()
            assert False, 'did not raise expected AttributeError'
        except AttributeError as ex:
            assert True, 'raised expected AttributeError %s' % str(ex)
        try:
            result = Bar.beta(1, 2, 3, a=4, b=5, c=6)
            assert result == 'beta(1, 2, 3, a=4, b=5, c=6)', 'did not return method name (%s)' % result
        except AttributeError as ex:
            assert False, 'was not found %s' % str(ex)


class Mash(MethodMissingHook):
    """
    dictionary keys must be hashable
    """

    def __init__(self, initial_dict=None):
        if initial_dict is None:
            initial_dict = {}
        self._attributes = initial_dict.copy()

    def __getitem__(self, item):
        """
        Called to implement evaluation of self[key]. For sequence types, the accepted keys should be integers and
        slice objects. Note that the special interpretation of negative indexes (if the class wishes to emulate a
        sequence type) is up to the __getitem__() method. If key is of an inappropriate type, TypeError may be
        raised; if of a value outside the set of indexes for the sequence (after any special interpretation of
        negative values), IndexError should be raised. For mapping types, if key is missing (not in the
        container), KeyError should be raised.

        :param item: dictionary index
        :type item: object
        :return: the value referenced by the item index
        :rtype: object
        :raises: IndexError|TypeError|KeyError
        """
        if item not in self._attributes:
            raise KeyError("{item} not in this mash.".format(item=str(item)))
        return self._attributes[item]

    def __setitem__(self, key, value):
        if not isinstance(key, collections.Hashable):
            raise TypeError("The key ({key}) is not hashable".format(key=str(key)))
        self._attributes[key] = value
        return self

    def __delitem__(self, key):
        if not isinstance(key, collections.Hashable):
            raise TypeError("The key ({key}) is not hashable".format(key=str(key)))
        del (self._attributes[key])
        return self

    # def method_missing(self, name, *argv, **kwargs):
    #     """
    #     Called when normal instance dispatching fails to resolve the called method.
    #
    #     The default behavior is to raise AttributeError.  The change this behavior, override this method.
    #
    #     :param name: method name called
    #     :type name: str
    #     :param argv: positional arguments passed on the method call
    #     :type argv: list
    #     :param kwargs: keyword arguments passed on the method call
    #     :type kwargs: dict
    #     :return: object
    #     :raises: AttributeError
    #     """
    #     return self._attributes[name]

    def attributes(self):
        """
        Return attribute dictionary.

        :return: the attributes
        :rtype: dict
        """
        return self._attributes
