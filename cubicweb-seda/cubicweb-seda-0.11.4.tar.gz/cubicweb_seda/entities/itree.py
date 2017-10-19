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
"""cubicweb-seda ITreeBase adapters"""

from cubicweb.predicates import is_instance
from cubicweb.view import EntityAdapter

from . import simplified_profile


def parent_archive_unit(entity):
    """Return the first encountered parent which is an ArchiveUnit"""
    while entity.cw_etype != 'SEDAArchiveUnit':
        entity = entity.cw_adapt_to('IContained').parent
    return entity


class IContainedToITreeBase(EntityAdapter):
    """Map IContained adapters to ITreeBase, additionaly configured with a list of relations leading to
    contained's children.

    ITreeBase is a simplified version of cubicweb's ITree.
    """

    __regid__ = 'ITreeBase'
    __abstract__ = True

    _children_relations = []  # list of (relation type, role) to get entity's children

    def iterchildren(self):
        """Return an iterator over the item's children."""
        for rel, role in self._children_relations:
            for child in self.entity.related(rel, role, entities=True):
                yield child

    def is_leaf(self):
        """Returns True if the entity does not have any children."""
        try:
            next(iter(self.iterchildren()))
            return False
        except StopIteration:
            return True

    def parent(self):
        return self.entity.cw_adapt_to('IContained').parent

    def iterancestors(self):
        """Return an iterator on the ancestors of the entity."""
        def _uptoroot(self):
            curr = self
            while True:
                curr = curr.parent()
                if curr is None:
                    break
                yield curr
                curr = curr.cw_adapt_to('ITreeBase')
        return _uptoroot(self)

    iterparents = iterancestors  # Compat. with CubicWeb's ITree.


class ITreeBaseArchiveUnitAdapter(IContainedToITreeBase):
    """Adapt ArchiveUnit entities to ITreeBase."""

    __select__ = is_instance('SEDAArchiveUnit')

    _children_relations = [('seda_archive_unit', 'object')]

    def parent(self):
        parent = self.entity.cw_adapt_to('IContained').parent
        if parent is None:
            return None
        if parent.cw_etype == 'SEDAArchiveTransfer':
            return parent
        return parent_archive_unit(parent)

    def iterchildren(self):
        seq = self.entity.first_level_choice.content_sequence
        if seq is None:
            # 'reference' archive unit
            return
        for rel, role in self._children_relations:
            for child in seq.related(rel, role, entities=True):
                yield child


class ITreeBaseSimplifiedArchiveUnitAdapter(ITreeBaseArchiveUnitAdapter):

    __select__ = ITreeBaseArchiveUnitAdapter.__select__ & simplified_profile()

    _children_relations = [('seda_archive_unit', 'object')]

    def iterchildren(self):
        for child in super(ITreeBaseSimplifiedArchiveUnitAdapter, self).iterchildren():
            yield child
        seq = self.entity.first_level_choice.content_sequence
        assert seq is not None, self.entity  # can't be None in simplified profile
        for do in self._cw.execute(
                'Any DO, DOUA ORDERBY DOUA WHERE DO user_annotation DOUA, '
                'REF seda_data_object_reference_id DO, '
                'REF seda_data_object_reference SEQ, SEQ eid %(x)s',
                {'x': seq.eid}).entities():
            yield do


class ITreeBaseDataObjectAdapter(IContainedToITreeBase):
    """Adapt BinaryDataObject and PhysicalDataObject entities to ITreeBase."""

    __select__ = is_instance('SEDABinaryDataObject', 'SEDAPhysicalDataObject')


class ITreeBaseSimplifiedDataObjectAdapter(ITreeBaseDataObjectAdapter):

    __select__ = ITreeBaseDataObjectAdapter.__select__ & simplified_profile()

    def parent(self):
        return parent_archive_unit(self.entity.reverse_seda_data_object_reference_id[0])


class ITreeBaseArchiveTransferAdapter(IContainedToITreeBase):
    """Adapt ArchiveTransfer entities to ITreeBase."""

    __select__ = is_instance('SEDAArchiveTransfer')

    @property
    def _children_relations(self):
        if self.entity.simplified_profile:
            return [('seda_archive_unit', 'object')]
        else:
            return [('seda_binary_data_object', 'object'),
                    ('seda_physical_data_object', 'object'),
                    ('seda_archive_unit', 'object')]

    def parent(self):
        return None
