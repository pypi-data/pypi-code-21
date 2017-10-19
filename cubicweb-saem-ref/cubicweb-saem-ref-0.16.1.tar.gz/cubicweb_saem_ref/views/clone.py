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
"""cubicweb-saem-ref views related to cloning of compound tree.

Only used for SEDA entities for now.
"""

from cubicweb import tags, _
from cubicweb.predicates import has_related_entities, is_in_state
from cubicweb.web import component

from cubicweb_seda.views.simplified import simplified_afs, simplified_pvs
from cubicweb_seda.views.clone import SEDAArchiveTransferCloneAction


# hide default relation components for 'new_version_of' rtype
simplified_afs.tag_subject_of(('*', 'new_version_of', '*'), 'main', 'hidden')
simplified_afs.tag_object_of(('*', 'new_version_of', '*'), 'main', 'hidden')
simplified_pvs.tag_subject_of(('*', 'new_version_of', '*'), 'hidden')
simplified_pvs.tag_object_of(('*', 'new_version_of', '*'), 'hidden')


# life-cycle management ############################################################################

# Only show clone action for SEDA profiles if no clone has been created yet

class SAEMSEDAArchiveTransferCloneAction(SEDAArchiveTransferCloneAction):
    __select__ = (SEDAArchiveTransferCloneAction.__select__
                  & ~has_related_entities('new_version_of', 'object')
                  & is_in_state('published'))
    title = _('new version')


def workflow_state(entity):
    """Return the state of the given entity."""
    return entity.cw_adapt_to('IWorkflowable').state


class SEDAArchiveTransferRelatedVersionsComponent(component.EntityCtxComponent):
    """Output a box containing relevant SEDA Profiles related to the current one."""
    __regid__ = 'saem.seda.relatedprofiles'
    __select__ = (component.EntityCtxComponent.__select__ &
                  (has_related_entities('new_version_of', role='subject') |
                   has_related_entities('new_version_of', role='object')))
    context = 'incontext'
    order = 11
    title = _('Related versions')

    def predecessor(self):
        """Yield the profile of which the displayed profile is a new version (draft or published).
        """
        if (workflow_state(self.entity) in (u'published', u'draft') and
                self.entity.predecessor):
            yield self.entity.predecessor

    def current_version(self, state):
        """Yield the latest profile, either published or draft, that replaces the displayed one.

        ``state`` parameter must be either "draft" or "published".
        """
        assert state in (u'published', u'draft')
        successor = self.entity.successor
        while successor and workflow_state(successor) != state:
            successor = successor.successor
        if successor:
            yield successor

    def render_body(self, w):
        profile_state = workflow_state(self.entity)
        display_entities = []
        if profile_state == u'draft':
            display_entities += self.predecessor()
        elif profile_state == u'published':
            display_entities += self.current_version(u'draft')
            display_entities += self.predecessor()
        elif profile_state == u'deprecated':
            display_entities += self.current_version(u'published')
        if display_entities:
            w(u'<ul class="list-group">')
            for entity in display_entities:
                w(u'<li class="list-group-item">')
                w(tags.span(self._cw._(workflow_state(entity)), klass='badge'))
                entity.view('incontext', w=w)
                w(u'</li>')
            w(u'</ul>')


def registration_callback(vreg):
    vreg.register_all(globals().values(), __name__, (SAEMSEDAArchiveTransferCloneAction,))
    vreg.register_and_replace(SAEMSEDAArchiveTransferCloneAction, SEDAArchiveTransferCloneAction)
