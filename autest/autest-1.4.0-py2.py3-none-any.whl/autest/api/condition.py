from __future__ import absolute_import, division, print_function

import hosts.output as host
from autest.core.conditions import ConditionFactory


def ExtendCondition(func, name=None):
    if name is None:
        name = func.__name__

    if hasattr(ConditionFactory, name):
        host.WriteWarningf("Condition already has a '{name}' test! Overidding with new function", name=name)

    setattr(ConditionFactory, name, func)
    host.WriteVerbose("api",
                      'Added Condition extension function "{0}"'.format(name))