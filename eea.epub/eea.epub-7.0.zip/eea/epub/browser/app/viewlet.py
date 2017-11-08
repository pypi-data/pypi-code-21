""" Custom viewlets
"""
from zope.component import queryMultiAdapter
from plone.app.layout.viewlets import common
from Products.Five.browser.pagetemplatefile import ViewPageTemplateFile

class EPUB(common.ViewletBase):
    """ Custom viewlet
    """
    render = ViewPageTemplateFile('../zpt/viewlet.pt')

    def async(self):
        """ Async enabled
        """
        settings = queryMultiAdapter((self.context, self.request),
                                     name='pdf.support')
        return int(settings.async())

    def available(self):
        """ Available
        """
        settings = queryMultiAdapter((self.context, self.request),
                                     name='epub.support')
        return settings.can_download()
