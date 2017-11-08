""" Browser view for tool
"""
from zope.component import queryAdapter
from Products.Five.browser import BrowserView
from eea.relations.interfaces import IToolAccessor

class View(BrowserView):
    """ Views
    """
    @property
    def content_types(self):
        """ Content types
        """
        tool = queryAdapter(self.context, IToolAccessor)
        if not tool:
            return

        for brain in tool.types():
            yield brain

    @property
    def relations(self):
        """ Relations
        """
        tool = queryAdapter(self.context, IToolAccessor)
        if not tool:
            return

        for brain in tool.relations():
            yield brain
