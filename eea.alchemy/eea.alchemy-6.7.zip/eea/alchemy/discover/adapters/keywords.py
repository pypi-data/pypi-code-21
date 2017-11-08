""" Auto-discover keywords
"""
import logging
from zope.interface import implements
from zope.component import getUtility
from zope.component import queryAdapter
from zope.component.hooks import getSite
from Products.CMFCore.utils import getToolByName

from eea.alchemy.config import EEAMessageFactory as _
from eea.alchemy.interfaces import IDiscoverTags
from eea.alchemy.interfaces import IDiscoverUtility
from eea.alchemy.controlpanel.interfaces import IAlchemySettings
from eea.alchemy.discover.adapters import Discover
logger = logging.getLogger('eea.alchemy')

class DiscoverTags(Discover):
    """ Common adapter to auto-discover keywords in context metadata
    """
    implements(IDiscoverTags)
    title = _(u'Keywords')

    def __init__(self, context):
        super(DiscoverTags, self).__init__(context)
        self.field = u'subject'
        self.index = u'Subject'

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

        tags = set(tag.get('text') for tag in self.tags)
        current = field.getAccessor(doc)()
        if isinstance(current, (str, unicode)):
            current = (current,)

        duplicates = set()
        for tag in tags:
            if isinstance(tag, str):
                tag = tag.decode('utf-8')
            duplicates.add(tag.lower())

        for tag in current:
            if isinstance(tag, str):
                tag = tag.decode('utf-8')
            lower = tag.lower()
            if lower in duplicates:
                continue

            tags.add(tag)
            duplicates.add(lower)

        if not set(tag.lower() for tag in tags).difference(
            set(tag.lower() for tag in current)):
            return

        tags = list(tags)
        tags.sort()
        tags = tuple(tags)

        return (tags, 'Update %s for %s. Before: %s  After:  %s' %
                (self.field, doc.absolute_url(1), current, tags))

    @property
    def existing(self):
        """ Get existing keywords from ZCatalog
        """
        ctool = getToolByName(self.context, 'portal_catalog')
        index = ctool.Indexes.get(self.index, None)
        if not index:
            return
        for value in index.uniqueValues():
            yield value

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

        string = string.strip()
        if not string:
            return

        duplicates = set()
        settings = queryAdapter(getSite(), IAlchemySettings)
        if not settings.onlyExistingKeywords:
            discover = getUtility(IDiscoverUtility, name=self.field)
            abs_url = ''
            if hasattr(self.context, "getObject"):
                abs_url = self.context.getObject().absolute_url_path()
            else:
                abs_url = self.context.absolute_url_path()

            items = discover(self.key, string, abs_url)
            for item in items:
                keyword = item.get('text')
                if not isinstance(keyword, unicode):
                    keyword = keyword.decode('utf-8')
                    item['text'] = keyword

                keyword = keyword.lower()
                if keyword in duplicates:
                    continue

                duplicates.add(keyword)
                yield item

        # Search in portal_catalog existing keywords
        for keyword in self.existing:
            if isinstance(keyword, str):
                keyword = keyword.decode('utf-8')

            lower = keyword.lower()
            if lower in duplicates:
                continue
            if lower not in string.decode('utf-8').lower():
                continue

            duplicates.add(lower)
            yield {
                'relevance': '100.0',
                'text': keyword
            }

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
