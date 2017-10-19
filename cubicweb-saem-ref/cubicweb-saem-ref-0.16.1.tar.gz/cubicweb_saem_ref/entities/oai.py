# copyright 2016 LOGILAB S.A. (Paris, FRANCE), all rights reserved.
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
"""cubicweb-saem-ref entity's classes for OAI-PMH protocol"""

from cubicweb.predicates import is_in_state, relation_possible, score_entity

from cubes.oaipmh import isodate, MetadataFormat
from cubes.oaipmh.entities import OAIPMHRecordAdapter, ETypeOAISetSpec, OAIComponent


# MetadataFormat instance for "rdf" with '<unknown>' schema since there
# appears to be no generic XML schema for RDF.
RDF_METADATAFORMAT = MetadataFormat(schema='<unknown>', namespace='rdf')


class SAEMOAIComponent(OAIComponent):
    """Override "oai" component to adjust ark identifier based on stored value
    (the former including the ark:/ prefix while the later does not).
    """
    deleted_handling = 'persistent'

    def match_identifier(self, identifier):
        prefix = 'ark:/'
        if identifier.startswith(prefix):
            identifier = identifier[len(prefix):]
        return super(SAEMOAIComponent, self).match_identifier(identifier)


class ArkOAIPMHRecordAdapter(OAIPMHRecordAdapter):
    """OAI-PMH Record using the "ark" attribute of entity as identifier.
    """

    __abstract__ = True
    __select__ = (OAIPMHRecordAdapter.__select__ &
                  score_entity(lambda x: hasattr(x, 'ark')))
    identifier_attribute = 'ark'

    @property
    def identifier(self):
        return 'ark:/' + self.entity.ark


def in_state(state):
    """Predicate checking for workflowability and matching on `state`.
    """
    return relation_possible('in_state') & is_in_state(state)


def not_in_state(state):
    """Predicate checking for workflowability and not matching on `state`.
    """
    return relation_possible('in_state') & ~is_in_state(state)


class OAIPMHActiveRecordAdapter(ArkOAIPMHRecordAdapter):
    """OAI-PMH Record for "active" entities (not deprecated in our application).

    See http://www.openarchives.org/OAI/2.0/openarchivesprotocol.htm#DeletedRecords
    """

    __abstract__ = True
    __select__ = ArkOAIPMHRecordAdapter.__select__ & not_in_state('deprecated')


class OAIPMHDeletedRecordAdapter(ArkOAIPMHRecordAdapter):
    """OAI-PMH Record for "deleted" entities (deprecated in our application).

    See http://www.openarchives.org/OAI/2.0/openarchivesprotocol.htm#DeletedRecords

    Handle the representation of entity with an ARK which is deleted as an
    OAI-PMH record.
    """

    __abstract__ = True
    __select__ = ArkOAIPMHRecordAdapter.__select__ & in_state('deprecated')

    @property
    def datestamp(self):
        """For delete a record, the date and time that it was deleted on.
        """
        trinfo = self.entity.cw_adapt_to('IWorkflowable').latest_trinfo()
        assert trinfo.transition.name == 'deprecate', \
            'unexpected latest transition {0}'.format(trinfo.transition)
        return isodate(trinfo.creation_date)

    deleted = True

    def metadata(self):
        return ''


class PublicETypeOAISetSpec(ETypeOAISetSpec):
    """OAI-PMH set specifier matching an entity type and entities in
    "published" or "deprecated" state.
    """

    def setspec_restrictions(self, value=None):
        """Add workflow state restrictions."""
        base, args = super(PublicETypeOAISetSpec, self).setspec_restrictions(value)
        restrictions = ', '.join([base, 'X in_state ST, NOT ST name "draft"'])
        return restrictions, args

    def query_for_identifier(self, identifier):
        qs, args = super(PublicETypeOAISetSpec, self).query_for_identifier(
            identifier)
        qs += ', X in_state ST, NOT ST name "draft"'
        return qs, args


def registration_callback(vreg):
    vreg.register_all(globals().values(), __name__, (SAEMOAIComponent,))
    vreg.register_and_replace(SAEMOAIComponent, OAIComponent)
