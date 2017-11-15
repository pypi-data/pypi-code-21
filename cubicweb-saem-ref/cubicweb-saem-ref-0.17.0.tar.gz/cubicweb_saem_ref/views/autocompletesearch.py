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
"""Auto-completion in search widgets."""

from collections import defaultdict

from logilab.mtconverter import xml_escape
from rql import RQLException

from cubicweb.uilib import domid
from cubicweb.utils import json_dumps, make_uid
from cubicweb.view import StartupView
from cubicweb.web import facet as facetbase
from cubicweb.web.views.boxes import SearchBox
from cubicweb.web.views.facets import HasTextFacet

__docformat__ = "restructuredtext en"

# XXX The words selection should be done in RQL ::
#     Any X HAVING W=WORDS(%(q)s)
#     or
#     Any W, SIMILARITY(W) HAVING W=WORDS(%(q)s)
#
# However, with WORDS class declared as above::
#
#     class WORDS(FunctionDescr):
#         supported_backends = ('postgres',)
#         rtype = 'String'
#
# the resulting sql for Any X HAVING W=WORDS('toto') states :
#
#       SELECT _W.eid
#       FROM entities AS _W
#       WHERE _W.eid=WORDS(%(140390076097112)s) {'140390076097112': u'toto'}
#
# Some more modifications are needed in `server/sources/rql2sql.py`,
# which we dont't want to do for instance.


def words_matching_term(req, term, previous_words='', base_rql=''):
    """Return a similarity ordered list of (word, etype) matching the current term, considering
    previously typed words and optional base rql in the case of facetted search.
    """
    assert term
    if not base_rql:
        base_rql = 'Any X WHERE X has_text %(text)s, X is ET, ET name %(etype)s'
    else:
        base_rql += ', X has_text %(text)s, X is ET, ET name %(etype)s'
    # the sqlgenerator introduces the searched text in the generated SQL and not in the query
    # arguments. As we want to hack this later, introduces an unexpected placeholder that will be
    # replaced.
    text_place_holder = 'xyz' * 10
    args = {'text': text_place_holder, 'etype': 'whatever'}
    # generate SQL from RQL to join with the above query
    try:
        union = req.vreg.parse(req, base_rql)
    except RQLException:
        return []
    req.vreg.rqlhelper.simplify(union)
    repository = req.cnx.repo
    plan = repository.querier.plan_factory(union, args, req.cnx)
    plan.preprocess(union)
    base_sql, qargs, _ = repository.system_source._rql_sqlgen.generate(union, args)
    # we don't care of original ordering, remove it
    base_sql = base_sql.split('ORDER BY')[0]
    # replace plain-text search terms and etype substitution by element from the parent query
    if previous_words:
        searched = repository.system_source.dbhelper._fti_query_to_tsquery_words(previous_words)
        searched = "'{0}&' || normalized_word".format(searched)
    else:
        searched = "normalized_word"
    base_sql = base_sql.replace("'{0}'".format(text_place_holder), searched)
    base_sql = base_sql.replace("%(etype)s", 'etype')
    qargs['q'] = term
    sql = '''SELECT word, etype
FROM words
WHERE similarity(word, %(q)s) > 0.4 AND length(word) > length(%(q)s)-1
AND EXISTS({base_sql})
ORDER BY similarity(word, %(q)s) DESC, word, etype;'''.format(base_sql=base_sql)
    return req.cnx.system_sql(sql, qargs).fetchall()


class AutocompleteSearchView(StartupView):
    """The principal view for autocomplete search
    """
    __regid__ = 'search-autocomplete'
    templatable = False
    binary = True

    def call(self):
        base_rql = self._cw.form['facetrql']
        # string containing words typed before the current one, to later ensure we provide
        # consistent results
        previous_words = ' '.join(self._cw.form['all'].split()[:-1])
        matching_words = words_matching_term(self._cw, self._cw.form['term'],
                                             previous_words, base_rql)
        processed = defaultdict(list)
        words = []
        for word, etype in matching_words:
            if word not in processed:
                words.append(word)
            processed[word].append(self._cw._(etype))
        results = []
        for word in words:
            labels = processed[word]
            results.append({'label': '%s : %s' % (word, ', '.join(sorted(labels))),
                            'value': word})
        self.w(json_dumps(results))


class AutocompleteSearchBox(SearchBox):
    formdef = '''
<form action="%(action)s" id="search_box" class="navbar-form" role="search">
  <input id="norql" autocomplete="off" type="text" accesskey="q" tabindex="%(tabindex1)s"
    title="search text" value="%(value)s" name="rql"
    class="search-query form-control" placeholder="%(searchlabel)s"/>
  <input type="hidden" name="__fromsearchbox" value="1" />
  <input type="hidden" name="subvid" value="tsearch" />
</form>
'''

    def render_body(self, w):
        self._cw.add_js(('jquery.ui.js', 'cubicweb.autocompletesearch.js'))
        self._cw.add_css(('jquery.ui.css',))
        url = self._cw.build_url('view', vid='search-autocomplete')
        minlength = 2
        limit = 20
        self._cw.add_onload('cw.search_autocomplete($("#norql"), "%s", %s, %s);'
                            % (url, minlength, limit))
        super(AutocompleteSearchBox, self).render_body(w)


class AutocompleteSearchWidget(facetbase.FacetStringWidget):

    def _render(self):
        """ has-hext facet widget with autocomplete"""
        req = self.facet._cw
        facetid = domid(make_uid(self.facet.__regid__))
        input_id = xml_escape('id-%s' % facetid)
        req.add_js(('jquery.ui.js', 'cubicweb.autocompletesearch.js'))
        req.add_css(('jquery.ui.css', ))
        url = req.build_url('view', vid='search-autocomplete')
        minlength = 2
        limit = 20
        req.add_onload('cw.search_autocomplete($("#%s"), "%s", %s, %s);' % (
            input_id, url, minlength, limit))
        w = self.w
        title = xml_escape(self.facet.title)
        w(u'<div id="%s" class="facet">\n' % facetid)
        cssclass = 'facetTitle'
        if self.facet.allow_hide:
            cssclass += ' hideFacetBody'
        w(u'<div class="%s" cubicweb:facetName="%s">%s</div>\n' %
            (cssclass, xml_escape(self.facet.__regid__), title))
        cssclass = 'facetBody'
        if not self.facet.start_unfolded:
            cssclass += ' hidden'
        w(u'<div class="%s">\n' % cssclass)
        w((u'<input autocomplete="off" id="%s" name="%s" '
            'type="text" value="%s" data-facet="1"/>\n') % (
            input_id, xml_escape(self.facet.__regid__),
            self.value or u''))
        w(u'</div>\n')
        w(u'</div>\n')


def registration_callback(vreg):
    try:
        import psycopg2
    except ImportError:
        psycopg2 = None
    if psycopg2:
        vreg.register_all(globals().values(), __name__, [])
        vreg.unregister(SearchBox)
        HasTextFacet.wdgclass = AutocompleteSearchWidget
