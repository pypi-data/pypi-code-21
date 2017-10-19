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
"""cubicweb-saem-ref monkeypatch of not-yet-integrated patches"""


# https://www.cubicweb.org/ticket/12512052 #########################################################
# this is not probably the right fix, see also https://www.cubicweb.org/ticket/12512176

from cubicweb.web import NoSelectableObject  # noqa
from cubicweb.web.views import ajaxcontroller  # noqa


@ajaxcontroller.ajaxfunc(output_type='xhtml')
def render(self, registry, oid, eid=None, selectargs=None, renderargs=None):
    if eid is not None:
        rset = self._cw.eid_rset(eid)
        # XXX set row=0
    elif self._cw.form.get('rql'):
        rset = self._cw.execute(self._cw.form['rql'])
    else:
        rset = None
    try:
        viewobj = self._cw.vreg[registry].select(oid, self._cw, rset=rset,
                                                 **ajaxcontroller.optional_kwargs(selectargs))
    except NoSelectableObject:
        return u''
    return self._call_view(viewobj, **ajaxcontroller.optional_kwargs(renderargs))


# avoid disappearance of navtop components (https://www.cubicweb.org/17074195) #####################
# other part lies in site_cubicweb.py

from logilab.common.decorators import monkeypatch  # noqa
from logilab.mtconverter import xml_escape  # noqa
from cubicweb.utils import UStringIO  # noqa
from cubicweb.web.views import ajaxcontroller, basetemplates, facets  # noqa


@monkeypatch(facets.FilterBox)
def _get_context(self):
    view = self.cw_extra_kwargs.get('view')
    context = getattr(view, 'filter_box_context_info', lambda: None)()
    if context:
        rset, vid, divid, paginate = context
    else:
        rset = self.cw_rset
        vid, divid = None, 'contentmain'
        paginate = view and view.paginable
    return rset, vid, divid, paginate


@monkeypatch(basetemplates.TheMainTemplate)
def content_column(self, view, content_cols):
    w = self.w
    w(u'<div id="main-center" class="%(prefix)s%(col)s" role="main">' % {
        'prefix': self.twbs_col_cls, 'col': content_cols})
    components = self._cw.vreg['components']
    self.content_components(view, components)
    w(u'<div id="pageContent">')
    self.content_header(view)
    vtitle = self._cw.form.get('vtitle')
    if vtitle:
        w(u'<div class="vtitle">%s</div>\n' % xml_escape(vtitle))
    self.state_header()
    self.content_navrestriction_components(view, components)
    w(u'<div id="contentmain">\n')
    nav_html = UStringIO()
    if view and not view.handle_pagination:
        view.paginate(w=nav_html.write)
    w(nav_html.getvalue())
    view.render(w=w)
    w(nav_html.getvalue())
    w(u'</div>\n')  # closes id=contentmain
    self.content_footer(view)
    w(u'</div>\n')  # closes div#pageContent
    w(u'</div>\n')  # closes div.%(prefix)s-%(col)s


@monkeypatch(ajaxcontroller.AjaxFunction)
def _call_view(self, view, paginate=False, **kwargs):
    divid = self._cw.form.get('divid')
    # we need to call pagination before with the stream set
    try:
        stream = view.set_stream()
    except AttributeError:
        stream = UStringIO()
        kwargs['w'] = stream.write
        assert not paginate
    if divid == 'contentmain':
        # ensure divid isn't reused by the view (e.g. table view)
        del self._cw.form['divid']
        # mimick main template behaviour
        paginate = True
    if divid == 'contentmain':
        stream.write(u'<div id="contentmain">')
    nav_html = UStringIO()
    if paginate and not view.handle_pagination:
        view.paginate(w=nav_html.write)
    stream.write(nav_html.getvalue())
    view.render(**kwargs)
    stream.write(nav_html.getvalue())
    if divid == 'contentmain':
        stream.write(u'</div>')
    extresources = self._cw.html_headers.getvalue(skiphead=True)
    if extresources:
        stream.write(u'<div class="ajaxHtmlHead">\n')
        stream.write(extresources)
        stream.write(u'</div>\n')
    return stream.getvalue()


def registration_callback(vreg):
    vreg.register_all(globals().values(), __name__, (render,))
    vreg.register_and_replace(render, ajaxcontroller.render)
