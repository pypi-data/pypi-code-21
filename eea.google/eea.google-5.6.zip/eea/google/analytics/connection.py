""" connection module """

from zope.interface import implements
from eea.google.api import Connection
from eea.google.analytics.interfaces import IGoogleAnalyticsConnection

class GoogleAnalyticsConnection(object):
    """ Access Google Analytics
    """
    implements(IGoogleAnalyticsConnection)

    def __call__(self, token):
        self.connection = Connection(token)
        return self.connection
