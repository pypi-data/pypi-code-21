from eureqa.analysis.components.base import _Component
from eureqa.utils.jsonrest import _JsonREST

class _Table(_Component):
    """ Low level Table component for showing tables within an analyis. See :class:`TableBuilder` for creating tables.
    """

    _component_type_str = 'TABLE'

    def __init__(self, table_id=None, columns=None, defaultSort=None, filters=None, searchBoxAttributes=None,
                 pageSizes=None, searchBoxPlaceholder=None, striped=None, title=None,
                 _analysis=None, _component_id=None, _component_type=None):
        super(_Table, self).__init__(_analysis=_analysis, _component_id=_component_id, _component_type=_component_type)

        if table_id is not None:
            self._table_id = table_id

        if columns is not None:
            self._columns = columns

        if defaultSort is not None:
            self._defaultSort = defaultSort

        if filters is not None:
            self._filters = filters

        if searchBoxAttributes is not None:
            self._searchBoxAttributes = searchBoxAttributes

        if pageSizes is not None:
            self._pageSizes = pageSizes

        if searchBoxPlaceholder is not None:
            self._searchBoxPlaceholder = searchBoxPlaceholder

        if striped is not None:
            self._striped = striped

        if title is not None:
            self._title = title


    @property
    def table_id(self):
        return self._table_id

    @table_id.setter
    def table_id(self, val):
        self._table_id = val
        self._update()


    @property
    def columns(self):
        return self._columns

    @columns.setter
    def columns(self, val):
        self._columns = val
        self._update()


    @property
    def defaultSort(self):
        return self._defaultSort

    @defaultSort.setter
    def defaultSort(self, val):
        self._defaultSort = val
        self._update()


    @property
    def filters(self):
        return self._filters

    @filters.setter
    def filters(self, val):
        self._filters = val
        self._update()


    @property
    def searchBoxAttributes(self):
        return self._searchBoxAttributes

    @searchBoxAttributes.setter
    def searchBoxAttributes(self, val):
        self._searchBoxAttributes = val
        self._update()


    @property
    def pageSizes(self):
        return self._pageSizes

    @pageSizes.setter
    def pageSizes(self, val):
        self._pageSizes = val
        self._update()


    @property
    def searchBoxPlaceholder(self):
        return self._searchBoxPlaceholder

    @searchBoxPlaceholder.setter
    def searchBoxPlaceholder(self, val):
        self._searchBoxPlaceholder = val
        self._update()


    @property
    def striped(self):
        return self._striped

    @striped.setter
    def striped(self, val):
        self._striped = val
        self._update()


    @property
    def title(self):
        return self._title

    @title.setter
    def title(self, val):
        self._title = val
        self._update()



    def _fields(self):
        return super(_Table, self)._fields() + [ 'table_id', 'columns', 'defaultSort', 'filters', 'searchBoxAttributes', 'pageSizes', 'searchBoxPlaceholder', 'striped', 'title' ]
