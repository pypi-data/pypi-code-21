""" Google Tool pages
"""
from Products.Five import BrowserView
from Products.statusmessages.interfaces import IStatusMessage

class GoogleToolView(BrowserView):
    """ Browser view
    """
    def _redirect(self, msg):
        """ Add status message and redirect back to context
        """
        if self.request:
            url = self.context.absolute_url()
            IStatusMessage(self.request).addStatusMessage(msg, type='info')
            self.request.response.redirect(url)
        return msg

    def remove(self, **kwargs):
        """ Remove connection
        """
        if self.request:
            kwargs.update(self.request.form)

        conn_id = kwargs.get('id', '')
        if not conn_id or conn_id not in self.context.objectIds():
            return self._redirect('Invalid id: %s' % conn_id)

        self.context.manage_delObjects(ids=[conn_id, ])
        return self._redirect('Connection deleted')
