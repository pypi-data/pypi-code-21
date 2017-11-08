""" Namechooser
"""
import re
from zope.interface import implements

from zope.container.interfaces import INameChooser
from zope.container.contained import NameChooser

ATTEMPTS = 10000

class PortalTypeNameChooser(NameChooser):
    """A name chooser for portal types.
    """

    implements(INameChooser)

    def __init__(self, context):
        self.context = context

    def checkName(self, name, obj):
        """ Check name
        """
        return True

    def chooseName(self, name, obj):
        """ Choose name
        """
        container = self.context
        name = name or getattr(obj, 'title', '')
        safe = re.compile(r'[^_A-Za-z0-9\.\-\s]')
        name = safe.sub('', name)
        name = name or obj.__class__.__name__
        name = name.strip()

        i = 0
        new_name = name
        while new_name in container.objectIds() and i <= ATTEMPTS:
            i += 1
            new_name = "%s-%d" % (name, i)

        self.checkName(new_name, obj)
        return new_name.encode('utf-8')
