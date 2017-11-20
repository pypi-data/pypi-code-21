""" AppOptics instrumentation API for Python.

Copyright (C) 2016 by SolarWinds, LLC.
All rights reserved.

appoptics_noop defines no-op/test mock classes for:
a) platforms we don't support building the c extension on
b) running unit test
"""
import pprint

# global set of registered event reporting listeners
listeners = []


class Metadata(object):
    def __init__(self, _=None):
        pass

    @staticmethod
    def fromString(_):
        return Metadata()

    def createEvent(self):
        return Event()

    @staticmethod
    def makeRandom(flag=True):
        return Metadata(_=True)

    def copy(self):
        return self

    def isValid(self):
        return True

    def isSampled(self):
        return True

    def toString(self):
        return ''


class Context(object):
    md = None

    @staticmethod
    def init(_, __):
        pass

    @staticmethod
    def setTracingMode(_):
        return False

    @staticmethod
    def setDefaultSampleRate(_):
        return False

    @staticmethod
    def sampleRequest(_, __):
        return True

    @classmethod
    def get(cls):
        return cls.md

    @classmethod
    def set(cls, md):
        cls.md = md

    @staticmethod
    def fromString(_):
        return Context()

    @staticmethod
    def copy():
        return Context()

    @classmethod
    def clear(cls):
        cls.md = None

    @classmethod
    def isValid(cls):
        return cls.md != None

    @classmethod
    def isSampled(cls):
        return cls.md != None

    @staticmethod
    def toString():
        return ''

    @staticmethod
    def createEvent():
        return Event()

    @staticmethod
    def startTrace(_=None):
        return Event()


class Event(object):
    def __init__(self, _=None, __=None):
        self.props = {}

    def addInfo(self, name, value):
        self.props[name] = value

    def addEdge(self, _):
        pass

    def addEdgeStr(self, _):
        pass

    def getMetadata(self):
        return Metadata()

    def metadataString(self):
        return ''

    def is_valid(self):
        return True

    @staticmethod
    def startTrace(_=None):
        return Event()

    def __repr__(self):
        return '<Event('+str(self.props)+')>'


class Reporter(object):
    """ Mock the Reporter; no-op for unsupported platforms, or unit test harness
        if in APPOPTICS_TEST mode. """
    def __init__(self, _, __=None):
        pass

    def sendReport(self, event, __=None):
        for listener in listeners:
            listener.send(event)

    def sendStatus(self, event, __=None):
        for listener in listeners:
            listener.send(event)


class UdpReporter(object):
    """ Mock UDP Reported; no-op for unsupported platforms, or unit test harness
        if in APPOPTICS_TEST mode. """
    def __init__(self, _, __=None):
        pass

    def sendReport(self, event, __=None):
        for listener in listeners:
            listener.send(event)

    def sendStatus(self, event, __=None):
        for listener in listeners:
            listener.send(event)


class SslReporter(object):
    """ Mock UDP Reported; no-op for unsupported platforms, or unit test harness
        if in APPOPTICS_TEST mode. """
    def __init__(self, _, __=None):
        pass

    def sendReport(self, event, __=None):
        for listener in listeners:
            listener.send(event)

    def sendStatus(self, event, __=None):
        for listener in listeners:
            listener.send(event)


class Span(object):
    @staticmethod
    def createHttpSpan(*args):
        for listener in listeners:
            listener.send({'SPAN_REPORT': args})

class MetricTags(object):
    def add(*args, **kwargs):
        pass


class CustomMetrics(object):
    @staticmethod
    def summary(*args, **kwargs):
        pass

    @staticmethod
    def increment(*args, **kwargs):
        pass


class oboe_metric_tag_t(object):
    def __init__(self, k, v):
        self.key = k
        self.value = v


class AppOpticsListener(object):
    """ Simple test harness for intercepting event reports. """
    def __init__(self):
        self.events = []
        self.listeners = listeners
        listeners.append(self)

    def send(self, event):
        self.events.append(event)

    def get_events(self, *filters):
        """ Returns all events matching the filters passed """
        events = self.events
        for _filter in filters:
            events = [ev for ev in events if _filter(ev)]
        return events

    def str_events(self, *filters):
        return pprint.pformat(self.get_events(*filters))

    def pop_events(self, *filters):
        """ Returns all events matching the filters passed,
        and also removes those events from the Trace so that
        they will not be returned by future calls to
        pop_events or events. """
        matched = self.get_events(*filters)
        for match in matched:
            self.events.remove(match)
        return matched

    def __del__(self):
        self.listeners.remove(self)


class DebugLog(object):
    @staticmethod
    def getLevelName(*args, **kwargs):
        pass

    @staticmethod
    def getModuleName(*args, **kwargs):
        pass

    @staticmethod
    def getLevel(*args, **kwargs):
        pass

    @staticmethod
    def setLevel(*args, **kwargs):
        pass

    @staticmethod
    def setOutputStream(*args, **kwargs):
        pass

    @staticmethod
    def setOutputFile(*args, **kwargs):
        pass

    @staticmethod
    def addDebugLogger(*args, **kwargs):
        pass

    @staticmethod
    def removeDebugLogger(*args, **kwargs):
        pass

    @staticmethod
    def logMessage(*args, **kwargs):
        pass
