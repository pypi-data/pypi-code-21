""" Browser Interfaces
"""
from zope.interface import Interface

class ILayer(Interface):
    """ Custom layer for this package
    """

class IExportView(Interface):
    """ IExportView interface
    """

class IImportView(Interface):
    """ IImportView interface
    """

class IEpubTocLogic(Interface):
    """ IEpubTocLogic interface
    """

    def getNavPoints():
        """ getNavPoints interface method
        """

class IEpubUtils(Interface):
    """ IEpubUtils interface
    """

    def getEpubFormatURL():
        """ getEpubFormatURL interface method
        """

    def getEbook():
        """ getEbook interface method
        """

    def isImportedEbook():
        """ isImportedEbook interface method
        """

    def isImportedChapter():
        """ isImportedChapter interface method
        """

    def isPartOfImportedBook():
        """ isPartOfImportedBook interface method
        """
