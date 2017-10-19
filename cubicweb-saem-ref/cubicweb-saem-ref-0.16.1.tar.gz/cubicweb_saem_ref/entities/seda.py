#  coding: utf-8
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
"""cubicweb-saem-ref entity's classes and adapters for SEDA classes"""

from logilab.common.decorators import monkeypatch

from cubicweb.predicates import is_instance, is_in_state

from cubes.oaipmh import MetadataFormat
from cubes.oaipmh.entities import OAISetSpec
from cubicweb_seda.entities import SEDAArchiveTransferIClonableAdapter
from cubicweb_seda.entities.custom import SEDAArchiveTransfer
from cubicweb_seda.entities.profile_generation import SEDA2ExportAdapter, SEDA1XSDExport
from cubicweb_seda.views import export

from .. import cwuri_url
from . import oai


# monkeypatch cwuri_url method instead of subclassing and replacing adapters because there are 5 of
# them impacted (SEDA 2 rng, 1/0.2 rng/xsd) while we may change it once for all on the common base
# class
SEDA2ExportAdapter.cwuri_url = staticmethod(cwuri_url)


# hijack xsd_archival_agreement to insert profile as well. Use a monkey-patch rather than new
# implementation to avoid doing it twice, once for SEDA 1 another for SEDA 0.2

orig_xsd_archival_agreement = SEDA1XSDExport.xsd_archival_agreement


@monkeypatch(SEDA1XSDExport)
def xsd_archival_agreement(self, parent, transfer):
    orig_xsd_archival_agreement(self, parent, transfer)
    self.element_schema(parent, 'ArchivalProfile', 'qdt:ArchivesIDType',
                        fixed_value=u'ark:/' + transfer.ark)


# override agency_id to return ark instead of eid
@monkeypatch(SEDA1XSDExport)
def agency_id(self, agency):
    return None if agency.agency is None else 'ark:/' + agency.agency.ark


SEDAArchiveTransferIClonableAdapter.__select__ &= is_in_state('published')
SEDAArchiveTransferIClonableAdapter.rtype = 'new_version_of'
SEDAArchiveTransferIClonableAdapter.skiprtypes += ('clone_of',)


class SEDAArchiveTransfer(SEDAArchiveTransfer):
    SEDAArchiveTransfer.fetch_attrs.append('ark')

    def __getstate__(self):
        # Exclude ark from copy to have so that it can be generated for the clone
        odict = self.__dict__.copy()
        odict['cw_attr_cache'].pop('ark', None)
        return odict

    @property
    def predecessor(self):
        """The predecessor of the current profile, that is the one that has been replaced by it"""
        predecessors = self.new_version_of
        if predecessors:
            return predecessors[0]
        return None

    @property
    def successor(self):
        """The successor of the current profile, that is the one that has replaced it"""
        successors = self.reverse_new_version_of
        if successors:
            return successors[0]
        return None


class TransferringAgentOAISetSpec(OAISetSpec):
    """OAI-PMH set specifier to match SEDAArchiveTransfer related to a transferring
    agent.
    """

    def setspecs(self, cnx):
        rset = cnx.execute(
            'Any A WHERE X archival_role R, R name "deposit", X ark A')
        desc = 'SEDA Profile used by organization {0}'
        for value, in rset.rows:
            yield value, desc.format(value)

    def setspec_restrictions(self, value):
        qs = ('A use_profile X, A archival_role R'
              ', R name "deposit", A ark %(value)s'
              ', X in_state ST, NOT ST name "draft"')
        return qs, {'value': value}


PROFILE_METADATA_FORMATS = {
    'seda02xsd': (
        MetadataFormat(
            schema='https://www.w3.org/2001/XMLSchema.xsd',
            namespace='http://www.w3.org/2001/XMLSchema'),
        'saem.oai.seda.0.2-xsd',
    ),
    'seda02rng': (
        MetadataFormat(
            schema='http://relaxng.org/relaxng.xsd',
            namespace='http://www.w3.org/2001/XMLSchema'),
        'saem.oai.seda.0.2-rng',
    ),
    'seda1rng': (
        MetadataFormat(
            schema='http://relaxng.org/relaxng.xsd',
            namespace='http://www.w3.org/2001/XMLSchema'),
        'saem.oai.seda.1.0-rng',
    ),
    'seda2rng': (
        MetadataFormat(
            schema='http://relaxng.org/relaxng.xsd',
            namespace='http://www.w3.org/2001/XMLSchema'),
        'saem.oai.seda.2.0-rng',
    ),
}


class SEDAArchiveTransferOAIPMHRecordAdapter(oai.OAIPMHActiveRecordAdapter):
    """OAI-PMH adapter for SEDAArchiveTransfer entity type."""
    __select__ = oai.OAIPMHActiveRecordAdapter.__select__ & is_instance('SEDAArchiveTransfer')
    metadata_formats = PROFILE_METADATA_FORMATS.copy()

    @classmethod
    def set_definition(cls):
        specifier = oai.PublicETypeOAISetSpec(
            'SEDAArchiveTransfer', cls.identifier_attribute, 'profile')
        specifier['transferring_agent'] = TransferringAgentOAISetSpec()
        return specifier


class DeletedSEDAArchiveTransferOAIPMHRecordAdapter(oai.OAIPMHDeletedRecordAdapter):
    """OAI-PMH adapter for deleted SEDAArchiveTransfer."""
    __select__ = oai.OAIPMHDeletedRecordAdapter.__select__ & is_instance('SEDAArchiveTransfer')
    metadata_formats = PROFILE_METADATA_FORMATS.copy()


class OAISEDAExportView(export.SEDAExportView):
    __abstract__ = True

    def call(self):
        version, format = self.__regid__.replace('saem.oai.seda.', '').split('-')
        self._cw.view('seda.export', rset=self.cw_rset, version=version, format=format, w=self.w)


class OAISEDA02XSDExportView(OAISEDAExportView):
    __regid__ = 'saem.oai.seda.0.2-xsd'


class OAISEDA02RNGExportView(OAISEDAExportView):
    __regid__ = 'saem.oai.seda.0.2-rng'


class OAISEDA1RNGExportView(OAISEDAExportView):
    __regid__ = 'saem.oai.seda.1.0-rng'


class OAISEDA2RNGExportView(OAISEDAExportView):
    __regid__ = 'saem.oai.seda.2.0-rng'
