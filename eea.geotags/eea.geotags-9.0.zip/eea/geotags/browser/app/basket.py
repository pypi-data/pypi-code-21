""" Geotags popup basket
"""
from Products.Five.browser import BrowserView

class Basket(BrowserView):
    """ Geotags popup basket
    """
    _fieldName = ''

    @property
    def fieldName(self):
        """ Field name
        """
        return self._fieldName

    def __call__(self, **kwargs):
        if self.request:
            kwargs.update(self.request.form)
        self._fieldName = kwargs.get('fieldName', '')
        return self.index()
