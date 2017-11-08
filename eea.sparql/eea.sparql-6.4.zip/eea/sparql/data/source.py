""" Sparql Data Provenances
"""

from zope.interface import implements

try:
    from eea.app.visualization.data.source import MultiDataProvenance
    from eea.app.visualization.interfaces import IMultiDataProvenance
except ImportError:
    class MultiDataProvenance(object):
        """ replacement for MultiDataProvenance from eea.app.visualization
        """
    class IMultiDataProvenance(object):
        """ replacement for IMultiDataProvenance from eea.app.visualization
        """

class SparqlMultiDataProvenance(MultiDataProvenance):
    """ Multiple Data Provenance for Sparql objects
    """
    implements(IMultiDataProvenance)

    def defaultProvenances(self):
        """ default provenances
        """
        title = self.context.title_or_id()
        link = self.context.absolute_url()
        field = self.context.getField('endpoint_url')
        owner = field.getAccessor(self.context)()
        return ({'title': title, 'link': link, 'owner': owner},)
