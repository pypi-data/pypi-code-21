from __future__ import absolute_import, division, print_function
import autest.glb as glb
import hosts.output as host


def RegisterReporter(func, name=None):
    if name is None:
        name = func.__name__
    glb.reporters[name] = func
    host.WriteVerbose("api", 'Registered reporter "{0}"'.format(name))
