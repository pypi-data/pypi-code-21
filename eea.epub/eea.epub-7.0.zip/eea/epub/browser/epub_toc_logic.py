""" Epub Table of contents logic Browserview
"""
from zope.annotation.interfaces import IAnnotations
from Products.Five import BrowserView

class EpubTocLogic(BrowserView):
    """ EpubTocLogic BrowserView
    """
    def getNavPoints(self):
        """ Retrieves the epub's Navigation Points
        """
        utils = self.context.restrictedTraverse('@@epub_utils')
        ebook = utils.getEbook()
        annotations = IAnnotations(ebook)
        mapping = annotations.get('eea.epub')
        return mapping['toc']
