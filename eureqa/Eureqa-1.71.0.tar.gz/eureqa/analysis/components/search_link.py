from eureqa.analysis.components.base import _Component
from eureqa.utils.jsonrest import _JsonREST

class SearchLink(_Component):
    """
    Create a link to a specified search

    Example of using HtmlBlock with a SearchLink::

        vl = SearchLink(search)
        h = HtmlBlock('Formatted <b>Card</b> in the Analysis, with reference to search {0}'.format(analysis.html_ref(vl)))
        analysis.create_card(h)


    :param Search search: the search to link to
    :param str link_text: (optional) the text to use for the search link is displayed
    """

    _component_type_str = 'SEARCH_LINK'

    def __init__(self, search=None, link_text=None, _analysis=None,  _component_id=None, _component_type=None):

        # implementation details:
        # self.datasource and self.search are properties
        # self._datasource and self._search is the actual datasource/search object  which may or may not be fetched
        # self._datasource_id and self._search_id are strings and

        if search is not None:
            self.search = search #invoke setter to set all fields

        if link_text is not None:
            self._link_text = link_text
        elif search is not None:
            self._link_text = search.name


        super(SearchLink, self).__init__(_analysis=_analysis, _component_id=_component_id, _component_type=_component_type)

    @property
    def search(self):
        """The search linked to

        :rtype: Search
        """
        # Note that the _search field is set by the underlying _Component
        # based on the _datasource_id string
        if hasattr(self, "_eureqa"):
            return self._eureqa._get_search_by_id(self._datasource_id, self._search_id)

    @search.setter
    def search(self, search):
        self._datasource_id = search._data_source_id
        self._search_id = search._id
        self._eureqa = search._eureqa
        self._update()

    @property
    def link_text(self):
        """The text to use for the search link when displayed.

        :return: the link text of this card
        :rtype: str"""
        return self._link_text

    @link_text.setter
    def link_text(self, val):
        self._link_text = val
        self._update()


    def _fields(self):
        return super(SearchLink, self)._fields() + [ 'datasource_id', 'search_id', 'link_text' ]
