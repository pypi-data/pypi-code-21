# copyright 2017 LOGILAB S.A. (Paris, FRANCE), all rights reserved.
# contact http://www.logilab.fr -- mailto:contact@logilab.fr
#
# This program is free software: you can redistribute it and/or modify it under
# the terms of the GNU General Public License as published by the Free
# Software Foundation, either version 2.1 of the License, or (at your option)
# any later version.
#
# This program is distributed in the hope that it will be useful, but WITHOUT
# ANY WARRANTY; without even the implied warranty of MERCHANTABILITY or FITNESS
# FOR A PARTICULAR PURPOSE. See the GNU General Public License for more
# details.
#
# You should have received a copy of the GNU General Public License along
# with this program. If not, see <http://www.gnu.org/licenses/>.
"""cubicweb-sherpa components, originaly copied from the saem_ref cube."""

from cubicweb import _
from cubicweb.predicates import multi_lines_rset, has_permission, is_instance, non_final_entity
from cubicweb.web import action, component

from . import jinja_render


class AddEntityAction(action.Action):
    """Action with 'add' link to be displayed in 'same etype' views usually 'SameETypeListView'.
    """
    __regid__ = 'sherpa.add_entity'
    __select__ = (multi_lines_rset()
                  & has_permission('add')
                  & is_instance('AuthorityRecord', 'ConceptScheme',
                                'SEDAArchiveTransfer', 'SEDAArchiveUnit'))
    extra_kwargs = {'SEDAArchiveUnit': {'unit_type': 'unit_content'}}
    order = 1

    @property
    def title(self):
        etype = self.cw_rset.description[0][0]
        return self._cw.__('New %s' % etype).lower()

    def url(self):
        etype = self.cw_rset.description[0][0]
        urlparams = self.extra_kwargs.get(etype, {})
        return self._cw.vreg['etypes'].etype_class(etype).cw_create_url(self._cw, **urlparams)


class ImportEntityAction(action.Action):
    """Action with 'import' link to be displayed in 'same etype' views usually
    'SameETypeListView'.

    Concret class should fill the `import_vid` class attribute and add a proper `is_instance`
    selector.
    """
    __abstract__ = True
    __regid__ = 'sherpa.import_entity'
    __select__ = multi_lines_rset() & has_permission('add')
    order = 2

    @property
    def title(self):
        etype = self.cw_rset.description[0][0]
        return self._cw.__('import %s' % etype)


class EACImportAction(ImportEntityAction):
    """Action with a link to import an authority record from an EAC-CPF file."""
    __select__ = (ImportEntityAction.__select__
                  & is_instance('AuthorityRecord'))
    _('import AuthorityRecord')  # generate message used by the import action

    def url(self):
        return self._cw.build_url('view', vid='eac.import')


class SKOSImportAction(ImportEntityAction):
    """Action with a link to import a concept scheme from a SKOS file."""
    __select__ = ImportEntityAction.__select__ & is_instance('ConceptScheme')
    _('import ConceptScheme')  # generate message used by the import action

    def url(self):
        return self._cw.build_url('add/skossource')


class ActionsComponent(component.CtxComponent):
    """Contextual component replacing the actions box (`cubicweb.web.views.boxes.EditBox`)."""

    __regid__ = 'sherpa.actions'
    __select__ = component.CtxComponent.__select__ & non_final_entity()
    context = 'navtop'

    def render_body(self, w):
        allactions = self._cw.vreg['actions'].possible_actions(
            self._cw, self.cw_rset, view=self.cw_extra_kwargs['view'])
        actions = allactions.get('mainactions', []) + allactions.get('moreactions', [])
        if actions:
            w(jinja_render('menu', actions=actions, _=self._cw._))


def registration_callback(vreg):
    vreg.register_all(globals().values(), __name__)

    from cubicweb.web.views import boxes, workflow
    vreg.unregister(boxes.EditBox)
    vreg.unregister(workflow.WorkflowActions)  # XXX unsupported for now
