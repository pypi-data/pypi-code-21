import json


class DashboardsMixin(object):

    def get_dashboards(self, project_id):
        """Return all dashboard for the given project.

        :param project_id: Project identifier

        :returns: A list of dashboard dictionaries.

        Example::

            >>> client.get_dashboards('2aEVClLRRA-vCCIvnuEAvQ')
            [{u'id': u'G0Tm2SQcTqu2d4GvfyrsMg',
              u'search': {u'query': u'Test'},
              u'title': u'Test',
              u'type': u'dashboard',
              u'widgets': [{u'col': 1,
                            u'id': 1,
                            u'row': 1,
                            u'size_x': 1,
                            u'size_y': 1,
                            u'title': u'Search Results',
                            u'type': u'Search'}]}]
        """
        url = '%(ep)s/v0/%(tenant)s/projects/%(project_id)s/dashboards' % {
            'ep': self.topic_api_url,
            'tenant': self.tenant,
            'project_id': project_id,
        }
        res = self._perform_request('get', url)
        return self._process_response(res)

    def get_dashboard(self, project_id, dashboard_id):
        """Return a specific dashboard from the given project.

        :param project_id: Project identifier
        :param dashboard_id: Dashboard identifier

        :returns: A dictionary of the given dashboard.

        Example::

            >>> client.get_dashboard('2aEVClLRRA-vCCIvnuEAvQ',
            ...                      'G0Tm2SQcTqu2d4GvfyrsMg')
            {u'id': u'G0Tm2SQcTqu2d4GvfyrsMg',
             u'search': {u'query': u'Test'},
             u'title': u'Test',
             u'type': u'dashboard',
             u'theme_id': u'G0Tm2SQcTqu2d4GvfyrsMg',
             u'widgets': [{u'col': 1,
                           u'id': 1,
                           u'row': 1,
                           u'size_x': 1,
                           u'size_y': 1,
                           u'title': u'Search Results',
                           u'type': u'Search'}]}
        """
        url = ('%(ep)s/v0/%(tenant)s/projects/%(project_id)s/'
               'dashboards/%(dashboard_id)s') % {
                   'ep': self.topic_api_url,
                   'tenant': self.tenant,
                   'project_id': project_id,
                   'dashboard_id': dashboard_id,
               }
        res = self._perform_request('get', url)
        return self._process_response(res)

    def new_dashboard(self, project_id, title, search=None, type=None,
                      column_count=None, row_height=None, theme_id=None,
                      hide_title=None, reset_placement=None, sections=None,
                      sidepanel=None, loaders=None):
        """Create a new dashboard.

        :param project_id: Project identifier
        :param title: Dashboard title
        :param search: Search parameters for the dashboard
        :param type: Dashboard type (`dashboard` or `result`). The latter is
            used for the chart view in the UI and not displayed as a dashboard
            tab.
        :param column_count: Number of columns on this dashboard. Used by
            the frontend to render the widgets in the correct size.
        :param row_height: Height in pixels of each row on this dashboard. Used
            by the frontend to render the widgets in the correct size.
        :param theme_id: Dashboard theme identifier
        :param hide_title: Boolean, whether to hide the dashboard title when
            shared
        :param reset_placement: Position of the filter reset flyout, either
            `left` or `right` is supported
        :param sections: List of dashboard sections
        :param sidepanel: Boolean, whether to show the sidepanel or not

        :returns: A list of dashboard dictionaries.

        Example::

            >>> client.new_dashboard('2aEVClLRRA-vCCIvnuEAvQ', title='Sample')
                {u'column_count': 16,
                 u'hide_title': False,
                 u'id': u'8N38s1XsTAKE39TFC4kTkg',
                 u'reset_placement': u'right',
                 u'row_height': 55,
                 u'search': None,
                 u'sections': [],
                 u'sidepanel': False,
                 u'theme': {
                     u'definition': {
                         u'activeColor': u'#e55100',
                         u'background': u'#ffffff',
                         u'borderColor': u'#BDBDBD',
                         u'borderRadius': 2,
                         u'headerHeight': 30,
                         u'marginBottom': 70,
                         u'marginLeft': 10,
                         u'marginRight': 10,
                         u'marginTop': 10,
                         u'titleColor': u'#616161',
                         u'titleFontSize': 17,
                         u'titleFontWeight': u'normal',
                         u'titleTextAlignment': u'left',
                         u'widgetGap': 5,
                         u'widgets': {
                             u'Chord': {
                                 u'activeBackground': u'#f5f5f5',
                                 u'activeColor': u'#e55100',
                                 u'background': u'#ffffff',
                                 u'chartColorScheme': [
                                     u'#4b8ecc',
                                     u'#348f5f',
                                     u'#ec6a2b',
                                     u'#807dba',
                                     u'#fec44f',
                                     u'#009994',
                                     u'#d43131',
                                     u'#0d7074'
                                 ],
                                 u'headerAlignment': u'left',
                                 u'headerBackground': u'#F5F5F5',
                                 u'headerColor': u'#b6b6b6',
                                 u'headerFontSize': 17,
                                 u'headerFontWeight': u'normal',
                                 u'linkBackground': u'#f5f5f5',
                                 u'linkColor': u'#2196F3',
                                 u'paddingBottom': 10,
                                 u'paddingLeft': 10,
                                 u'paddingRight': 10,
                                 u'paddingTop': 5,
                                 u'primaryButtonGradient1': u'#1484f9',
                                 u'primaryButtonGradient2': u'#156fcc',
                                 u'textColor': u'#212121'
                                 },
                             u'Connection': {
                                 u'color': u'#212121',
                                 u'fontAlign': u'center',
                                 u'fontSize': u'13',
                                 u'fontWeight': u'normal',
                                 u'hoverColor': u'#E3F2FD',
                                 u'labelColor': u'#212121',
                                 u'primaryButtonGradient1': u'#FFECB3',
                                 u'primaryButtonGradient2': u'#EF5350'
                             },
                             u'Facets': {u'labelColor': u'#212121'},
                             u'FacetsHistogram': {
                                 u'labelColor': u'#212121',
                                 u'legendColor': u'#212121'
                             },
                             u'FacetsList': {
                                 u'activeColor': u'#e55100',
                                 u'barColor': u'#1484f9',
                                 u'facetValueColor': u'#bdbdbd'
                             },
                             u'FacetsTable': {
                                 u'activeBackground': u'#F5F5F5',
                                 u'activeColor': u'#e55100',
                                 u'headerColor': u'#616161'
                             },
                             u'Frequency': {u'labelColor': u'#212121'},
                             u'HorizontalResultList': {
                                 u'linkColor': u'#2196F3',
                                 u'subtitleColor': u'#616161'
                             },
                             u'IFrame': {},
                             u'Keywords': {
                                 u'barColor': u'#1484f9',
                                 u'headerColor': u'#616161',
                                 u'linkColor': u'#2196F3'
                             },
                             u'PredQuery': {
                                 u'activeBackground': u'#F5F5F5',
                                 u'activeColor': u'#e55100'
                             },
                             u'Search': {
                                 u'activeColor': u'#e55100',
                                 u'titleColor': u'#616161',
                                 u'titleColorRead': u'#212121',
                                 u'titleFontSize': 15,
                                 u'titleFontSizeRead': 15,
                                 u'titleFontWeight': u'bolder',
                                 u'titleFontWeightRead': u'bolder',
                                 u'titleTextAlignment': u'left',
                                 u'titleTextAlignmentRead': u'left'
                             },
                             u'SearchQuery': {
                                 u'backgroundColor': u'#428bca',
                                 u'borderColor': u'#1e88e5',
                                 u'textColor': u'#ffffff'
                             },
                             u'SignificantTerms': {},
                             u'TagCloud': {},
                             u'default': {
                                 u'activeBackground': u'#f5f5f5',
                                 u'activeColor': u'#e55100',
                                 u'background': u'#ffffff',
                                 u'chartColorScheme': [
                                     u'#64b5f6',
                                     u'#E57373',
                                     u'#FFD54F',
                                     u'#81C784',
                                     u'#7986CB',
                                     u'#4DD0E1',
                                     u'#F06292',
                                     u'#AED581',
                                     u'#A1887F',
                                     u'#FFB74D',
                                     u'#4FC3F7',
                                     u'#FF8A65',
                                     u'#DCE775',
                                     u'#BA68C8'
                                 ],
                                 u'headerAlignment': u'left',
                                 u'headerBackground': u'#F5F5F5',
                                 u'headerColor': u'#616161',
                                 u'headerFontSize': 17,
                                 u'headerFontWeight': u'normal',
                                 u'linkBackground': u'#f5f5f5',
                                 u'linkColor': u'#2196F3',
                                 u'paddingBottom': 10,
                                 u'paddingLeft': 10,
                                 u'paddingRight': 10,
                                 u'paddingTop': 5,
                                 u'textColor': u'#212121'
                             }
                         }
                     },
                     u'id': u'ofVfiQ-uRWSZeGFZspH9nQ',
                     u'scope': u'default',
                     u'title': u'Squirro Default'},
                    u'theme_id': u'ofVfiQ-uRWSZeGFZspH9nQ',
                    u'title': u'foo',
                    u'type': u'dashboard'
                }
        """
        url = '%(ep)s/v0/%(tenant)s/projects/%(project_id)s/dashboards' % {
            'ep': self.topic_api_url,
            'tenant': self.tenant,
            'project_id': project_id,
        }
        data = {
            'title': title,
            'search': search,
            'type': type,
            'sections': sections,
            'sidepanel': sidepanel,
            'loaders': loaders
        }
        if column_count:
            data['column_count'] = column_count
        if row_height:
            data['row_height'] = row_height
        if theme_id:
            data['theme_id'] = theme_id
        if hide_title:
            data['hide_title'] = hide_title
        if reset_placement:
            data['reset_placement'] = reset_placement
        headers = {'Content-Type': 'application/json'}
        res = self._perform_request(
            'post', url, data=json.dumps(data), headers=headers)
        return self._process_response(res, [201])

    def modify_dashboard(self, project_id, dashboard_id, title=None,
                         search=None, type=None, column_count=None,
                         row_height=None, theme_id=None, hide_title=None,
                         reset_placement=None, sections=None, sidepanel=None,
                         loaders=None, widgets=None):
        """Update a dashboard.

        :param project_id: Project identifier
        :param dashboard_id: Dashboard identifier
        :param title: Dashboard title
        :param search: Search parameters for the dashboard
        :param type: Dashboard type
        :param column_count: Number of columns on this dashboard. Used by
            the frontend to render the widgets in the correct size.
        :param row_height: Height in pixels of each row on this dashboard. Used
            by the frontend to render the widgets in the correct size.
        :param theme_id: Associated theme id
        :param hide_title: Boolean, whether to hide the dashboard title when
            shared
        :param reset_placement: Position of the filter reset flyout, either
            `left` or `right` is supported
        :param sections: List of dashboard sections
        :param widgets: List of dashboard widgets (legacy support)
        :param sidepanel: Boolean, whether to show the sidepanel or not

        :returns: A dictionary of the updated dashboard.

        Example::

            >>> client.modify_dashboard('2aEVClLRRA-vCCIvnuEAvQ',
            ...                         'YagQNSecR_ONHxwBmOkkeQ',
            ...                         search={'query': 'Demo'})
        """
        if sections and widgets:
            raise ValueError('Sections and widgets arguments can not be mixed.')

        url = ('%(ep)s/v0/%(tenant)s/projects/%(project_id)s/'
               'dashboards/%(dashboard_id)s') % {
                   'ep': self.topic_api_url,
                   'tenant': self.tenant,
                   'project_id': project_id,
                   'dashboard_id': dashboard_id,
               }
        data = {
            'title': title,
            'search': search,
            'type': type,
            'column_count': column_count,
            'row_height': row_height,
            'theme_id': theme_id,
            'hide_title': hide_title,
            'reset_placement': reset_placement,
            'sections': sections,
            'sidepanel': sidepanel,
            'loaders': loaders
        }
        if widgets is not None:
            data['widgets'] = widgets

        post_data = {}
        for key, value in data.iteritems():
            if value is not None:
                post_data[key] = value
        headers = {'Content-Type': 'application/json'}
        res = self._perform_request(
            'put', url, data=json.dumps(post_data), headers=headers)
        return self._process_response(res)

    def move_dashboard(self, project_id, dashboard_id, after):
        """Move a dashboard.

        :param project_id: Project identifier
        :param dashboard_id: Dashboard identifier
        :param after: The dashboard identifier after which the dashboard should
            be moved. Can be `None` to move the dashboard to the beginning
            of the list.

        :returns: No return value.

        Example::

            >>> client.move_dashboard('2aEVClLRRA-vCCIvnuEAvQ',
            ...                       'Ue1OceLkQlyz21wpPqml9Q',
            ...                       'nJXpKUSERmSgQRjxX7LrZw')
        """
        url = ('%(ep)s/v0/%(tenant)s/projects/%(project_id)s/'
               'dashboards/%(dashboard_id)s/move') % {
                   'ep': self.topic_api_url,
                   'tenant': self.tenant,
                   'project_id': project_id,
                   'dashboard_id': dashboard_id,
               }
        headers = {'Content-Type': 'application/json'}
        res = self._perform_request(
            'post', url, data=json.dumps({'after': after}), headers=headers)
        return self._process_response(res, [204])

    def delete_dashboard(self, project_id, dashboard_id):
        """Delete a specific dashboard from the given project.

        :param project_id: Project identifier
        :param dashboard_id: Dashboard identifier

        :returns: No return value.

        Example::

            >>> client.delete_dashboard('2aEVClLRRA-vCCIvnuEAvQ',
            ...                         'Ue1OceLkQlyz21wpPqml9Q')
        """
        url = ('%(ep)s/v0/%(tenant)s/projects/%(project_id)s/'
               'dashboards/%(dashboard_id)s') % {
                   'ep': self.topic_api_url,
                   'tenant': self.tenant,
                   'project_id': project_id,
                   'dashboard_id': dashboard_id,
               }
        res = self._perform_request('delete', url)
        return self._process_response(res, [204])
