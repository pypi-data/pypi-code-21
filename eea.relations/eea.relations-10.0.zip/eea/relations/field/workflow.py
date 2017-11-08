""" Workflows
"""
from zope.interface import Interface
from zope.component import adapts
from zope.interface import implements
from eea.relations.field.interfaces import IValueProvider, IRequiredFor
from eea.relations.field import EEAReferenceField
from eea.relations.component import queryForwardRelations
from eea.relations.component import queryContentType

class ValueProvider(object):
    """ Adapter to check if field has value and get value according with defined
    possible content relations
    """
    implements(IValueProvider)
    adapts(Interface, EEAReferenceField)

    def __init__(self, context, field):
        self.context = context
        self.field = field

    def relations(self, state):
        """ Relations
        """
        relations = queryForwardRelations(self.context)
        for relation in relations:
            field = relation.getField('required_for')
            if not field:
                continue
            value = field.getAccessor(relation)()
            if not value:
                continue
            if state not in value:
                continue

            to = relation.getField('to')
            if not to:
                continue
            yield to.getAccessor(relation)()

    def has_value(self, **kwargs):
        """ Has value?
        """
        state = kwargs.get('state', None)
        value = self.get_value(**kwargs)
        if not state:
            return bool(value)

        relations = set(rel for rel in self.relations(state))
        for doc in value:
            ctype = queryContentType(doc)
            if not ctype:
                continue
            name = ctype.getId()
            if name not in relations:
                continue
            relations.remove(name)

        if not relations:
            return True
        return False

    def get_value(self, **kwargs):
        """ Get value
        """
        return self.field.getAccessor(self.context)()

class RequiredFor(object):
    """ Adapter to check if field is required for a given state
    """
    implements(IRequiredFor)
    adapts(Interface, EEAReferenceField)

    def __init__(self, context, field):
        self.context = context
        self.field = field

    def required_for(self, state):
        """ Lookup possible context relations
        """
        relations = queryForwardRelations(self.context)
        for relation in relations:
            field = relation.getField('required_for')
            if not field:
                continue
            value = field.getAccessor(relation)()
            if not value:
                continue
            if state in value:
                return True
        return False

    def required_for_attr(self, state):
        """ Lookup field attributes
        """
        ATTR = 'required_for_' + state
        return getattr(self.field, ATTR, False)

    def __call__(self, state, **kwargs):
        """ Lookup relations then fallback to field attributes
        """
        return self.required_for(state) or self.required_for_attr(state)
