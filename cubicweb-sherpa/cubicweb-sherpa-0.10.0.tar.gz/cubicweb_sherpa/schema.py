# copyright 2017 LOGILAB S.A. (Paris, FRANCE), all rights reserved.
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

from cubicweb.schema import ERQLExpression

from cubes.skos.schema import ConceptScheme

ConceptScheme.__permissions__ = {
    'read': ('managers', 'users', 'guests'),
    'add': ('managers',),
    'update': ('managers',),
    'delete': ('managers',),
}


def post_build_callback(schema):
    from cubicweb_compound import CompositeGraph, utils
    graph = CompositeGraph(schema)
    utils.graph_set_etypes_update_permissions(schema, graph, 'ConceptScheme')
    utils.graph_set_write_rdefs_permissions(schema, graph, 'ConceptScheme')

    for action in ('update', 'delete'):
        schema['SEDAArchiveUnit'].set_action_permissions(
            action, ('managers',
                     ERQLExpression('U has_{action}_permission C, '
                                    'X container C'.format(action=action)),
                     ERQLExpression('NOT EXISTS(X container C), X owned_by U')))
