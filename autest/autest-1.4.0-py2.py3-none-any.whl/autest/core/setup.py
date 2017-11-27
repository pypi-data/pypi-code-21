from __future__ import absolute_import, division, print_function
import traceback
from future.utils import with_metaclass

import autest.glb as glb
from autest.exceptions.setuperror import SetupError
from autest.testers import tester


class _setup__metaclass__(type):
    def __call__(cls, *lst, **kw):
        inst = type.__call__(cls, *lst, **kw)
        for k, v in glb.setup_items.items():
            setattr(inst, k, v(inst))
        return inst


def mapsetup(item):
    def dosetup(ev):
        try:
            item.RanOnce = True
            item.setup()
        except SetupError as e:
            # this is a known failure
            item._Result = tester.ResultType.Failed
            item._Reason = str(e)
        except Exception as e:
            # this is some random expection
            item._Result = tester.ResultType.Exception
            item._Reason = traceback.format_exc()

    return dosetup


def mapcleanup(item):
    def docleanup(ev):
        item.cleanup()

    return docleanup


class Setup(with_metaclass(_setup__metaclass__, object)):
    def __init__(self, test):
        self.__setup_items = []
        self.__test = test
        self.__reason = None
        self.__result = None

    def _BindEvents(self):

        for item in self.__setup_items:
            if hasattr(item, 'setup'):
                self.__test.SetupEvent.Connect(mapsetup(item))

        for item in self.__setup_items:
            if hasattr(item, 'cleanup'):
                self.__test.CleanupEvent.Connect(mapcleanup(item))

    def _add_item(self, task):
        # bind the setup task with the test object so it
        # can get information about certain locations
        task._bind(self.__test)
        self.__setup_items.append(task)

    @property
    def _Items(self):
        return self.__setup_items

    @property
    def _Result(self):
        if self.__result is None:
            # we have no tests to run?
            if len(self.__setup_items) == 0:
                self.__result = tester.ResultType.Passed
            else:
                # get results of this runnable
                self.__result = -1
                for i in self.__setup_items:
                    if self.__result < i._Result:
                        self.__result = i._Result

        return self.__result

    @property
    def _Reason(self):
        # if not self.__reason:
        # return "Setup has no issues"
        return self.__reason

    @_Reason.setter
    def _Reason(self, value):
        self.__reason = value

    @property
    def _Failed(self):
        return self.__reason is not None


#import autest.api
# autest.api.AddTestEnityMember(Setup)
