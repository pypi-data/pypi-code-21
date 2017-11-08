""" Inline comments notifications subscription
"""
from zope.component import queryAdapter
from Products.Five.browser import BrowserView
from Products.statusmessages.interfaces import IStatusMessage
from eea.annotator.interfaces import IAnnotatorStorage
from eea.annotator.config import EEAMessageFactory as _

class Subscribe(BrowserView):
    """ Subscribe
    """
    @property
    def storage(self):
        """ Storage
        """
        return queryAdapter(self.context, IAnnotatorStorage)

    def _redirect(self, msg=''):
        """ Redirect
        """
        if self.request.get('ajax', False):
            return msg

        if msg:
            IStatusMessage(self.request).addStatusMessage(msg)

        return self.request.response.redirect(self.context.absolute_url())

    def __call__(self, *args, **kwargs):
        storage = self.storage
        if not storage:
            msg = _(u"Couldn't subscribe you to inline comments notifications")
        else:
            storage.subscribe()
            msg = _(u"Successfully subscribed you "
                    u"to inline comments notifications")
        return self._redirect(msg)


class Unsubscribe(Subscribe):
    """ Unsubscribe
    """
    def __call__(self, *args, **kwargs):
        storage = self.storage
        if not storage:
            msg = _(u"Couldn't unsubscribe you from "
                    u"inline comments notifications")
        else:
            storage.unsubscribe()
            msg = _(u"Successfully unsubscribed you "
                    u"from inline comments notifications")
        return self._redirect(msg)
