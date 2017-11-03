from __future__ import absolute_import, division, print_function

# this is a utility class that allows us to add objects
# to another as if it was in a namespace
# ie this mean I can have object foo and add a function to boo
# so that one would call Foo.Boo.myfunc instead of Foo.myfunc

# this is primary used for object like Setup which contain
# basic list of extendable actions to do. This allows a user
# to extend what actions can be called


class NameSpace(object):
    def __init__(self, obj):
        self._parent = obj

    def _add_item(self, task):
        self._parent._add_item(task)
