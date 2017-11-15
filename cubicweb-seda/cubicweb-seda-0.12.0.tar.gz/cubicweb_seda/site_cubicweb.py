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

from logilab.common.decorators import monkeypatch

from cubicweb.entity import Entity
from cubicweb.rqlrewrite import RQLRelationRewriter
from cubicweb.server import ssplanner

Entity.cw_skip_copy_for.append(('container', 'subject'))
Entity.cw_skip_copy_for.append(('container', 'object'))
Entity.cw_skip_copy_for.append(('clone_of', 'subject'))
Entity.cw_skip_copy_for.append(('clone_of', 'object'))


# monkey-patch to allow using computed relation in WHERE clause of write queries
# (https://www.cubicweb.org/ticket/17113286)

@monkeypatch(ssplanner.SSPlanner)
def _select_plan(self, plan, select, solutions):
    union = ssplanner.Union()
    union.append(select)
    select.clean_solutions(solutions)
    ssplanner.add_types_restriction(self.schema, select)
    rewriter = RQLRelationRewriter(plan.cnx)
    rewriter.rewrite(union, plan.args)
    self.rqlhelper.annotate(union)
    return self.build_select_plan(plan, union)
