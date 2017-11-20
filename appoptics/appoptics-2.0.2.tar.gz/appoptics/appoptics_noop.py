""" AppOptics instrumentation API for Python.

Copyright (C) 2016 by SolarWinds, LLC.
All rights reserved.

appoptics_noop defines no-op classes for platforms we don't support building the c extension on
"""

# No-op classes intentionally left undocumented
# "Missing docstring"
# pylint: disable-msg=C0103

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
        return Metadata(True)

    def copy(self):
        return self

    def isValid(self):
        return False

    def isSampled(self):
        return False

    def toString(self):
        return ''

class Context(object):
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
        return False

    @staticmethod
    def get():
        return Metadata()

    @staticmethod
    def set(_):
        pass

    @staticmethod
    def fromString(_):
        return Context()

    @staticmethod
    def copy():
        return Context()

    @staticmethod
    def clear():
        pass

    @staticmethod
    def isValid():
        return False

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
        pass

    def addInfo(self, _, __):
        pass

    def addEdge(self, _):
        pass

    def addEdgeStr(self, _):
        pass

    def getMetadata(self):
        return Metadata()

    def metadataString(self):
        return ''

    def is_valid(self):
        return False

    @staticmethod
    def startTrace(_=None):
        return Event()


class Reporter(object):
    def __init__(self, _, __=None):
        pass

    def sendReport(self, _, __=None):
        pass

    def sendStatus(self, _, __=None):
        pass


class UdpReporter(object):
    def __init__(self, _, __=None):
        pass

    def sendReport(self, _, __=None):
        pass

    def sendStatus(self, _, __=None):
        pass

class SslReporter(object):
    def __init__(self, _, __=None):
        pass

    def sendReport(self, _, __=None):
        pass

    def sendStatus(self, _, __=None):
        pass

class Span(object):
    @staticmethod
    def createHttpSpan(_, __, ___, ____, _____, ______):
        pass

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
