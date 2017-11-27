from __future__ import absolute_import, division, print_function
import hosts.output as host
from autest.core.test import Test


def ExtendTest(func, name=None):
    if name is None:
        name = func.__name__
    method = func
    setattr(Test, name, method)
    host.WriteVerbose("api",
                      'Added Test extension function "{0}"'.format(name))
