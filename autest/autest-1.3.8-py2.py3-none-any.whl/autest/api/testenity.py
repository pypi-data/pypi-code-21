from __future__ import absolute_import, division, print_function

import hosts.output as host
import autest.glb as glb
from autest.core.testenity import TestEnity
from autest.core.test import Test
from autest.core.testrun import TestRun


def AddTestEnityMember(clsobj, name=None, classes=None):
    # imported here to break import cycle
    from autest.testenities.process import Process

    if not issubclass(clsobj, TestEnity):
        host.WriteError(
            "Object must be subclass of autest.core.testenity.TestEnity")

    # get name of task if user did not provide a value
    if name is None:
        name = clsobj.__name__

    if classes is None:
        classes = [Test, TestRun, Process]

    for cls in classes:
        # get any info that might exist, else return empty dictionary
        cls_info = glb.runable_items.get(cls, {})
        if name in cls_info:
            host.WriteError(
                "Cannot add user object member {1}.{0}\n {0} already exists on {1} object".
                format(name, cls.__name__),
                show_stack=False)
        cls_info[name] = clsobj
        # set the information ( as this might have been the empty dictionary )
        glb.runable_items[cls] = cls_info
