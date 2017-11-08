""" Relation required validator
"""
from zope.interface import implements
from Products.validation.interfaces.IValidator import IValidator
from Products.CMFCore.utils import getToolByName

from eea.relations.component import queryForwardRelations
from eea.relations.component import queryContentType

class Required(object):
    """ Validator
    """
    implements(IValidator)

    def __init__(self, name, title='', description=''):
        self.name = name
        self.title = title or name
        self.description = description

    def relations(self, instance):
        """ Possible relations
        """
        rtool = getToolByName(instance, 'portal_relations')
        relations = queryForwardRelations(instance)
        for relation in relations:
            field = relation.getField('required')
            if not field:
                continue
            value = field.getAccessor(relation)()
            if not value:
                continue

            to = relation.getField('to').getAccessor(relation)()
            if to not in rtool.objectIds():
                continue

            yield to

    def __call__(self, value, instance, *args, **kwargs):
        """ Validate
        """
        if not value:
            return 1

        if not isinstance(value, (tuple, list)):
            value = value,

        ctool = getToolByName(instance, 'portal_catalog')
        brains = ctool(UID={'query': value, 'operator': 'or'})

        relations = set(self.relations(instance))
        if not relations:
            return 1

        for brain in brains:
            doc = brain.getObject()
            if not doc:
                continue

            ctype = queryContentType(doc)
            if not ctype:
                continue

            name = ctype.getId()
            if name not in relations:
                continue

            relations.remove(name)

            if not relations:
                return 1

        rtool = getToolByName(instance, 'portal_relations')
        names = [rtool[rel].title_or_id() for rel in relations]
        return "Requires relations with: %s" % ', '.join(names)
