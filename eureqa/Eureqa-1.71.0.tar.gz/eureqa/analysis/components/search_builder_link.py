from eureqa.analysis.components.base import _Component
from eureqa.utils.jsonrest import _JsonREST
from eureqa.search_settings import SearchSettings

class SearchBuilderLink(_Component):
    """
    Create a SearchBuilderLink component

    Example of using HtmlBlock with a SearchBuilderLink::

        # include a link to the search builder with nothing pre-populated
        search_builder_link = SearchBuilderLink()
        h = HtmlBlock('Click this link to open the pre-populated search builder: {0}'.format(analysis.html_ref(search_builder_link)))
        layout.add_component(h)

        # include a link to the search builder with settings pre-populated by a search template
        datasource = e.create_data_source("data_source_1", "tests/Nutrition.csv")
        search_builder_link = SearchBuilderLink(datasource=datasource,
                                                search_template=search_templates.SearchTemplates.Timeseries,
                                                min_delay=1,
                                                max_delay=10,
                                                target_variable='Calories',
                                                input_variables=['Steps', 'Weight', '(Protein (g))', '(Fat (g))'])
        h = HtmlBlock('Click this link to open the pre-populated search builder: {0}'.format(analysis.html_ref(search_builder_link)))
        layout.add_component(h)

    :param str link_text: the visible, clickable text for the link
    :param DataSource datasource: datasource to pre-populate the search builder with
    :param SearchTemplate search_template: search template information to pre-populate the search builder with
    :param int min_delay: the minimum delay used in a timeseries search
    :param int max_delay: the maximum delay used in a timeseries search
    :param str target_variable: the variable to search for models of
    :param str[] input_variables: the variables to use as inputs in the models
    """

    _component_type_str = 'SEARCH_BUILDER_LINK'

    def __init__(self,
                 link_text=None,
                 datasource=None,
                 search_template=None,
                 min_delay=None,
                 max_delay=None,
                 target_variable=None,
                 input_variables=None,
                 _analysis=None,
                 _component_id=None,
                 _component_type=None):

        # implementation details:
        # self.datasource is a property, property
        # self._datasource is the actual datasource object (cache of the datasource) which may or may not be fetched
        # self._datasource_id a string, and its setting/handling is handled by the JsonRest implementation'

        if link_text is not None:
            self._link_text = link_text
        else:
            self._link_text = "Search Builder"

        datasource_id = datasource._datasource_id if datasource is not None else None
        self._search_template_detail = SearchSettings(datasource_id=datasource_id,
                                                      search_template_id=search_template,
                                                      default_min_delay=min_delay,
                                                      maximum_history_absolute_rows=max_delay,
                                                      target_variable=target_variable,
                                                      input_variables=input_variables)

        super(SearchBuilderLink, self).__init__(_analysis=_analysis, _component_id=_component_id, _component_type=_component_type)


    @property
    def link_text(self):
        """The HTML text which will be wrapped with a link to the search builder.

        :rtype: str
        """
        return getattr(self, "_link_text", None)

    def _to_json(self):
        base = super(SearchBuilderLink, self)._to_json()
        if hasattr(self, '_link_text'): base['link_text'] = self._link_text
        base['search_detail'] = None
        if hasattr(self, '_search_template_detail'): base['search_detail'] = self._search_template_detail._to_json()
        return base

    def _from_json(self, body):
        super(SearchBuilderLink, self)._from_json(body)
        if 'link_text' in body:
            self._link_text = body['link_text']
        if 'search_detail' in body:
            self._search_template_detail = SearchSettings.from_json(None, body['search_detail'])
