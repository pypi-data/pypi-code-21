# copyright 2015 LOGILAB S.A. (Paris, FRANCE), all rights reserved.
# contact http://www.logilab.fr -- mailto:contact@logilab.fr
#
# This program is free software: you can redistribute it and/or modify it under
# the terms of the GNU Lesser General Public License as published by the Free
# Software Foundation, either version 2.1 of the License, or (at your option)
# any later version.
#
# This program is distributed in the hope that it will be useful, but WITHOUT
# ANY WARRANTY; without even the implied warranty of MERCHANTABILITY or FITNESS
# FOR A PARTICULAR PURPOSE. See the GNU Lesser General Public License for more
# details.
#
# You should have received a copy of the GNU Lesser General Public License along
# with this program. If not, see <http://www.gnu.org/licenses/>.
"""cubicweb-saem-ref SKOS entity's classes"""

from logilab.common.decorators import cachedproperty, monkeypatch

from cubicweb.predicates import is_instance, score_entity
from cubicweb.entities import fetch_config

from cubes.skos import entities as skos
from cubes.oaipmh.entities import ETypeOAISetSpec, RelatedEntityOAISetSpec

from . import oai


@monkeypatch(skos)
def _add_concept(scheme, label, language_code, kind=u'preferred', **kwargs):
    """Overriden to set concept_scheme in transaction_data, necessary for NAA retrieval in hooks

    Once skos > 0.10 is out, may be refactored to use the original function, not done yet to
    support label's `kind` argument.
    """
    cnx = scheme._cw
    # add concept scheme to transaction data for NAA retrieval in hooks
    cnx.transaction_data['concept_scheme'] = scheme.eid
    concept = cnx.create_entity('Concept', in_scheme=scheme, **kwargs)
    cnx.create_entity('Label', label=label, language_code=language_code,
                      kind=kind, label_of=concept)
    # hooks do use existing labels, clear cache here to ensure the label is considered
    concept.cw_clear_all_caches()
    return concept


class ConceptScheme(skos.ConceptScheme):
    fetch_attrs, cw_fetch_order = fetch_config(('title', 'cwuri', 'ark',
                                                'description', 'description_format'))

    @cachedproperty
    def top_concepts_rset(self):
        rset = self._cw.execute(
            'Any C,CU,CA,CD,CE WHERE C cwuri CU, C ark CA, C definition CD, C example CE, '
            'C in_scheme X, NOT C broader_concept SC, X eid %(x)s',
            {'x': self.eid})
        if len(rset) > self._cw.property_value('navigation.page-size'):
            return rset  # optimizations below are not worth it
        # prefill 'preferred_label' relation cache for the above concepts
        labels_rset = self._cw.execute(
            'Any L,LL,LK,LLC,C ORDERBY C WHERE '
            'L label LL, L kind LK, L language_code LLC, C preferred_label L, '
            'C in_scheme X, NOT C broader_concept SC, X eid %(x)s',
            {'x': self.eid})
        entities = tuple(rset.entities())
        skos.cache_entities_relations(entities, labels_rset, 'preferred_label', 'subject',
                                      entity_col=4, target_col=0)
        narrower_rset = self._cw.execute(
            'Any C,CU,CA,CD,CE,BC ORDERBY BC WHERE '
            'C cwuri CU, C ark CA, C definition CD, C example CE, '
            'BC in_scheme X, C broader_concept BC, NOT BC broader_concept SC, X eid %(x)s',
            {'x': self.eid})
        skos.cache_entities_relations(entities, narrower_rset, 'broader_concept', 'object',
                                      entity_col=5, target_col=0)
        # return the original rset
        return rset


class Concept(skos.Concept):
    fetch_attrs, cw_fetch_order = fetch_config(('cwuri', 'ark', 'definition', 'example'))


class ConceptSchemeOAIPMHRecordAdapter(oai.OAIPMHActiveRecordAdapter):
    """OAI-PMH adapter for ConceptScheme entity type."""
    __select__ = oai.OAIPMHActiveRecordAdapter.__select__ & is_instance('ConceptScheme')
    metadata_formats = {'rdf': (oai.RDF_METADATAFORMAT, 'list.rdf')}

    @classmethod
    def set_definition(cls):
        return oai.PublicETypeOAISetSpec(
            'ConceptScheme', cls.identifier_attribute)


class ConceptInPublicSchemeETypeOAISetSpec(ETypeOAISetSpec):
    """OAI-PMH set specifier matching on "Concept" entity type and fetching
    concepts related to scheme not in "draft" state.
    """

    def __init__(self):
        super(ConceptInPublicSchemeETypeOAISetSpec, self).__init__(
            'Concept', 'ark')

    def setspec_restrictions(self, value=None):
        return 'X in_scheme Y, Y in_state ST, NOT ST name "draft"', {}


class ConceptInPublicSchemeRelatedEntityOAISetSpec(RelatedEntityOAISetSpec):
    """OAI-PMH second-level set specifier to match "Concept" entity type
    related to scheme not in "draft" state.
    """

    def __init__(self):
        super(ConceptInPublicSchemeRelatedEntityOAISetSpec, self).__init__(
            'in_scheme', 'ConceptScheme', 'ark',
            description=u'A concept in scheme identified by {0}')

    def setspecs(self, cnx):
        rset = cnx.execute('Any A WHERE X is ConceptScheme, X ark A,'
                           '            X in_state ST, NOT ST name "draft"')
        for value, in rset.rows:
            yield value, self.description.format(value)


def not_in_draft_scheme(concept):
    """Return True if `concept` is in a ConceptScheme not in "draft" state.
    """
    return concept.in_scheme[0].in_state[0].name != 'draft'


class ConceptOAIPMHRecordAdapter(oai.ArkOAIPMHRecordAdapter):
    """OAI-PMH adapter for ConceptScheme entity type."""
    __select__ = (oai.ArkOAIPMHRecordAdapter.__select__ & is_instance('Concept') &
                  score_entity(not_in_draft_scheme))
    metadata_formats = {'rdf': (oai.RDF_METADATAFORMAT, 'primary.rdf')}

    @classmethod
    def set_definition(cls):
        specifier = ConceptInPublicSchemeETypeOAISetSpec()
        specifier['in_scheme'] = ConceptInPublicSchemeRelatedEntityOAISetSpec()
        return specifier
