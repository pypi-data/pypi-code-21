# -*- coding: utf-8 -*-


class UnsupportedDRMAAVersion(Exception):
    def __init__(self, ver):
        self.ver = ver

    def __str__(self):
        return "We only support DRMAA version 1.x - You have {}".format(self.ver)


class UnrecognizedQueueSystem(Exception):
    def __init__(self, contact, info, impl, version):
        self.args = (contact, info, impl, version)

    def __str__(self):
        return """Failed to recognize the current system.

Please report to the author(s) of jug_schedule and include the following

Contact : {0}
DRM Info: {1}
DRMAA   : {2}
Version : {3}
""".format(*self.args)


class CleanExit(Exception):
    "Raised when a fatal error ocurred but we should try to exit cleanly"


class UnsupportedFeature(Exception):
    "Raised when some behavior is not supported"

# vim: ai sts=4 et sw=4
