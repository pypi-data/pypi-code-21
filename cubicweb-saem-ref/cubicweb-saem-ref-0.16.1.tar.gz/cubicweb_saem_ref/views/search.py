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
"""cubicweb-saem-ref custom behaviour for search"""

from logilab.mtconverter import TransformError, xml_escape

from cubicweb.uilib import cut
from cubicweb.utils import json_dumps
from cubicweb.predicates import is_instance
from cubicweb.view import EntityView
from cubicweb.web import facet
from cubicweb.web.views import magicsearch, baseviews, basecontrollers, ajaxcontroller


# highlighting #################################################################

def highlight_keywords(cw):
    """Highlight the form keywords (if any) on page loading"""
    if 'highlight' in cw.form:
        # as we are handling this upstream, directly from the controller and
        # not from a view, jquery hasn't been loaded yet.
        # As jquery.highlight relies on it, we have to add it first.
        cw.add_js((u'jquery.js', u'jquery.highlight.js'))
        cw.add_onload(
            u'$(document).ready(function(){$("h1, h2, h3, h4, h5, '
            'table tbody td").highlight(%s);});' % json_dumps(cw.form['highlight']))


class FullTextTranslator(magicsearch.FullTextTranslator):
    """Full text translator adding a 'highlight' element to _cw.form"""

    def preprocess_query(self, uquery):
        self._cw.form['highlight'] = uquery.strip()
        return super(FullTextTranslator, self).preprocess_query(uquery)


class TextSearchResultView(baseviews.TextSearchResultView):
    """Overloaded so that it adds a 'highlight' keyword to the entities URL"""

    def cell_call(self, row, col, **kwargs):
        entity = self.cw_rset.complete_entity(row, col)
        self.w(entity.view('searchresult'))
        searched = self.cw_rset.searched_text()
        if searched is None:
            return
        searched = searched.lower()
        highlighted = '<b>%s</b>' % searched
        for attr in entity.e_schema.indexable_attributes():
            try:
                value = xml_escape(entity.printable_value(attr, format='text/plain').lower())
            except TransformError:
                continue
            if searched in value:
                contexts = []
                for ctx in value.split(searched):
                    if len(ctx) > 30:
                        contexts.append(u'...' + ctx[-30:])
                    else:
                        contexts.append(ctx)
                value = u'\n' + highlighted.join(contexts)
                self.w(value.replace('\n', '<br/>'))


class EntitySearchResultView(EntityView):
    """Overloaded so that it adds an 'highlight' keyword to the URL"""

    __regid__ = 'searchresult'

    def cell_call(self, row, col):
        entity = self.cw_rset.get_entity(row, col)
        desc = cut(entity.dc_description(), 50)
        if 'highlight' in self._cw.form:
            url = entity.absolute_url(highlight=self._cw.form['highlight'])
        else:
            url = entity.absolute_url()
        self.w(u'<a href="%s" title="%s">%s</a>' % (
            xml_escape(url), xml_escape(desc), xml_escape(entity.dc_title())))


# Beware: this code overrides the monkeypatch of the bootstrap cube.
# See tickets https://www.cubicweb.org/ticket/5098473 and
# https://www.cubicweb.org/ticket/5102924
class SameETypeListView(baseviews.SameETypeListView):
    """Overloaded so that it takes into account subvid form param"""

    def call(self, **kwargs):
        """display a list of entities by calling their <item_vid> view"""
        subvid = self._cw.form.pop('subvid') if 'subvid' in self._cw.form else None
        if subvid is not None:
            self.item_vid = subvid
        super(SameETypeListView, self).call(**kwargs)


class ViewController(basecontrollers.ViewController):
    """Overloaded view controller dealing with 'highlight' keyword in the URL

    Highlight in the generated view the words passed to the url with 'highlight' keyword
    """

    def _select_view_and_rset(self, rset):
        highlight_keywords(self._cw)
        return super(ViewController, self)._select_view_and_rset(rset)


class AjaxController(ajaxcontroller.AjaxController):

    def publish(self, rset=None):
        highlight_keywords(self._cw)
        return super(AjaxController, self).publish(rset)


# facets #######################################################################

class AgentStartDateFacet(facet.DateRangeFacet):
    __regid__ = 'saem.agent_start_date_facet'
    __select__ = facet.DateRangeFacet.__select__ & is_instance('Agent')
    rtype = 'start_date'


class AgentEndDateFacet(facet.DateRangeFacet):
    __regid__ = 'saem.agent_end_date_facet'
    __select__ = facet.DateRangeFacet.__select__ & is_instance('Agent')
    rtype = 'end_date'


class AgentKindFacet(facet.RelationAttributeFacet):
    __regid__ = 'saem.agent_kind_facet'
    __select__ = facet.RelationAttributeFacet.__select__ & is_instance('Agent')
    rtype = 'agent_kind'
    role = 'subject'
    target_attr = 'name'


class AgentRoleFacet(facet.RelationAttributeFacet):
    __regid__ = 'saem.agent_role_facet'
    __select__ = facet.RelationAttributeFacet.__select__ & is_instance('Agent')
    rtype = 'archival_role'
    role = 'subject'
    target_attr = 'name'


################################################################################

def registration_callback(vreg):
    vreg.register_all(globals().values(), __name__,
                      (FullTextTranslator, TextSearchResultView,
                       SameETypeListView, ViewController, AjaxController))
    vreg.register_and_replace(FullTextTranslator, magicsearch.FullTextTranslator)
    vreg.register_and_replace(TextSearchResultView, baseviews.TextSearchResultView)
    vreg.register_and_replace(SameETypeListView, baseviews.SameETypeListView)
    vreg.register_and_replace(ViewController, basecontrollers.ViewController)
    vreg.register_and_replace(AjaxController, ajaxcontroller.AjaxController)
