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
"""cubicweb-saem-ref entity's classes for exporting agents to eac"""

from cubicweb.predicates import is_instance

from cubes.oaipmh import MetadataFormat
from cubes.oaipmh.entities import RelatedEntityOAISetSpec
from cubicweb_eac import entities as eac

from . import oai


ARECORD_METADATA_FORMATS = {
    'eac': (
        MetadataFormat(
            schema='http://eac.staatsbibliothek-berlin.de/schema/cpf.xsd',
            namespace='urn:isbn:1-931666-33-4'),
        'eac.export',
    ),
}


eac.AuthorityRecord.fetch_attrs += ('ark',)


class AuthorityRecordEACAdapter(eac.AuthorityRecordEACAdapter):

    @property
    def file_name(self):
        """Return a file name for the dump."""
        if self.entity.ark:
            name = self.entity.ark.replace("/", "-")
            return u'EAC_{0}.xml'.format(name)
        return super(AuthorityRecordEACAdapter, self).file_name

    def recordid_element(self, control_elt):
        # export ark in <recordId>
        self.element('recordId', parent=control_elt, text=self.entity.ark.replace("/", "-"))
        record_id = self.entity.record_id
        if record_id:
            # export original <recordId> to <otherRecordId>
            self.element('otherRecordId', parent=control_elt, text=record_id)
        for local_type, value in self.entity.other_record_ids:
            attrs = {}
            if local_type is not None:
                attrs['localType'] = local_type
            self.element('otherRecordId', parent=control_elt, attributes=attrs,
                         text=value)

    def publication_status_element(self, control_elt):
        status = {'draft': 'inProcess', 'published': 'approved'}.get(
            self.entity.cw_adapt_to('IWorkflowable').state, 'inProcess')
        self.element('publicationStatus', parent=control_elt, text=status)

    def agent_element(self, activity, maintenance_event_elt):
        if activity.associated_with:
            agent = activity.associated_with[0].login
        else:
            agent = activity.agent
        if agent:
            self.element('agentType', maintenance_event_elt, text='human')
            self.element('agent', maintenance_event_elt, text=agent)
        else:
            super(AuthorityRecordEACAdapter, self).agent_element(activity, maintenance_event_elt)


class AuthorityRecordOAIPMHRecordAdapter(oai.OAIPMHActiveRecordAdapter):
    """OAI-PMH adapter for AuthorityRecord entity type."""
    __select__ = oai.OAIPMHActiveRecordAdapter.__select__ & is_instance('AuthorityRecord')
    metadata_formats = ARECORD_METADATA_FORMATS.copy()

    @classmethod
    def set_definition(cls):
        specifier = oai.PublicETypeOAISetSpec('AuthorityRecord', cls.identifier_attribute)
        specifier['used_by'] = RelatedEntityOAISetSpec(
            'use_authorityrecord', 'OrganizationUnit', 'ark', role='object',
            description=u'An authority record used by {0}')
        return specifier


class DeletedAuthorityRecordOAIPMHRecordAdapter(oai.OAIPMHDeletedRecordAdapter):
    """OAI-PMH adapter for deleted AuthorityRecord."""
    __select__ = oai.OAIPMHDeletedRecordAdapter.__select__ & is_instance('AuthorityRecord')
    metadata_formats = ARECORD_METADATA_FORMATS.copy()


def registration_callback(vreg):
    vreg.register_all(globals().values(), __name__, (AuthorityRecordEACAdapter,))
    vreg.register_and_replace(AuthorityRecordEACAdapter, eac.AuthorityRecordEACAdapter)
