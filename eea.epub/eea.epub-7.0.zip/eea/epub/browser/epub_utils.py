""" Utilities for the Epub package
"""

from Acquisition import aq_base
from Products.Five import BrowserView
from Products.CMFCore.utils import getToolByName
from Products.CMFPlone import utils
from eea.epub.interfaces import IImportedBook
from eea.epub.interfaces import IImportedChapter
from eea.epub.interfaces import IImportedImage
from eea.epub.interfaces import IExportable

class EpubUtils(BrowserView):
    """ EpubUtils BrowserView
    """
    def getEbook(self):
        """ Retrieve the Ebook
        """
        obj = self.context
        portal_url = getToolByName(obj, 'portal_url')
        portal = portal_url.getPortalObject()
        while not IImportedBook.providedBy(obj) \
                and aq_base(obj) is not aq_base(portal):
            obj = utils.parent(obj)
        return obj

    def isEpubExportable(self):
        """ Boolean if Epub IExportable is provided by current context
        """
        return IExportable.providedBy(self.context)

    def isImportedEbook(self):
        """ Boolean if Epub IImportedBook is provided by current context
        """
        return IImportedBook.providedBy(self.context)

    def isImportedChapter(self):
        """ Boolean if Epub IImportedChapter is provided by current context
        """
        return IImportedChapter.providedBy(self.context)

    def isImportedImage(self):
        """ Boolean if Epub IImportedImage is provided by current context
        """
        return IImportedImage.providedBy(self.context)

    def isPartOfImportedBook(self):
        """ Boolean if content is par of the imported book
        """
        return self.isImportedEbook() \
                or self.isImportedChapter() or self.isImportedImage()

    def getEpubFormatURL(self):
        """ Returns the url of the original epub or the download.epub if
        the book is marked as isEpubExportable
        """
        if self.isPartOfImportedBook():
            ebook = self.getEbook()
            return ebook.absolute_url() + '/original.epub'
        elif self.isEpubExportable():
            return self.context.absolute_url() + '/download.epub'
        return ''
