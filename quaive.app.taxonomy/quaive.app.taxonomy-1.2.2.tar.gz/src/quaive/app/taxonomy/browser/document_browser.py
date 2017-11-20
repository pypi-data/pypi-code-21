# coding=utf-8
from collections import defaultdict
from json import loads
from plone import api
from plone.app.blocks.interfaces import IBlocksTransformEnabled
from plone.memoize.view import memoize
from ploneintranet.core import ploneintranetCoreMessageFactory as _
from ploneintranet.layout.browser.grouped_search import GroupedSearchTile
from ploneintranet.layout.interfaces import IAppView
from ploneintranet.search.interfaces import ISiteSearch
from ploneintranet.workspace.browser.tiles.sidebar import Sidebar
from Products.CMFPlone.utils import safe_unicode
from zope.component import getUtility
from zope.component.interfaces import ComponentLookupError
from zope.interface import implementer
from zope.schema.interfaces import IVocabularyFactory

import logging


log = logging.getLogger(__name__)


@implementer(IBlocksTransformEnabled, IAppView)
class DocumentBrowserView(Sidebar):

    app_name = 'document-browser'

    def __init__(self, context, request):
        super(DocumentBrowserView, self).__init__(context, request)
        app_parameters = loads(self.context.app_parameters)
        self.vocabulary_name = app_parameters.get('vocabulary', 'taxonomy')
        self.vocabulary_index = app_parameters.get(
            'vocabulary_index', self.vocabulary_name)

    def __call__(self):
        try:
            factory = getUtility(IVocabularyFactory, self.vocabulary_name)
            self.vocabulary = factory(self.context)
        except ComponentLookupError:
            self.vocabulary = None
        return self.index()

    @property
    def search_query(self):
        return self.request.get('sidebar-search', None)

    @property
    def term_id(self):
        term_id = self.request.get('term-id')
        if term_id:
            if term_id in self.vocabulary:
                return term_id

    def terms(self, vocabulary=None, path=None):
        # Don't return vocab terms when searching
        # quaive/ploneintranet.prototype#272
        if self.search_query:
            return []
        if not self.term_id:
            return self.vocabulary
        else:
            if vocabulary is None:
                vocabulary = self.vocabulary
            if path == []:
                return vocabulary
            elif path is None:
                path = self.vocabulary.getTermPath(self.term_id)
            try:
                term = self.vocabulary.getTerm(path[0])
                return self.terms(vocabulary=vocabulary[term], path=path[1:])
            except KeyError:
                return []

    def vdex_tree(self):
        """ Return the vocabulary data structure, which includes all sub terms,
        for the current term:

        [(
           <VdexTerm '1.1' at 0x7f709c874ed>,
           OrderedDict([(<VdexTerm '1.1.1' at 0x7f709c92ba5>, OrderedDict())])
        )]
        """
        vocab = self.vocabulary
        for node in self.vocabulary.getTermPath(self.term_id):
            vocab = vocab[self.vocabulary.getTerm(node)]
        return vocab.items()

    def flattened_tokens(self, vdex_tree=None):
        """ Return the tokens for all sub_terms so that we can query for
        content tagged with any sub term.
        """
        if not vdex_tree:
            vdex_tree = self.vdex_tree()
        for term, sub_terms in vdex_tree:
            if sub_terms:
                sub_vdex_tree = sub_terms.items()
                for token in self.flattened_tokens(vdex_tree=sub_vdex_tree):
                    yield safe_unicode(token)
            yield safe_unicode(term.token)

    def items(self):
        """ Return a list of dicts for each item which matches the currently
        selected vocabulary term.
        If there is a search query, then return items for that query with the
        currently selected vocabulary term or any sub-terms.

        If the search query starts with a vocabulary term, then igore the
        searchable text and filter the terms in the query to only include terms
        which start with the query.

        For example: if you have browsed to the term 09.10, and then search for
        "09.10.0" then the results will be filtered to only include items with
        terms that start with "09.10.0".
        """
        search_util = getUtility(ISiteSearch)
        if self.vocabulary_index not in search_util.facet_fields:
            log.error(
                'There is no search facet for the vocabulary index named: {}'
                .format(self.vocabulary_index)
            )
            return []

        filters = {}
        searchable_text = ''
        search_query = safe_unicode(self.search_query)
        if self.vocabulary_name:
            if self.search_query:
                searchable_text = u'{}*'.format(search_query)

                term_tokens = list(self.flattened_tokens())
                if self.term_id:
                    term_tokens.append(self.term_id)

                for token in term_tokens:
                    if token.startswith(search_query):
                        term_tokens = [
                            i for i in term_tokens
                            if i.startswith(search_query)
                        ]
                        searchable_text = None
                filters[self.vocabulary_index] = term_tokens
            else:
                filters[self.vocabulary_index] = self.term_id
        if not (filters or searchable_text):
            return []

        results = search_util.query(
            searchable_text, filters=filters, step=9999)

        #
        # 2. Prepare the results for display in the sidebar
        #

        portal = api.portal.get()
        proto_view = api.content.get_view('proto', portal, self.request)
        items = []
        for result in results:
            # Do checks to set the right classes for icons and candy

            # Does the item have a description?
            # If so, signal that with a class.
            cls_desc = (
                'has-description' if result.description
                else 'has-no-description'
            )
            ctype = proto_view.friendly_type2type_class(
                result.friendly_type_name)
            cls = 'item %s %s' % (ctype, cls_desc)

            item = {}
            item['cls'] = cls
            item['mime-type'] = ''
            item['url'] = result.url
            item['id'] = result.getId()
            item['title'] = result.title
            item['description'] = result.description
            item['dpi'] = (
                "source: #document-body; "
                "target: #document-body; "
                "history: record; "
                "url: %s" % result.url
            )
            items.append(item)

        return items

    @property
    def breadcrumb(self):
        app_url = self.context.absolute_url()
        if not self.term_id:
            return None
        else:
            term_path = self.vocabulary.getTermPath(self.term_id)
            if len(term_path) < 2:
                # A top level term
                return {'url': app_url, 'title': _(u'Document browser')}
            else:
                parent_term = term_path[-2]
                return {
                    'url': app_url + '?term-id=' + parent_term,
                    'title': parent_term,
                }

    @property
    def current_term(self):
        if self.term_id:
            return self.vocabulary.getTerm(self.term_id)

    @property
    def search_placeholder(self):
        term = self.current_term
        if term:
            return _(u"search_within_placeholder",
                     default=u"Search within the new '${sterm}'",
                     mapping={
                         u'sterm': format(term.value)})


class TaxonomySearchTile(GroupedSearchTile):

    @memoize
    def search_results(self):
        app_parameters = loads(self.context.app_parameters)
        self.vocabulary_name = app_parameters.get('vocabulary')
        self.vocabulary_index = app_parameters.get(
            'vocabulary_index', self.vocabulary_name)
        term_id = self.request.get('term-id')
        search_util = getUtility(ISiteSearch)
        if self.vocabulary_index not in search_util.facet_fields:
            log.error(
                'There is no search facet for the vocabulary named: {}'
                .format(self.vocabulary_name)
            )
            return []
        else:
            pt = api.portal.get_tool('portal_types')
            types = [
                t for t in pt.keys() if t not in self._types_not_to_search_for
            ]
            return search_util.query(
                filters={
                    'portal_type': types,
                    self.vocabulary_index: safe_unicode(term_id),
                },
                step=9999,
            )

    @memoize
    def results_sorted_groups(self):
        ''' Return the groups
        '''
        groups = super(TaxonomySearchTile, self).results_sorted_groups()
        if groups:
            return groups
        else:
            group_by = self.request.get('group-by', 'first-letter')
            if group_by == 'workspace':
                return sorted(self.results_by_workspace().keys())
            elif group_by == 'author':
                return sorted(self.results_by_author().keys())

    @memoize
    def results_grouped(self):
        ''' Dispatch to the relevant method to group the results
        '''
        results = super(TaxonomySearchTile, self).results_grouped()
        if results:
            return results
        else:
            group_by = self.request.get('group-by', 'first-letter')
            if group_by == 'workspace':
                return self.results_by_workspace()
            elif group_by == 'author':
                return self.results_by_author()

    @memoize
    def results_by_workspace(self):
        ''' Return the list of results grouped by workspace
        '''
        by_path = defaultdict(list)
        by_title = defaultdict(list)
        for result in self.search_results():
            path = result.path.split('/')
            if path[2] == 'workspaces' and len(path) > 2:
                workspace_path = '/'.join(path[:4])
                by_path[workspace_path].append(result)

        search_utility = getUtility(ISiteSearch)
        workspaces = search_utility.query(
            filters={
                'portal_type': [
                    'ploneintranet.workspace.workspacefolder',
                    'ploneintranet.workspace.case',
                ],
                'path': by_path.keys(),
            },
            step=9999,
        )
        for workspace in workspaces:
            by_title[workspace.title.encode('utf-8')] = by_path[workspace.path]
        for key in by_title.keys():
            by_title[key] = sorted(
                by_title[key], key=lambda x: x.modified, reverse=True)
        return by_title

    @memoize
    def results_by_author(self):
        ''' Return the list of results grouped by author
        '''
        by_user_profile_paths = defaultdict(list)
        by_user_name = defaultdict(list)
        portal_path = '/'.join(api.portal.get().getPhysicalPath())
        for result in self.search_results():
            user_id = result.get('Creator', _(u'Unknown'))
            user_profile_path = portal_path + '/profiles/' + user_id
            by_user_profile_paths[user_profile_path].append(result)
        search_utility = getUtility(ISiteSearch)
        user_profiles = search_utility.query(
            filters={
                'portal_type': 'ploneintranet.userprofile.userprofile',
                'path': by_user_profile_paths.keys(),
            },
            step=9999,
        )
        for user_profile in user_profiles:
            by_user_name[user_profile.title] = by_user_profile_paths[
                user_profile.path]
        for key in by_user_name.keys():
            by_user_name[key] = sorted(
                by_user_name[key], key=lambda x: x.modified, reverse=True)
        return by_user_name
