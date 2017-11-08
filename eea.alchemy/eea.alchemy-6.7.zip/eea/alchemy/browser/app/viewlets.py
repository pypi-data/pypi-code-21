""" Custom viewlets
"""
from zope.component import queryAdapter
from zope.component.hooks import getSite
from plone.app.layout.viewlets import common
from Products.Five.browser.pagetemplatefile import ViewPageTemplateFile
from eea.alchemy.controlpanel.interfaces import IAlchemySettings

class AlchemyViewlet(common.ViewletBase):
    """ A custom viewlet registered above the body tag to insert alchemy markers
    """
    render = ViewPageTemplateFile('../zpt/viewlet.pt')

    def __init__(self, context, request, view, manager=None):
        super(AlchemyViewlet, self).__init__(context, request, view, manager)
        self._settings = None

    @property
    def settings(self):
        """ Settings
        """
        if self._settings is None:
            site = getSite()
            self._settings = queryAdapter(site, IAlchemySettings)
        return self._settings

    @property
    def available(self):
        """ Condition for rendering of this viewlet
        """
        enabled = self.settings.autoTagging or False
        if getattr(self.context, "forcedisableautolinks", False):
            enabled = False
        return enabled

    @property
    def modalEnabled(self):
        """ Condition if Modal Window for Results is enabled
        """
        modal = self.settings.modalDisplay or False
        return modal
