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
"""cubicweb-saem-ref workflows definition"""

from cubicweb import _


def define_publication_workflow(add_workflow, etype):
    """Define a publication workflow for `etype`."""
    wf = add_workflow('publication workflow', etype)
    draft = wf.add_state(_('draft'), initial=True)
    published = wf.add_state(_('published'))
    deprecated = wf.add_state(_('deprecated'))
    if etype == 'SEDAArchiveTransfer':
        wf.add_transition(_('publish'), (draft, ), published,
                          conditions=('U in_group G, G name IN ("users", "managers"),'
                                      'X compat_list ~= "%SEDA 0.2%"',))
    else:
        wf.add_transition(_('publish'), (draft, ), published,
                          requiredgroups=('managers', 'users'))
    wf.add_transition(_('deprecate'), (published, ), deprecated,
                      requiredgroups=('managers', 'users'))
    return wf
