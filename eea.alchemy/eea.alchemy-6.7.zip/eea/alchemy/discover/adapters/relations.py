""" Auto-discover relatedItems
"""
import logging
from zope.interface import implements
from zope.component import getUtility
from zope.component.hooks import getSite
from zope.browser.interfaces import IBrowserView
from zope.pagetemplate.interfaces import IPageTemplate
from Products.GenericSetup.PythonScripts.interfaces import IPythonScript
from Products.CMFCore.FSPythonScript import FSPythonScript
from plone.uuid.interfaces import IUUID
from plone import api
from eea.alchemy.interfaces import IDiscoverRelatedItems
from eea.alchemy.interfaces import IDiscoverUtility
from eea.alchemy.config import EEAMessageFactory as _
from eea.alchemy.discover.adapters import Discover
from eea.alchemy.relations import canRelate
logger = logging.getLogger('eea.alchemy')


class DiscoverRelatedItems(Discover):
    """ Common adapter to auto-discover related items in context metadata
    """
    implements(IDiscoverRelatedItems)
    title = _(u'Related items')

    def __init__(self, context):
        super(DiscoverRelatedItems, self).__init__(context)
        self.field = 'relatedItems'
        self.index = 'relatedItems'
        self._tags = []

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

        current = [IUUID(obj, None) for obj in field.getAccessor(doc)()]
        tags = [tag.get('text') for tag in self.tags]

        if not set(tags).difference(current):
            return

        # Preserve current tags
        for tag in current:
            if tag not in tags:
                tags.append(tag)

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

        string = string.strip()
        if not string:
            return

        site = getSite().absolute_url()
        if getObject:
            doc = getObject()

        myuid = IUUID(doc, None)

        discovered = set()
        discover = getUtility(IDiscoverUtility, name=u'links')
        if discover:
            try:
                discovered.update(x.get('text')
                                  for x in discover(string, match=site))
            except Exception, err:
                logger.exception("%s while discovering items on: %s",
                                err, doc.absolute_url_path())

        discover = getUtility(IDiscoverUtility, name=u'iframes')
        if discover:
            try:
                discovered.update(x.get('text')
                                  for x in discover(string, match=site))
            except Exception, err:
                logger.exception("%s while discovering items on: %s",
                                err, doc.absolute_url_path())

        uids = set()
        for text in discovered:
            if text.startswith('resolveuid/'):
                uid = text.split('/')[1]
                if uid == myuid:
                    continue

                if canRelate(doc, uid=uid):
                    if uid in uids:
                        continue

                    uids.add(uid)
                    yield {
                        'count': 1,
                        'type': 'Link',
                        'text': uid,
                        'relevance': '100.0'
                    }
                    continue

            nav_root = api.portal.get_navigation_root(doc)
            nav_root_path = '/'.join(nav_root.getPhysicalPath())

            obj = doc.unrestrictedTraverse(text, None)
            if obj is None:
                obj = doc.unrestrictedTraverse(nav_root_path + '/' + text, None)

            if obj is None:
                err = "No object found"
                logger.warn("%s while trying "
                                 "doc.unrestrictedTraverse(text)"
                                 "with doc: %s    text: %s",
                                 err, doc.absolute_url_path(), text)
                continue
            else:
                if IBrowserView.providedBy(obj):
                    obj = obj.context
                elif (IPageTemplate.providedBy(obj) or
                      IPythonScript.providedBy(obj) or
                      isinstance(obj, FSPythonScript)):
                    obj = obj.getParentNode()

                if not canRelate(doc, obj):
                    continue

                uid = IUUID(obj, None)
                if not uid:
                    continue

                if uid == myuid:
                    continue

                if uid in uids:
                    continue

                uids.add(uid)
                yield {
                    'count': 1,
                    'type': 'Link',
                    'text': uid,
                    'relevance': '100.0'
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
