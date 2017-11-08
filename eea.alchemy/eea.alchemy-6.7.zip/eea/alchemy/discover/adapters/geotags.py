""" Auto-discover geotags API
"""
import logging
from zope.interface import implements
from zope.component import getUtility

from eea.alchemy.interfaces import IDiscoverGeoTags
from eea.alchemy.interfaces import IDiscoverUtility
from eea.alchemy.discover.adapters import Discover
from eea.alchemy.config import EEAMessageFactory as _

logger = logging.getLogger('eea.alchemy')

class DiscoverGeoTags(Discover):
    """ Common adapter to auto-discover geotags in context metadata
    """
    implements(IDiscoverGeoTags)
    title = _(u'Geographical coverage')

    def __init__(self, context):
        super(DiscoverGeoTags, self).__init__(context)
        self.field = u'location'
        self.index = u'location'

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

        current = field.getAccessor(doc)()
        if current and isinstance(current, (str, unicode)):
            # Location already set, skip as we don't want to mess it
            return

        tags = set(tag.get('text') for tag in self.tags)
        if current:
            if isinstance(current, (str, unicode)):
                tags.add(current)
            else:
                tags = tags.union(current)

        if not tags:
            return

        tags = list(tags)
        tags.sort()
        if isinstance(current, (str, unicode)):
            tags = ', '.join(tags)

        return (tags, 'Update %s for %s. Before: %s  After: %s' %
                        (self.field, doc.absolute_url(1), current, tags))

    @property
    def tags(self):
        """ Getter
        """
        if not self.key:
            return

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

        abs_url = ''
        if hasattr(self.context, "getObject"):
            abs_url = self.context.getObject().absolute_url_path()
        else:
            abs_url = self.context.absolute_url_path()
        for item in discover(self.key, string, abs_url):
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
