from __future__ import absolute_import, division, print_function
import time
from collections import namedtuple

from autest.common.constructor import call_base, smart_init
import autest.common.sort as sort
import autest.common.is_a as is_a
import hosts.output as host

# need better name...  to do later


@smart_init
class Order(object):
    @call_base()
    def __init__(self):

        # items holding state
        self.__startbefore = {}  # {process : metadata}
        self.__startafter = {}
        self.__endbefore = {}
        self.__endafter = {}

        # ready logic
        self.__ready = None
        self.__startup_time = None
        # delay logic
        self.__delay_start = None

    def _setupReadyStart(self, obj, *lst, **kw):
        # validate this is an order object
        if not isinstance(obj, Order):
            host.WriteError(
                "Object must be subclass of autest.core.order.Order")
        readyfunc = kw.get("ready", obj._isReady)
        args = kw.copy()
        try:
            del args["ready"]
        except KeyError:
            pass
        value = readyfunc
        if is_a.Number(value):
            readyfunc = lambda hasRunFor: hasRunFor(value)
        elif hasattr(readyfunc, "when_wrapper"):
            readyfunc = readyfunc(**args)
        return readyfunc, args

    def _setupReadyEnd(self, obj, *lst, **kw):
        # validate this is an order object
        if not isinstance(obj, Order):
            host.WriteError(
                "Object must be subclass of autest.core.order.Order")
        readyfunc = kw.get("ready", lambda: True)
        args = kw.copy()
        try:
            del args["ready"]
        except KeyError:
            pass
        value = readyfunc
        if is_a.Number(value):
            readyfunc = lambda hasRunFor: hasRunFor(value)
        elif hasattr(readyfunc, "when_wrapper"):
            readyfunc = readyfunc(**args)
        return readyfunc, args

    def StartBefore(self, *lst, **kw):
        if lst == () and kw == {}:
            return self.__startbefore
        if lst == () and kw != {}:
            raise SyntaxError

        for obj in lst:
            readyfunc, args = self._setupReadyStart(obj, *lst, **kw)
            host.WriteDebugf(
                ["startbefore"],
                "Setting ready logic to wait for object {0} with readyfunc {1}",
                obj, readyfunc)
            self.__startbefore[obj] = (readyfunc, args)

    def StartAfter(self, *lst, **kw):
        if lst == () and kw == {}:
            return self.__startafter
        if lst == () and kw != {}:
            raise SyntaxError
        for obj in lst:
            readyfunc, args = self._setupReadyStart(obj, *lst, **kw)
            host.WriteDebugf(
                ["startafter"],
                "Setting ready logic to wait for object {0} with readyfunc {1}",
                obj, readyfunc)
            self.__startafter[obj] = (readyfunc, args)

    def EndBefore(self, *lst, **kw):
        if lst == () and kw == {}:
            return self.__endbefore
        if lst == () and kw != {}:
            raise SyntaxError
        for obj in lst:
            readyfunc, args = self._setupReady(obj, *lst, **kw)
            host.WriteDebugf(
                ["endbefore"],
                "Setting ready logic to wait for object {0} with readyfunc {1}",
                obj, readyfunc)
            self.__endbefore[obj] = (readyfunc, args)

    def EndAfter(self, *lst, **kw):
        if lst == () and kw == {}:
            return self.__endafter
        if lst == () and kw != {}:
            raise SyntaxError
        for obj in lst:
            readyfunc, args = self._setupReady(obj, *lst, **kw)
            host.WriteDebugf(
                ["endafter"],
                "Setting ready logic to wait for object {0} with readyfunc {1}",
                obj, readyfunc)
            self.__endafter[obj] = (readyfunc, args)

    @property
    def DelayStart(self):
        return self.__delay_start

    @DelayStart.setter
    def DelayStart(self, time):
        self.__delay_start = time

    @property
    def Ready(self):
        return self.__ready

    @Ready.setter
    def Ready(self, test):
        if is_a.Number(test):
            host.WriteDebugf(
                ["order"],
                "Setting ready logic to wait for {0} second for item {1}",
                test, self._ID)
            self.__ready = lambda hasRunFor: hasRunFor(test)
        elif hasattr(test, "when_wrapper"):
            host.WriteDebugf(["order"],
                             "Setting ready logic to {0} second for item {1}",
                             test, self._ID)
            self.__ready = test()
        else:
            host.WriteDebugf(["order"],
                             "Setting ready logic to {0} second for item {1}",
                             test, self._ID)
            self.__ready = test

    def _isReady(self, *lst, **kw):
        if self.__ready is None:
            host.WriteDebugf(
                ["order", 'when', 'process'],
                "Calling Default isReady() function", )
            return True
        try:
            return self.__ready(*lst, **kw)
        except TypeError:
            return self.__ready()

    # internal functions to testing is ready logic
    def _stopReadyTimer(self):
        self.__startup_time = None

    def _startReadyTimer(self):
        self.__startup_time = time.time()

    def _readyTime(self, curr_time):
        if self.__startup_time is None:
            return 0.0
        else:
            return curr_time - self.__startup_time


# some util functions
ordered_item_t = namedtuple("ordered_item_t", "object readyfunc args")


def SortStartOrderedList(lst, startidx=0):
    '''
        make a flatten list of ordered items, ignores Ready logic
        lst -- list of items to sort based on any extra startXXX() relationships
        startidx -- this is the starting default point everything flows around
    '''
    # make depends mapping
    d = {}
    for i in lst:
        try:
            d[i.Name].extend(i.StartBefore().keys())
        except KeyError:
            d[i.Name] = list(i.StartBefore().keys())
        for k in i.StartAfter().keys():
            if k not in d[i]:
                try:
                    d[k].append(i)
                except KeyError:
                    d[k] = [i]
            else:
                "{0} is already a depends on {1}".format(i, k)

    # Sort the items in the list based on depends mapping
    return sort.depends_back_sort(lst, d)


def SortEndOrderedList(lst, startidx=0):
    '''
        make a flatten list of ordered items, ignores Ready logic
        lst -- list of items to sort based on any extra startXXX() relationships
        startidx -- this is the starting default point everything flows around
    '''
    # make depends mapping
    d = {}
    for i in lst:
        try:
            d[i.Name].extend(i.StartBefore().keys())
        except KeyError:
            d[i.Name] = list(i.StartBefore().keys())
        for k in i.StartAfter().keys():
            if k not in d[i]:
                try:
                    d[k].append(i)
                except KeyError:
                    d[k] = [i]
            else:
                "{0} is already a depends on {1}".format(i, k)

    # Sort the items in the list based on depends mapping
    return sort.depends_back_sort(lst, d)


# these funtions generate a list with visted information in it
# The list that are returned are Fat in that they can contain an item
# more than once. This is because the "ready" requirements for a given process
# can happen for different reason for the same process. For example
# you might want to start a server before one client when port 8080 is ready
# while a different client when port 9090 is read on the same server
# example:
# client.StartBefore(server,ready=When.PortOpen(8080))
# client2.StartBefore(server,ready=When.PortOpen(9090))
# at the moment this only works with processes
# everything else at the moment is a straight depends setup
# ie use of ready does not seem to have value for ordering Tests or TestRuns
# as those items are sequential in nature while Processes are asynchronous,
# and need a delay to help allow the sequential execution to work correctly.


def GenerateStartOrderedList(item):
    '''
        make a flatten list of ordered items
        item -- this is the starting default point everything flows around
    '''

    def append_not_exist(olst, nlst):
        for l in nlst:
            if l not in olst:
                olst.append(l)

    def getlst(data, stack, default_proc):
        ret = []

        for obj, func_info in data.items():
            info = ordered_item_t(obj, func_info[0], func_info[1])
            # break any loops
            if info in stack:
                host.WriteMessagef(
                    "Ignoring adding {0} to start order as it is already exist, breaking loop.",
                    info)
                continue
            stack.append(info)
            ret.extend(getlst(obj.StartBefore(), stack, default_proc))
            ret.append(info)
            ret.extend(getlst(obj.StartAfter(), stack, default_proc))
        return ret

    fat_lst = []

    if item.Command is not None:
        fat_lst.extend(getlst(item.StartBefore(), [], item))
        fat_lst.append(ordered_item_t(item, item._isReady, {}))
        fat_lst.extend(getlst(item.StartAfter(), [], item))

    return fat_lst


def GenerateEndOrderedList(item):
    '''
        make a flatten list of ordered items
        item -- this is the starting default point everything flows around
    '''

    def append_not_exist(olst, nlst):
        for l in nlst:
            if l not in olst:
                olst.append(l)

    def getlst(data, stack, default_proc):
        ret = []

        for obj, func_info in data.items():
            info = ordered_item_t(obj, None, {})
            # break any loops
            if info in stack:
                host.WriteMessagef(
                    "Ignoring adding {0} to start order as it is already exist, breaking loop.",
                    info)
                continue
            stack.append(info)
            ret.extend(getlst(obj.EndBefore(), stack, default_proc))
            ret.append(info)
            ret.extend(getlst(obj.EndAfter(), stack, default_proc))
        return ret

    fat_lst = []

    if item.Command is not None:
        fat_lst.extend(getlst(item.EndBefore(), [], item))
        fat_lst.append(ordered_item_t(item, None, {}))
        fat_lst.extend(getlst(item.EndAfter(), [], item))

    return fat_lst
