from __future__ import absolute_import, division, print_function

import hosts.output as host
from autest.core.testrun import TestRun


def ExtendTestRun(func, name=None, setproperty=False):
    if name is None:
        name = func.__name__

    method = func
    if setproperty:
        method = property(fset=method)

    setattr(TestRun, name, method)
    host.WriteVerbose("api",
                      'Added TestRun extension function "{0}"'.format(name))
