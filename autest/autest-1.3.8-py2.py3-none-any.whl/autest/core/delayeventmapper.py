from __future__ import absolute_import, division, print_function
import autest.glb as glb
import hosts.output as host
import autest.common as common
import autest.common.is_a as is_a
from autest.common.constructor import call_base, smart_init
from autest.core.testerset import TesterSet

# this is base class to add common logic for when I need to
# delay adding the event mapping.  The reason or this would be cases
# in which more than one value coudl be mapped in a file, but only on can exist in the event
# in cases like this we can make sure the correct logic exists for mapping the first
# or last value only.  Likewise handling cases in which I would want to make more than one
# event can be handled correctly as well.  The second factor this adds is some debug ablity
# on what is being mapped to the event

# this class defines an interface for registering events to the Runable object
# this class holds events and binds them when we runable is told to start.
# this helps with debugging as we can see what is being mapped based on the key
# for the event name being used.


@smart_init
class DelayedEventMapper(object):
    '''
    This class provides the base interface for creating predefined event mappings for a
    defined concept
    '''

    @call_base()
    def __init__(self):
        self.__addevent = {}

    def _RegisterTestSet(self, event_name, event_callbacks):
        ''' 
        differs from _Register as it on adds the callback
        it does not make a property
        '''
        self.__addevent[event_name] = event_callbacks

    def _Register(self, event_name, event_callbacks, property_name, inst=None):
        if inst is None:
            inst = self
        cls = inst.__class__
        varname = "_event_name_{0}_".format(property_name)
        setattr(inst, varname, event_name)
        self._RegisterTestSet(event_name, event_callbacks)

        def getter(self):
            return self._GetRegisteredEvent(getattr(self, varname))

        def setter(self, value):
            if not isinstance(value, TesterSet):
                obj = self._GetRegisteredEvent(getattr(self, varname))
                if is_a.List(value):
                    for v in value:
                        obj.add(v)
                else:
                    obj.assign(value)

        property_name = common.make_list(property_name)
        for p in property_name:
            if not hasattr(cls, p):
                setattr(cls, p, property(getter, setter))

    def _BindEvents(self):
        '''
        Bind the event to the callbacks
        '''
        for obj in self.__addevent.values():
            if not isinstance(obj, TesterSet):
                event, callback = obj
                event += callback
            else:
                obj._bind()

    def _GetCallBacks(self):
        return self.__addevent.values()

    def _RegisterEvent(self, key, event, callback):
        '''
        Default set or override "named" event
        '''
        if key in self.__addevent:
            host.WriteDebug(
                ['testrun'],
                "Replacing existing key: {0} value: {1} with\n new value: {2}".
                format(key, self.__addevent[key], (event, callback)))
        self.__addevent[key] = (event, callback)

    def dump_event_data(self):
        ret = ""
        for k, v in self.__addevent.items():
            if isinstance(v, TesterSet):
                if len(v._testers):
                    ret += k + ":\n"
                    ret += "  " + pprint.pformat(v._testers, indent=2) + "\n"
            else:
                ret += k + ":\n"
                ret += "  {0}\n".format(v)
        return ret

    def _GetRegisteredEvent(self, key):
        ''' 
        return a given event mapping so we can add on to it
        '''
        try:
            return self.__addevent[key]
        except KeyError:
            return None

    def _GetRegisteredEvents(self):
        return self.__addevent
