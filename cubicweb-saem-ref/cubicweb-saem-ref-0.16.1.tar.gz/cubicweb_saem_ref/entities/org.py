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
"""cubicweb-saem-ref entity's classes for Organization and its associated classes (mainly
OrganizationUnit and Agent)
"""

from cubicweb.predicates import is_instance
from cubicweb.entities import AnyEntity, fetch_config

from cubes.oaipmh.entities import ETypeOAISetSpec, RelatedEntityOAISetSpec

from . import oai


class Organization(AnyEntity):
    __regid__ = 'Organization'
    fetch_attrs, cw_fetch_order = fetch_config(('name', 'ark'))


class Agent(AnyEntity):
    __regid__ = 'Agent'
    fetch_attrs, cw_fetch_order = fetch_config(('name', 'ark'))


class OrganizationUnit(AnyEntity):
    __regid__ = 'OrganizationUnit'
    fetch_attrs, cw_fetch_order = fetch_config(('name', 'ark'))

    def has_role(self, role):
        """Return True if the unit has the archival role `role` else False"""
        return any(archival_role for archival_role in self.archival_role
                   if archival_role.name == role)


class ArchivalRole(AnyEntity):
    __regid__ = 'ArchivalRole'
    fetch_attrs, cw_fetch_order = fetch_config(('name',))


ORG_METADATA_FORMATS = {'rdf': (oai.RDF_METADATAFORMAT, 'primary.rdf')}


class OrganizationOAIPMHRecordAdapter(oai.ArkOAIPMHRecordAdapter):
    """OAI-PMH adapter for Organization entity type."""
    __select__ = (oai.ArkOAIPMHRecordAdapter.__select__
                  & is_instance('Organization'))
    metadata_formats = ORG_METADATA_FORMATS.copy()

    @classmethod
    def set_definition(cls):
        return ETypeOAISetSpec(
            'Organization', identifier_attribute=cls.identifier_attribute)


class OrganizationUnitOAIPMHRecordAdapter(oai.OAIPMHActiveRecordAdapter):
    """OAI-PMH adapter for OrganizationUnit entity type."""
    __select__ = (oai.OAIPMHActiveRecordAdapter.__select__
                  & is_instance('OrganizationUnit'))
    metadata_formats = ORG_METADATA_FORMATS.copy()

    @classmethod
    def set_definition(cls):
        specifier = oai.PublicETypeOAISetSpec(
            'OrganizationUnit',
            identifier_attribute=cls.identifier_attribute)
        specifier['role'] = RelatedEntityOAISetSpec(
            'archival_role', 'ArchivalRole', 'name',
            description=u'An organization unit with {0} archival role')
        return specifier


class DeletedOrganizationUnitOAIPMHRecordAdapter(oai.OAIPMHDeletedRecordAdapter):
    """OAI-PMH adapter for deleted OrganizationUnit."""
    __select__ = (oai.OAIPMHDeletedRecordAdapter.__select__
                  & is_instance('OrganizationUnit'))
    metadata_formats = ORG_METADATA_FORMATS.copy()


class AgentOAIPMHRecordAdapter(oai.OAIPMHActiveRecordAdapter):
    """OAI-PMH adapter for Agent entity type."""
    __select__ = (oai.OAIPMHActiveRecordAdapter.__select__
                  & is_instance('Agent'))
    metadata_formats = ORG_METADATA_FORMATS.copy()

    @classmethod
    def set_definition(cls):
        return oai.PublicETypeOAISetSpec(
            'Agent',
            identifier_attribute=cls.identifier_attribute)


class DeletedAgentOAIPMHRecordAdapter(oai.OAIPMHDeletedRecordAdapter):
    """OAI-PMH adapter for deleted Agent."""
    __select__ = (oai.OAIPMHDeletedRecordAdapter.__select__
                  & is_instance('Agent'))
    metadata_formats = ORG_METADATA_FORMATS.copy()
