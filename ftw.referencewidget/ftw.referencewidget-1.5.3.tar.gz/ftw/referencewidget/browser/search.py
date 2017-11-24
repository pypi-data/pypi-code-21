from ftw.referencewidget.browser.utils import extend_with_batching
from ftw.referencewidget.browser.utils import get_root_path_from_source
from ftw.referencewidget.browser.utils import get_selectable_types
from ftw.referencewidget.browser.utils import get_sort_options
from ftw.referencewidget.browser.utils import get_sort_order_options
from ftw.referencewidget.browser.utils import get_traversal_types
from plone import api
from Products.CMFCore.utils import getToolByName
from Products.Five import BrowserView
import json


class SearchView(BrowserView):

    def __call__(self):

        json_prep = {'items': [],
                     'sortOnOptions': get_sort_options(self.request),
                     'sortOrderOptions': get_sort_order_options(self.request)}

        search_term = self.request.get('term')
        request_path = self.request.get('request_path')
        only_current_path = self.request.get('search_current_path') == '1'
        if not search_term:
            return json.dumps(json_prep)

        if not search_term.endswith("*"):
            search_term += "*"
        search_types = get_selectable_types(self.context)

        query = {'portal_type': search_types,
                 'Title': search_term,
                 'sort_order': self.request.get('sort_order',
                                                u'ascending').encode('utf-8'),
                 'sort_on': self.request.get('sort_on',
                                             u'modified').encode('utf-8')}
        if only_current_path and request_path:
            query['path'] = request_path

        query.update(self.context.traversal_query)

        root_path = get_root_path_from_source(self.context)
        if root_path:
            query['path'] = root_path

        catalog = getToolByName(self.context.context, 'portal_catalog')
        results = catalog(query)
        results, batch_html = extend_with_batching(self.context, results)

        json_prep['batching'] = batch_html

        traversel_type = get_traversal_types(self.context)
        plone = api.portal.get()
        for item in results:
            if only_current_path and request_path and item.getPath() == query['path']:
                continue

            contenttype = 'contenttype-' \
                + item.portal_type.replace('.', '-').lower()

            traversable = item.is_folderish and  \
                (item.portal_type in traversel_type)

            date = ' (%s)' % plone.toLocalizedTime(item.start) if item.start else ''

            label = '{0}{1} ({2})'.format(item.Title, date, item.getPath())
            json_prep['items'].append({'title': label,
                                       'path': item.getPath(),
                                       'selectable': True,
                                       'content-type': contenttype,
                                       'traversable': traversable
                                       })

        self.request.RESPONSE.setHeader("Content-type", "application/json")
        return json.dumps(json_prep)
