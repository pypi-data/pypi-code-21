# copyright 2016-2017 LOGILAB S.A. (Paris, FRANCE), all rights reserved.
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
"""cubicweb-seda views for ArchiveUnit"""

from cubicweb import _
from cubicweb.predicates import adaptable, is_instance
from cubicweb.web import component

from ..entities import simplified_profile, component_unit
from . import jqtree


class ProfileTreeComponent(component.EntityCtxComponent):
    """Display the whole profile tree."""
    __regid__ = 'seda.tree'
    __select__ = (component.EntityCtxComponent.__select__
                  & adaptable('ITreeBase'))
    context = 'left'
    order = -1
    title = _('SEDA profile tree')

    def render_body(self, w):
        self._cw.add_css('cubes.jqtree.css')
        self.entity.view('jqtree.treeview', w=w)


class UnitTreeComponent(ProfileTreeComponent):
    __select__ = ProfileTreeComponent.__select__ & component_unit()
    title = _('Archive unit component tree')


class ArchiveTransferIJQTreeAdapter(jqtree.IJQTreeAdapter):
    __select__ = (jqtree.IJQTreeAdapter.__select__
                  & is_instance('SEDAArchiveTransfer'))

    def maybe_parent_of(self):
        return ['SEDAArchiveUnit',
                'SEDAPhysicalDataObject', 'SEDABinaryDataObject']


class SimplifiedArchiveTransferIJQTreeAdapter(ArchiveTransferIJQTreeAdapter):
    __select__ = ArchiveTransferIJQTreeAdapter.__select__ & simplified_profile()

    def maybe_parent_of(self):
        return ['SEDAArchiveUnit']


class ArchiveUnitIJQTreeAdapter(jqtree.IJQTreeAdapter):
    __select__ = (jqtree.IJQTreeAdapter.__select__
                  & is_instance('SEDAArchiveUnit'))

    def maybe_parent_of(self):
        return [] if self.entity.is_archive_unit_ref else ['SEDAArchiveUnit']

    def maybe_moved(self):
        return True

    def reparent(self, peid):
        parent = self._cw.entity_from_eid(peid)
        if parent.cw_etype == 'SEDAArchiveUnit':
            parent = parent.first_level_choice.content_sequence
        else:
            assert parent.cw_etype == 'SEDAArchiveTransfer', (
                'cannot re-parent to entity type {0}'.format(parent.cw_etype))
        rset = self._cw.execute(
            'SET X seda_archive_unit P WHERE X eid %(x)s, P eid %(p)s',
            {'x': self.entity.eid, 'p': parent.eid})
        return rset.rows


class SimplifiedArchiveUnitIJQTreeAdapter(ArchiveUnitIJQTreeAdapter):
    __select__ = ArchiveUnitIJQTreeAdapter.__select__ & simplified_profile()

    def maybe_parent_of(self):
        return [] if self.entity.is_archive_unit_ref else ['SEDAArchiveUnit',
                                                           'SEDABinaryDataObject']


class DataObjectIJQTreeAdapter(jqtree.IJQTreeAdapter):
    __select__ = (jqtree.IJQTreeAdapter.__select__
                  & is_instance('SEDABinaryDataObject', 'SEDAPhysicalDataObject'))

    def maybe_moved(self):
        return False


class SimplifiedBinaryDataObjectIJQTreeAdapter(jqtree.IJQTreeAdapter):
    __select__ = (jqtree.IJQTreeAdapter.__select__
                  & is_instance('SEDABinaryDataObject') & simplified_profile())
    rtype_to_archivetransfer = 'seda_binary_data_object'

    def maybe_moved(self):
        return True

    def reparent(self, peid):
        archunit = self._cw.entity_from_eid(peid)
        parent = archunit.first_level_choice.content_sequence
        rset = self._cw.execute(
            'SET REF seda_data_object_reference SEQ WHERE'
            ' REF seda_data_object_reference_id X,'
            ' X eid %(x)s, SEQ eid %(seq)s',
            {'x': self.entity.eid, 'seq': parent.eid})
        return rset.rows
