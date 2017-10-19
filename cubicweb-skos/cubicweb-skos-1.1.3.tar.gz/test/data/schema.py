
from yams.buildobjs import RelationDefinition, EntityType
from cubicweb.schema import RQLConstraint


class inlined_match(RelationDefinition):
    subject = ('Concept', 'ExternalUri')
    object = ('Concept', 'ExternalUri')
    cardinality = '?*'
    inlined = True


class scheme_relation_type(RelationDefinition):
    subject = 'ConceptScheme'
    object = 'CWRType'
    cardinality = '**'


class Language(EntityType):
    u""""""


class language_to(RelationDefinition):
    subject = 'Language'
    object = 'Concept'
    cardinality = '?*'
    inlined = True
    constraints = [RQLConstraint('O in_scheme CS, CS scheme_relation_type CR, '
                                 'CR name "language_to"')]
