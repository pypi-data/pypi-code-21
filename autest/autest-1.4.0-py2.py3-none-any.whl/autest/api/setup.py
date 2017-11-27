from __future__ import absolute_import, division, print_function
import autest.glb as glb
import autest.common.namespace as namespace
import types
import hosts.output as host
from autest.core.setupitem import SetupItem
from autest.core.setup import Setup

# this api allow users to add new items to Setup
# the user can add a namespace as well to allow for
# logic such as Setup.Copy(...) or Setup.Copy.FromDirectory(...)
# like logic to happen. In this example Copy was added in as:
# autest.api.AddSetupTask(Copy,"__call__",ns='Copy')
# which uses a python trick with overloaded operators to
# add Copy as a special function __call__ to the "namespace" Copy


def AddSetupItem(item, name=None, ns=None):
    # helper function
    def wrapper(self, *lst, **kw):
        self._add_item(item(*lst, **kw))

    # check to make sure this is a SetupItem type
    if not issubclass(item, SetupItem):
        host.WriteError(
            "Object must be subclass of autest.core.setupitem.SetupItem",
            stack=host.getCurrentStack(1)
            )

    # get name of task if user did not provide a value
    if name is None:
        name = item.__name__

    if ns is None:
        host.WriteVerbose("setupext",
                          "Adding setup extension named: {0}".format(name))
        method = wrapper
        setattr(Setup, name, method)
    else:
        # see if we have this namespace defined already
        nsobj = glb.setup_items.get(ns)
        if nsobj is None:
            # create the ns object
            nsobj = type(ns, (namespace.NameSpace, ), {})
            # copy on class type as defined for given name
            glb.setup_items[ns] = nsobj
        # add new method to namespace object
        x = wrapper
        setattr(nsobj, name, x)
        host.WriteVerbose(
            "setupext",
            "Adding setup extension named: {0} to namespace: {1}".format(name,
                                                                         ns))
