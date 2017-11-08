""" Vocabularies
"""
from zope.interface import implements
from zope.component import getAdapters, queryUtility
from zope.component.hooks import getSite
from zope.schema.vocabulary import SimpleVocabulary
from zope.schema.vocabulary import SimpleTerm
from zope.schema.interfaces import IVocabularyFactory
from eea.alchemy.interfaces import IDiscoverAdapter
from Products.CMFCore.utils import getToolByName

class DiscoverAdapters(object):
    """ Vocabulary factory for all registered Alchemy Discover Adapters
    """
    implements(IVocabularyFactory)
    _adapter = None

    def adapters(self, context):
        """ Registered adapters for IDiscoverAdapter
        """
        if not self._adapter:
            self._adapter = [a for a in getAdapters((context,),
                                                    IDiscoverAdapter)]
        return self._adapter

    def __call__(self, context=None):
        if not context:
            context = getSite()
        items = [SimpleTerm(name, name, getattr(a, 'title', name))
                 for name, a in self.adapters(context) if name]
        return SimpleVocabulary(items)

class SchemaFields(object):
    """ Get all schema fields registered for portal_types
    """
    implements(IVocabularyFactory)
    _schema = None

    def schema(self, context=None):
        """ Get schema
        """
        if self._schema:
            return self._schema

        types = getToolByName(context, 'portal_types')
        ctool = getToolByName(context, 'portal_catalog')
        res = set()
        for portal_type in types.objectIds():
            brains = ctool(portal_type=portal_type, sort_limit=1)
            if not brains:
                continue

            brain = brains[0]
            try:
                doc = brain.getObject()
            except Exception:
                continue

            schema = getattr(doc, 'Schema', None)
            if not schema:
                continue

            schema = schema()
            for field in schema.fields():
                res.add(field.getName())

        self._schema = sorted(res, key=str.lower)
        return self._schema

    def __call__(self, context=None):
        if not context:
            context = getSite()
        schema = self.schema(context)
        return SimpleVocabulary([
            SimpleTerm(field, field, field) for field in schema
        ])

class CatalogMetadata(object):
    """ Get catalog metadata
    """
    implements(IVocabularyFactory)

    def __call__(self, context=None):
        if not context:
            context = getSite()

        catalog = getToolByName(context, 'portal_catalog')
        schema = catalog.schema()
        schema.sort(key=str.lower)

        return SimpleVocabulary([
            SimpleTerm(term, term, term) for term in schema
        ])

class SchemaAndCatalog(object):
    """ Join schema fields and catalog indexes into a vocabulary
    """
    implements(IVocabularyFactory)

    def __call__(self, context=None):
        if not context:
            context = getSite()
        items = []

        # Schema
        voc = queryUtility(IVocabularyFactory,
                           name=u"eea.alchemy.vocabularies.SchemaFields")

        existing = set()
        for term in voc(context):
            existing.add(term.value)
            items.append(SimpleTerm(term.value, term.token,
                                    u'Schema: %s' % term.title))

        # Catalog
        voc = queryUtility(IVocabularyFactory,
                           name=u"eea.alchemy.vocabularies.CatalogMetadata")
        for term in voc(context):
            if term.value in existing:
                continue
            items.append(SimpleTerm(term.value, term.token,
                                    u'Catalog: %s' % term.title))
        return SimpleVocabulary(items)
