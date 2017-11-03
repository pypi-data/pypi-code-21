from __future__ import absolute_import, division, print_function
import time
import hosts.output as host
import autest.glb as glb
from autest.common.constructor import call_base, smart_init
from autest.exceptions.killonfailure import KillOnFailureError


@smart_init
class RunLogic(object):
    @call_base()
    def __init__(self):
        pass

    @classmethod
    def Run(cls, obj):
        tmp = cls()
        if not tmp.Start(obj):
            tmp.Stop()
        return tmp

    def StopItems(self, items, longwait=None, shortwait=None):
        for i in self.ShutdownItems(items, longwait, shortwait):
            if not i:
                break

    def ShutdownItems(self, items, longwait=None, shortwait=None):
        if longwait is None:
            longwait = 0
        if shortwait is None:
            shortwait = 0
        if items:
            wtime = longwait
            for p in items:
                st = time.time()
                while p.isRunning():
                    # poll all items
                    p.PollItems(items)
                    # if the time we will wait up?
                    if time.time() - st > wtime:
                        # we kill them
                        p.Stop()
                        # reset time to lesser time for reset for processes
                        wtime = shortwait
                    yield True
                # process is done call poll to make sure
                # all events go off
                p.Poll()

        yield False

    def PollItems(self, items):
        ret = False
        for i in items:
            tmp = i.Poll()
            ret |= tmp
        return ret

    def isReady(self, item, hasrunfor):
        '''
            Test the item mapped ready function as well as the
            the object own ready function (given it has one)
        '''
        obj = item.object
        isReady = True
        isObjReady = True
        args = item.args
        try:
            isObjReady = obj._isReady(process=obj, hasRunFor=hasrunfor, **args)
        except TypeError:
            try:
                isObjReady = obj._isReady(hasRunFor=hasrunfor, **args)
            except TypeError:
                try:
                    isObjReady = obj._isReady(**args)
                except TypeError:
                    isObjReady = obj._isReady()

        try:
            isReady = item.readyfunc(process=obj, hasRunFor=hasrunfor, **args)
        except TypeError:
            try:
                isReady = item.readyfunc(hasRunFor=hasrunfor, **args)
            except TypeError:
                try:
                    isReady = item.readyfunc(**args)
                except TypeError:
                    isReady = item.readyfunc()

        return isReady and isObjReady

    def StartOrderedItemsAync(self, items, logic_cls):

        # this function start a bunch of item at the same time
        # This is great for items such as processes which more than
        # one would be running at a given time
        started_items = []
        host.WriteDebug(["runlogic"], "Starting objects")
        try:
            # note a given Item might be in the list more than once
            # this mean there are different requirements for the next item
            # to be considered ready we want to test for
            for idx, ready_item in enumerate(items):
                typename = type(items[0].object).__name__
                # get next process if any as we will want to
                # use this process name to help with error messages
                # for the user
                try:
                    next_item = items[idx + 1].object
                except IndexError:
                    # we are at the last item or we only have item process to start
                    # In either case we don't need to wait
                    # for item to be ready
                    # Start the item and continue
                    started_items.append(logic_cls.Run(ready_item.object))
                    break
                # if we are here we:
                # * have more than one process
                # * are not at the end of the list
                # * need to start and want to wait on being ready
                host.WriteDebugf(["runlogic"], "Starting object {0}",
                                 ready_item.object.Name)
                starting_obj = logic_cls.Run(ready_item.object)
                started_items.append(starting_obj)

                # Start timer as we have something
                # we have to wait on, and we need to make
                # sure we have a fallback if something is wrong with
                # the isReady logic never becoming ready in time
                ready_item.object._startReadyTimer()
                try:
                    hasRunFor = starting_obj.hasRunFor
                except AttributeError:
                    hasRunFor = None
                isReady = False

                # check to see if should delay the start of the object for some
                # reason
                if ready_item.object.DelayStart:
                    delay_start = time.time()
                    delay_time = 0
                    while delay_time < ready_item.object.DelayStart:
                        # poll other items
                        for f in started_items:
                            if f.isRunning():
                                try:
                                    # Need to do poll on running processes to make sure any events or test run correctly
                                    # while we start up the set of processes
                                    f.Poll()
                                except KillOnFailureError:
                                    self.StopItems(started_items)
                                    return 'Delaying start of {0}'.format(
                                        ready_item.object.Name
                                    ), "Test run stopped because Kill On Failure from {0}".format(
                                        f.Name)
                        delay_time = time - time.time() - delay_start

                while not isReady:
                    isReady = self.isReady(ready_item, hasRunFor)
                    # if it is ready set state on process
                    if isReady:
                        ready_item.object._stopReadyTimer()
                        host.WriteDebugf(["runlogic"], "Object {0} is ready!",
                                         ready_item.object.Name)
                        continue
                    # verify we are running...
                    if not started_items[-1].isRunning():
                        # If we are not running we need to stop
                        self.StopItems(started_items)
                        return 'Waiting for {0} "{1}" to become ready'.format(
                            typename, ready_item.object.
                            Name), 'Process finished before it was ready'
                    # test that the process started in the time needed
                    if ready_item.object.StartupTimeout < ready_item.object._readyTime(
                            time.time()):
                        self.StopItems(started_items)
                        return (
                            "Checking that {0} is ready within {1} seconds so we can start process: {2}".
                            format(typename, ready_item.object.StartupTimeout,
                                   next_item.Name),
                            "Process failed to become ready in time")
                    # poll other items
                    for f in started_items:
                        if f.isRunning():
                            try:
                                # Need to do poll on running processes to make sure any events or test run correctly
                                # while we start up the set of processes
                                f.Poll()
                            except KillOnFailureError:
                                self.StopItems(started_items)
                                return 'Waiting for {0} "{1}" to become ready'.format(
                                    typename, ready_item.object.Name
                                ), "Test run stopped because Kill On Failure"
        except KillOnFailureError as e:
            self.StopItems(started_items)
            return 'KillOnFailure while starting {0} {1}'.format(
                typename, ready_item.object.Name), e.info
        except:
            self.StopItems(started_items)
            raise
        return started_items
