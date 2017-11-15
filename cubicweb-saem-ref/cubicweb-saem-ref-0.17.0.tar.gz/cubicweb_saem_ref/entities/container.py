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
"""cubicweb-saem_ref "compound"-related functionalities."""

from functools import partial

from cubicweb_compound import structure_def
from cubicweb_compound.entities import IContainer, IContained

# don't put Activity in a compound graph, it causes problem since it belongs to both
# SEDAArchiveTransfer tree and to concept/authority record tree, which don't have the same
# IContained implementation.
structure_def = partial(structure_def, skipetypes=('Activity',))


def authority_record_container_def(schema):
    """Define container for AuthorityRecord"""
    return structure_def(schema, 'AuthorityRecord').items()


def org_container_def(schema):
    return structure_def(schema, 'Organization').items()


def scheme_container_def(schema):
    """Define container for ConceptScheme"""
    skiprtypes = ('broader_concept', 'label_of')
    return structure_def(schema, 'ConceptScheme', skiprtypes=skiprtypes).items()


def concept_container_def(schema):
    """Define container for Concept"""
    return structure_def(schema, 'Concept').items()


def registration_callback(vreg):
    vreg.register(IContainer.build_class('Organization'))
    for etype, parent_relations in org_container_def(vreg.schema):
        IContained.register_class(vreg, etype, parent_relations)
    vreg.register(IContainer.build_class('AuthorityRecord'))
    for etype, parent_relations in authority_record_container_def(vreg.schema):
        IContained.register_class(vreg, etype, parent_relations)
    vreg.register(IContainer.build_class('ConceptScheme'))
    for etype, parent_relations in scheme_container_def(vreg.schema):
        if etype == 'Concept':
            # XXX turn parent_relations to a list to ensure broader_concept is considered first
            parent_relations = list(parent_relations)
            parent_relations.insert(0, ('broader_concept', 'subject'))
        IContained.register_class(vreg, etype, parent_relations)
    vreg.register(IContainer.build_class('Concept'))
    for etype, parent_relations in concept_container_def(vreg.schema):
        IContained.register_class(vreg, etype, parent_relations)
