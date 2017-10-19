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
"""cubicweb-saem-ref custom views for skos entities"""


from cubicweb import tags, _
from cubicweb.view import AnyRsetView
from cubicweb.predicates import is_instance
from cubicweb.web import formwidgets as fw
from cubicweb.web.views import baseviews, treeview, uicfg, editcontroller

from cubes.skos import views as skos

from . import ImportEntityComponent


afs = uicfg.autoform_section
affk = uicfg.autoform_field_kwargs

for etype, attr in (('ConceptScheme', 'ark'),
                    ('Concept', 'ark')):
    affk.set_field_kwargs(etype, attr, widget=fw.TextInput({'size': 80}))
    affk.set_field_kwargs(etype, attr, required=False)


_('Import ConceptScheme')  # generate message used by the import component


class SKOSImportComponent(ImportEntityComponent):
    """Component with a link to import a concept scheme from a SKOS file."""
    __select__ = ImportEntityComponent.__select__ & is_instance('ConceptScheme')

    @property
    def import_url(self):
        return self._cw.build_url('add/skossource')


afs.tag_object_of(('*', 'related_concept_scheme', 'ConceptScheme'), 'main', 'hidden')

skos.ConceptSchemePrimaryView.tabs.append(_('saem.lifecycle_tab'))
skos.ConceptPrimaryView.tabs.append(_('saem.lifecycle_tab'))


class ConceptSchemeSameETypeListView(baseviews.SameETypeListView):
    """Override SameETypeListView to display a search action on top"""
    __select__ = baseviews.SameETypeListView.__select__ & is_instance('ConceptScheme')

    def call(self, **kwargs):
        self.search_link()
        super(ConceptSchemeSameETypeListView, self).call(**kwargs)

    def search_link(self):
        """Render a link to search for Concepts within selected ConceptSchemes"""
        rql = 'Any X WHERE X in_scheme S, S eid '
        if len(self.cw_rset) > 1:
            rql += 'IN ({0})'.format(', '.join(str(x[0]) for x in self.cw_rset.rows))
        else:
            rql += str(self.cw_rset[0][0])
        href = self._cw.build_url(rql=rql)
        title = self._cw._('search for concepts of concept schemes')
        self.w(u'<a class="btn btn-default pull-right" href="{href}">{title}</a>'.format(
            href=href, title=title))


class ConceptTreeView(treeview.TreeView):
    """`treeview` for Concept entities."""
    __select__ = treeview.TreeView.__select__ & is_instance('Concept')
    subvid = 'skos.concept-popover'


class ConceptPopoverView(AnyRsetView):
    """Popover view for Concept, to be displayed within treeview"""
    __regid__ = 'skos.concept-popover'
    __select__ = is_instance('Concept')

    def cell_call(self, row, col, **kwargs):
        entity = self.cw_rset.get_entity(row, col)
        self._cw.add_onload("$('#{eid}').popover();".format(eid=entity.eid))
        title = entity.dc_title()
        content = u'<dl>'
        for attr in ('definition', 'example'):
            if getattr(entity, attr):
                content += u'<dt>{label}</dt><dd>{value}</dd>'.format(
                    label=self._cw._(attr),
                    value=entity.printable_value(attr, format=u'text/html'))
        content += u'</dl>'
        content += tags.a(self._cw._('view'), href=entity.absolute_url())
        data = {'data-title': title,
                'data-content': content,
                'data-html': 'true',
                'data-trigger': 'focus'}
        self.w(tags.a(title, href='javascript:$.noop();', id=str(entity.eid), **data))


class SAEMEditController(editcontroller.EditController):

    def edit_entity(self, formparams, multiple=False):
        if formparams['__type'] == 'Concept' and not formparams['eid'].isdigit():
            # concept is being created, attempt to find its parent scheme and set this in
            # transaction data so it's reachable from hooks. This is necessary because some hook
            # will use that to retrieve the ARK NAA that should be used to assign a ark to the newly
            # created concept. This is really hackish, and could be avoided if in_scheme relation
            # was inlined or if form data was available from the hook side.
            for linkto in self._cw.list_form_param('__linkto'):
                rtype, eid, target = linkto.split(':')
                if rtype == 'in_scheme':
                    self._cw.transaction_data['concept_scheme'] = eid
                    break
            else:
                # not found, search in form params
                for param, value in formparams.items():
                    if param == 'in_scheme-subject':
                        self._cw.transaction_data['concept_scheme'] = value
                        break
        return super(SAEMEditController, self).edit_entity(formparams, multiple)


def registration_callback(vreg):
    vreg.register_all(globals().values(), __name__, (SAEMEditController,))
    vreg.register_and_replace(SAEMEditController, editcontroller.EditController)
    from cubes.skos.views import ImportConceptSchemeAction
    vreg.unregister(ImportConceptSchemeAction)
    from cubicweb.web.views import cwsources
    vreg.unregister(cwsources.ManageSourcesAction)
