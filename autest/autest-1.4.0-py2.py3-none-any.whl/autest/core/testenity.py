from __future__ import absolute_import, division, print_function
from future.utils import with_metaclass
from autest.common.constructor import call_base, smart_init
import autest.glb as glb

from .metaclass import _test_enity__metaclass__


# This is the base class for any item that defines some set of tests
# on some runable object
@smart_init
class TestEnity((with_metaclass(_test_enity__metaclass__, object))):

    @call_base()
    def __init__(self, runable=None):
        self.__runable = runable if runable is not None else self

    @property
    def _Runable(self):
        return self.__runable

    @property
    def _RootRunable(self):
        return self.__runable._RootRunable

    def _Register(self, event_name, event_callbacks, property_name):
        # forward call to main runablescope this item is bound to
        return self._Runable._Register(event_name, event_callbacks, property_name, self)

    def _GetRegisteredEvent(self, key):
        return self._Runable._GetRegisteredEvent(key)
