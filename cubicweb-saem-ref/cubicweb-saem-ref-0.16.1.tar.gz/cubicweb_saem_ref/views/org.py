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
"""cubicweb-saem-ref views for organization-like entities (Organization, OrganizationUnit and
Agent types)
"""

from six import text_type

from cubicweb import tags, _
from cubicweb.predicates import is_instance, match_kwargs, relation_possible
from cubicweb.view import EntityView
from cubicweb.uilib import js
from cubicweb.web import formwidgets as fw
from cubicweb.web.views import ajaxcontroller, tabs, uicfg

from cubes.relationwidget import views as rwdg

from . import (SubviewsTabView, RelatedEntitiesListView,
               configure_relation_widget, dropdown_button, has_rel_perm)


affk = uicfg.autoform_field_kwargs
afs = uicfg.autoform_section
abaa = uicfg.actionbox_appearsin_addmenu
pvs = uicfg.primaryview_section
pvds = uicfg.primaryview_display_ctrl
rdc = uicfg.reledit_ctrl


def authority_form_value(form, field):
    """Field default value function returning the current user's authority or None"""
    if form._cw.user.authority:
        return (text_type(form._cw.user.authority[0].eid),)
    return []


pvs.tag_subject_of(('*', 'authority', '*'), 'attributes')
afs.tag_subject_of(('*', 'authority', '*'), 'main', 'attributes')
affk.tag_subject_of(('*', 'authority', '*'), {'value': authority_form_value})

pvs.tag_subject_of(('*', 'authority_record', '*'), 'attributes')
afs.tag_subject_of(('*', 'authority_record', '*'), 'main', 'attributes')
affk.tag_subject_of(('*', 'authority_record', '*'),
                    {'widget': rwdg.RelationFacetWidget(dialog_options={'width': 800})})

for etype, attr in (
    ('Organization', 'ark'),
    ('Organization', 'name'),
    ('OrganizationUnit', 'ark'),
    ('OrganizationUnit', 'name'),
    ('Agent', 'ark'),
    ('Agent', 'name'),
):
    affk.set_field_kwargs(etype, attr, widget=fw.TextInput({'size': 80}))
    if attr == 'ark':
        affk.set_field_kwargs(etype, attr, required=False)


# Organization

pvs.tag_object_of(('*', 'authority', 'Organization'), 'hidden')
pvs.tag_subject_of(('Organization', 'archival_authority', '*'), 'hidden')
afs.tag_object_of(('*', 'authority', 'Organization'), 'main', 'hidden')
abaa.tag_object_of(('*', 'authority', 'Organization'), False)
pvs.tag_subject_of(('Organization', 'archival_unit', '*'), 'attributes')
pvs.tag_subject_of(('Organization', 'ark_naa', 'ArkNameAssigningAuthority'), 'attributes')
afs.tag_subject_of(('Organization', 'ark_naa', 'ArkNameAssigningAuthority'), 'main', 'attributes')
afs.tag_subject_of(('Organization', 'archival_unit', '*'), 'main', 'attributes')


class OrganizationTabbedPrimaryView(tabs.TabbedPrimaryView):
    """Tabbed primary view for Organization entity type."""
    __select__ = tabs.TabbedPrimaryView.__select__ & is_instance('Organization')
    tabs = [
        'main_tab',
        _('saem_org_orgunit_tab'),
        _('saem_org_agent_tab'),
    ]


class OrganizationUnitTab(SubviewsTabView):
    __regid__ = 'saem_org_orgunit_tab'
    __select__ = SubviewsTabView.__select__ & is_instance('Organization')
    relations_info = [
        ('authority', 'object', 'OrganizationUnit'),
    ]
    subvids = (
        'saem.org.organizationunits',
    )


class AgentTab(OrganizationUnitTab):
    __regid__ = 'saem_org_agent_tab'
    relations_info = [
        ('authority', 'object', 'Agent'),
    ]
    subvids = (
        'saem.org.agents',
    )


class OrganizationRelatedOrganizationUnitListView(RelatedEntitiesListView):
    __regid__ = 'saem.org.organizationunits'
    rtype = 'authority'
    role = 'object'
    target_etype = 'OrganizationUnit'

    _('creating Agent (Agent authority Organization %(linkto)s)')

    @property
    def title(self):
        return None


class OrganizationRelatedAgentListView(OrganizationRelatedOrganizationUnitListView):
    __regid__ = 'saem.org.agents'
    target_etype = 'Agent'

    _('creating OrganizationUnit (OrganizationUnit authority Organization %(linkto)s)')


# OrganizationUnit

class LinkedObjectsTab(SubviewsTabView):
    """Abstract class for tab displaying objects related through non-composite relation.

    Parametrized using:

    * `required_role`, the archival role required to edit the relation ;

    * `not_possible_msg`, the message to be displayed when the organisation unit doesn't have the
      role ;

    * `link_targets`, list of 3-uple (entity type, relation type, role) to be displayed.
    """
    __abstract__ = True
    required_role = None
    not_possible_msg = None
    link_targets = ()

    def entity_call(self, entity):
        self.w(u'<div id="%s%s">' % (self.__regid__, entity.eid))
        rtype, role = self.link_targets[0][1:]
        if (not entity.has_role(self.required_role)
                and has_rel_perm('add', entity, rtype, role)):
            msg = self._cw._(self.not_possible_msg)
            self.w('<div class="alert alert-warning">%s</div>' % msg)
        else:
            self.generate_add_button(entity)
        super(LinkedObjectsTab, self).entity_call(entity)
        self.w(u'</div>')

    def generate_add_button(self, entity):
        """Add html for the add button on the right hand corner of the tab, if the logged user may
        add some relation.
        """
        divid = "relatedentities%s" % entity.eid
        links = []
        for etype, rtype, role in self.link_targets:
            if not has_rel_perm('add', entity, rtype, role, target_etype=etype):
                continue
            relation = '%s:%s:%s' % (rtype, etype, role)
            search_url = self._cw.build_url('ajax', fname='view', vid='search_related_entities',
                                            eid=entity.eid,
                                            __modal=1, multiple='1', relation=relation)
            title = (self._cw._('Search %s to link to the organization unit')
                     % self._cw.__(etype + '_plural').lower())
            validate = js.saem.buildRelationValidate(entity.eid, rtype, role, self.__regid__)
            url = configure_relation_widget(self._cw, divid, search_url, title, True, validate)
            links.append(tags.a(self._cw._(etype), href=url, klass=''))
        if links:
            rwdg.bootstrap_dialog(self.w, self._cw._, divid)
            self.w(tags.div(id=divid, style='display: none'))
            self.w(dropdown_button(self._cw._('add'), links))
            self.w(tags.div(klass='clearfix'))


class RTypeListView(RelatedEntitiesListView):
    """List of related entities the organization unit is using.

    Slightly different from default RelatedEntitiesListView behaviour:

    * only include button delete the relation (not the entity),
    * give extra arguments so the permission to delete the relation is checked.
    """
    __abstract__ = True
    tabid = None

    @property
    def subvid_kwargs(self):
        entity = self.cw_rset.one()
        return {'unit': entity, '__redirectpath': entity.rest_path(),
                'rtype': self.rtype, 'role': self.role, 'tabid': self.tabid}


class OrganizationUnitUsingListItemView(EntityView):
    """Extended 'oneline' view for entities related to an organization unit, including link to
    remove the relation.
    """
    __regid__ = 'saem.listitem'
    __select__ = EntityView.__select__ & match_kwargs('unit', 'rtype', 'role', 'tabid')

    # XXX usually expect role to be the role of the entity, here it's the role of the organization
    # unit
    def entity_call(self, entity, unit, rtype, role, tabid, **editurlparams):
        entity.view('outofcontext', w=self.w)
        if has_rel_perm('delete', unit, rtype, role, target_entity=entity):
            self._cw.add_js(('cubicweb.ajax.js', 'cubes.saem_ref.js'))
            self.w(u'<div class="pull-right">')
            jscall = js.saem.ajaxRemoveRelation(unit.eid, entity.eid, rtype, role, tabid)
            self.w(tags.a(title=self._cw._('delete'), klass='icon-trash',
                          href='javascript: %s' % jscall))
            self.w(u'</div>')


class OrganizationUnitSearchForRelatedEntitiesView(rwdg.SearchForRelatedEntitiesView):
    __select__ = (rwdg.SearchForRelatedEntitiesView.__select__
                  & (rwdg.edited_relation('use_profile')
                     | rwdg.edited_relation('related_concept_scheme')
                     | rwdg.edited_relation('use_authorityrecord')))
    has_creation_form = False

    def linkable_rset(self):
        """Return rset of entities to be displayed as possible values for the edited relation. You
        may want to override this.
        """
        entity = self.compute_entity()
        rtype, tetype, role = self._cw.form['relation'].split(':')
        return entity.unrelated(rtype, tetype, role, ordermethod='fetch_order')


# cw provide delete_relation and add_relation. Implements add_relations because it's easy but we
# could do it using several call to add_relation
@ajaxcontroller.ajaxfunc
def add_relations(self, eid, rtype, role, related_eids):
    """Add relation `rtype` between `eid` with role `role` and `related_eid`."""
    rql = 'SET S {rtype} O WHERE S eid %(eids)s, O eid %(eido)s'.format(rtype=rtype)
    for related_eid in related_eids:
        self._cw.execute(rql, {'eids': eid if role == 'subject' else int(related_eid),
                               'eido': eid if role == 'object' else int(related_eid)})


pvs.tag_subject_of(('OrganizationUnit', 'archival_role', '*'), 'attributes')
afs.tag_subject_of(('OrganizationUnit', 'archival_role', '*'), 'main', 'attributes')
afs.tag_object_of(('*', 'archival_unit', 'OrganizationUnit'), 'main', 'hidden')
# archival_role is used in constraints for archival_agent and use_profile relations
rdc.tag_attribute(('OrganizationUnit', 'archival_role'), {'reload': True})
pvs.tag_subject_of(('OrganizationUnit', 'contact_point', '*'), 'attributes')
afs.tag_subject_of(('OrganizationUnit', 'contact_point', '*'), 'main', 'attributes')

pvs.tag_subject_of(('*', 'related_concept_scheme', '*'), 'hidden')
afs.tag_subject_of(('*', 'related_concept_scheme', '*'), 'main', 'hidden')
pvs.tag_object_of(('*', 'related_concept_scheme', '*'), 'hidden')
afs.tag_object_of(('*', 'related_concept_scheme', '*'), 'main', 'hidden')
abaa.tag_object_of(('*', 'related_concept_scheme', '*'), False)

for rtype in ('use_profile', 'use_authorityrecord'):
    pvs.tag_subject_of(('*', rtype, '*'), 'hidden')
    afs.tag_subject_of(('*', rtype, '*'), 'main', 'hidden')
    abaa.tag_subject_of(('*', rtype, '*'), False)


class OrganizationUnitTabbedPrimaryView(tabs.TabbedPrimaryView):
    """Tabbed primary view for OrganizationUnit"""
    __select__ = tabs.TabbedPrimaryView.__select__ & is_instance('OrganizationUnit')
    tabs = [
        'main_tab',
        _('saem_ou_concepts_profiles_tab'),
        _('saem_ou_authorityrecords_tab'),
    ]


class DepositOrganizationUnitConceptsProfilesTab(LinkedObjectsTab):
    """SEDA profiles and concept schemes used by an organization unit with role "deposit"."""
    __regid__ = 'saem_ou_concepts_profiles_tab'
    __select__ = EntityView.__select__ & is_instance('OrganizationUnit')
    required_role = 'deposit'
    not_possible_msg = _("You can't add profiles or concept schemes to organization unit "
                         "without the 'deposit' role.")
    link_targets = [('SEDAArchiveTransfer', 'use_profile', 'subject'),
                    ('ConceptScheme', 'related_concept_scheme', 'subject')]
    subvids = (
        'saem.ou.schemes',
        'saem.ou.profiles',
    )


class OrganizationUnitUsingConceptSchemeListView(RTypeListView):
    """View for ConceptScheme, to be displayed in the context of an organization unit."""
    __regid__ = 'saem.ou.schemes'
    rtype = 'related_concept_scheme'
    role = 'subject'
    tabid = 'saem_ou_concepts_profiles_tab'


class RelatedSEDAArchiveTransferListView(RTypeListView):
    """View for SEDAArchiveTransfer, to be displayed in the context of an organization unit."""
    __regid__ = 'saem.ou.profiles'
    rtype = 'use_profile'
    role = 'subject'
    tabid = 'saem_ou_concepts_profiles_tab'


class OrganizationUnitAuthorityRecordsTab(LinkedObjectsTab):
    """Authority records used by this organization unit."""
    __regid__ = 'saem_ou_authorityrecords_tab'
    __select__ = EntityView.__select__ & relation_possible('use_authorityrecord')
    required_role = 'archival'
    not_possible_msg = _("You can't add authority record to organization unit "
                         "without the 'archival' role.")
    link_targets = [('AuthorityRecord', 'use_authorityrecord', 'subject')]
    subvids = (
        'saem.ou.authorityrecords',
    )


class OrganizationUnitAuthorityRecordsView(RTypeListView):
    __regid__ = 'saem.ou.authorityrecords'
    rtype = 'use_authorityrecord'
    role = 'subject'
    target_etype = 'AuthorityRecord'
    title = None
    tabid = 'saem_ou_authorityrecords_tab'


# Agent
pvs.tag_subject_of(('Agent', 'phone_number', '*'), 'attributes')
afs.tag_subject_of(('Agent', 'phone_number', '*'), 'main', 'inlined')
pvds.tag_subject_of(('Agent', 'use_email', '*'), {'vid': 'text'})

afs.tag_object_of(('*', 'contact_point', 'Agent'), 'main', 'hidden')

pvs.tag_object_of(('*', 'agent_user', '*'), 'hidden')
pvs.tag_subject_of(('Agent', 'agent_user', '*'), 'hidden')
afs.tag_subject_of(('Agent', 'agent_user', '*'), 'main', 'hidden')
