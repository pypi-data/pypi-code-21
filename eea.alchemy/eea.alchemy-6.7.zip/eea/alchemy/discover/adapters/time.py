""" Auto-discover time periods
"""
import logging
from zope.interface import implements
from zope.component import getUtility
from eea.alchemy.interfaces import IDiscoverTime
from eea.alchemy.interfaces import IDiscoverUtility
from eea.alchemy.config import EEAMessageFactory as _
from eea.alchemy.discover.adapters import Discover
logger = logging.getLogger('eea.alchemy')

class DiscoverTime(Discover):
    """ Common adapter to auto-discover time periods in context metadata
    """
    implements(IDiscoverTime)
    title = _(u'Temporal coverage')

    def __init__(self, context):
        super(DiscoverTime, self).__init__(context)
        self.field = u'temporalCoverage'
        self.index = u'getTemporalCoverage'

    @property
    def preview(self):
        """ Discovery preview
        """
        doc = self.context
        # ZCatalog brain
        if getattr(doc, 'getObject', None):
            doc = doc.getObject()

        field = doc.getField(self.field)
        if not field:
            logger.warn('%s has no %s schema field. %s not set',
                        doc.absolute_url(1), self.field, self.title)
            return

        languageIndependent = getattr(field, 'languageIndependent', False)
        isCanonical = getattr(doc, 'isCanonical', None)
        isTranslation = not isCanonical() if isCanonical else False
        if languageIndependent and isTranslation:
            return

        mutator = field.getMutator(doc)
        if not mutator:
            logger.warn("Can't edit field %s for doc %s",
                        self.field, doc.absolute_url(1))
            return

        tags = set()
        for tag in self.tags:
            text = tag.get('text')
            if not text:
                continue
            try:
                start, end = text.split('-')
                start, end = int(start), int(end)
                tag = range(start, end+1)
            except Exception, err:
                logger.exception(err)
                continue
            else:
                tags = tags.union(tag)

        current = [int(year) for year in field.getAccessor(doc)()]
        tags = tags.union(current)
        tags = list(tags)
        tags.sort(reverse=True)
        if not set(tags).difference(current):
            return

        tags = [str(yr) for yr in tags]
        return (tags, 'Update %s for %s. Before: %s, After: %s' %
                            (self.field, doc.absolute_url(1), current, tags))

    @property
    def tags(self):
        """ Getter
        """
        doc = self.context
        getObject = getattr(doc, 'getObject', None)
        string = ""
        for prop in self.metadata:
            text = ''

            # ZCatalog brain
            if getObject:
                text = getattr(doc, prop, '')
                if not text:
                    doc = getObject()

            # ATContentType
            if not text and getattr(doc, 'getField', None):
                field = doc.getField(prop)
                if not field:
                    continue
                text = field.getAccessor(doc)()

            if not text:
                continue

            if not isinstance(text, (unicode, str)):
                continue

            string += '\n' + text

        discover = getUtility(IDiscoverUtility, name=self.field)
        if not discover:
            return

        string = string.strip()
        if not string:
            return

        for item in discover(string):
            yield item

    @tags.setter
    def tags(self, value):
        """ Setter
        """
        data = self.preview
        if not data:
            return

        tags, info = data

        doc = self.context
        if getattr(doc, 'getObject', None):
            # ZCatalog brain
            doc = doc.getObject()

        field = doc.getField(self.field)
        mutator = field.getMutator(doc)

        logger.info(info)

        mutator(tags)
        doc.reindexObject(idxs=[self.index])
