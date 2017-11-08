""" Converter init module
"""
try:
    from eea.app.visualization import interfaces
    IGuessType = interfaces.IGuessType
except ImportError:
    from zope.interface import Interface
    class IGuessType(Interface):
        """ eea.app.visualization not installed
        """
