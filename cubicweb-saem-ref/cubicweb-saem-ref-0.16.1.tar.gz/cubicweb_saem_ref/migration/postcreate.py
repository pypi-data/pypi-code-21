# coding: utf-8
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
"""cubicweb-saem-ref postcreate script"""

from cubicweb import _
from cubicweb_saem_ref import workflows


set_property('ui.site-title', u'Référentiel SAEM')
set_property('ui.language', u'fr')
set_property('ui.date-format', u'%d/%m/%Y')
set_property('ui.datetime-format', u'%d/%m/%Y %H:%M')

for name in [_('producer'), _('deposit'), _('archival'), _('control'),
             _('enquirer'), _('seda-actor')]:
    create_entity('ArchivalRole', name=name)

for etype in ('Agent', 'AuthorityRecord', 'ConceptScheme', 'OrganizationUnit',
              'SEDAArchiveTransfer'):
    workflows.define_publication_workflow(add_workflow, etype)
commit()

schema_wf = get_workflow_for('ConceptScheme')
with cnx.deny_all_hooks_but():
    rql('SET X in_state S WHERE X is ConceptScheme, S eid %(s)s',
        {'s': schema_wf.state_by_name('published').eid})
commit()

for stmt in repo.system_source.dbhelper.sql_create_sequence('ext_ark_count').split(';'):
    if stmt:
        sql(stmt)
