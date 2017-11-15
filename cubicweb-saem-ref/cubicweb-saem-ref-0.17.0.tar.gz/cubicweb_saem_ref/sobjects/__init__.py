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
"""cubicweb-saem-ref server objects"""

from six.moves import map as imap

from cubicweb.predicates import match_user_groups, match_kwargs
from cubicweb.server import Service
from cubicweb.dataimport.stores import MetadataGenerator

from cubicweb_eac import sobjects as eac

from .. import user_has_naa
from ..hooks import set_ark_and_cwuri


class SAEMMetadataGenerator(MetadataGenerator):
    """SAEM specific metadata generator, necessary when no hooks are activated (e.g. skos import) to
    handle ARK generation and setting of the initial state.
    """

    def __init__(self, cnx, baseurl=None, source=None, naa_what=None):
        super(SAEMMetadataGenerator, self).__init__(cnx, baseurl, source)
        if naa_what is None and source is not None:
            source_entity = cnx.find('CWSource', eid=source.eid).one()
            if source_entity.reverse_through_cw_source:
                skos_source = source_entity.reverse_through_cw_source[0]
                if skos_source.ark_naa:
                    naa_what = skos_source.ark_naa[0].what
        self.naa_what = naa_what

    def etype_rels(self, etype):
        etype_rels = super(SAEMMetadataGenerator, self).etype_rels(etype)
        if etype == 'ConceptScheme':
            etype_rels.append('in_state')
        return etype_rels

    def gen_in_state(self, etype):
        wf_state = self._cnx.execute('Any S WHERE ET default_workflow WF, ET name %(etype)s, '
                                     'WF initial_state S', {'etype': etype}).one()
        return wf_state.eid

    def entity_attrs(self, etype):
        entity_attrs = super(SAEMMetadataGenerator, self).entity_attrs(etype)
        if etype in ('ConceptScheme', 'Concept', 'AuthorityRecord', 'Agent'):
            entity_attrs.insert(0, 'ark')  # insert before cwuri
        return entity_attrs

    def gen_ark(self, etype, eid, attrs):
        """ARK generation callback"""
        set_ark_and_cwuri(self._cnx, eid, etype, attrs, naa_what=self.naa_what)
        # returning value, even if set by the function, is necessary due to the meta generator
        # implementation
        return attrs['ark']


class EACImportService(eac.EACImportService):
    """Service to import an AuthorityRecord from an EAC XML file - overriden from the EAC cube to
    adapt selector and automatically set ark_naa / authority relations.
    """

    __select__ = eac.EACImportService.__select__ & (match_kwargs('authority') | user_has_naa())

    def import_eac_stream(self, stream, import_log, store, extid2eid=None, naa=None, **kwargs):
        authority = self.cw_extra_kwargs.get('authority')
        if authority is None:
            authority = self._cw.user.authority[0]
        if naa is None:
            naa = authority.ark_naa[0]
        self._authority = authority
        self._naa = naa
        return super(EACImportService, self).import_eac_stream(stream, import_log, store,
                                                               extid2eid=extid2eid, **kwargs)

    def external_entities_stream(self, extentities, extid2eid):
        extentities = super(EACImportService, self).external_entities_stream(extentities, extid2eid)

        extid2eid[self._naa.cwuri] = self._naa.eid
        extid2eid[self._authority.cwuri] = self._authority.eid

        def set_authority_or_naa(extentity):
            """insert function to set parent authority in the ext-entities stream"""
            if extentity.etype == 'AuthorityRecord':
                extentity.values['ark_naa'] = set([self._naa.cwuri])
            elif extentity.etype == 'Agent':
                extentity.values['authority'] = set([self._authority.cwuri])
            return extentity

        return imap(set_authority_or_naa, extentities)


class AllocateArk(Service):
    """Service to allocate an ark identifier given an
    ArkNameAssigningAuthority entity.
    """
    __regid__ = 'saem.attribute-ark'
    __select__ = match_user_groups('managers', 'users')

    def call(self, naa):
        generator = self._cw.vreg['adapters'].select('IARKGenerator', self._cw,
                                                     naa_what=naa.what)
        return generator.generate_ark()


def registration_callback(vreg):
    vreg.register_all(globals().values(), __name__, [EACImportService])
    vreg.register_and_replace(EACImportService, eac.EACImportService)
