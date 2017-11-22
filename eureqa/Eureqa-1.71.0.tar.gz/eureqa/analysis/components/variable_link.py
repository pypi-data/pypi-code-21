from eureqa.analysis.components.base import _Component

class VariableLink(_Component):
    """
    Create a VariableLink component

    Example of using HtmlBlock with a VariableLink::

        vl = VariableLink(d, 'X')
        h = HtmlBlock('Formatted <b>Card</b> in the Analysis, with reference to {0}'.format(analysis.html_ref(vl)))
        analysis.create_card(h)


    :param DataSource datasource: datasource from which to find the variable
    :param str variable_name: name of the variable
    """

    _component_type_str = 'VARIABLE_LINK'

    def __init__(self, datasource=None, variable_name=None, _analysis=None, _component_id=None, _component_type=None):

        # implementation details:
        # self.datasource is a property, property
        # self._datasource is the actual datasource object (cache of the datasource) which may or may not be fetched
        # self._datasource_id a string, and its setting/handling is handled by the JsonRest implementation'

        if datasource is not None:
            self.datasource = datasource

        if variable_name is not None:
            self._variable_name = variable_name

        super(VariableLink, self).__init__(_analysis=_analysis, _component_id=_component_id, _component_type=_component_type)

    @property
    def datasource(self):
        """The data source providing data for this component

        :rtype: DataSource
        """
        # Note that the _datasource field is set by the underlying _Component
        # based on the _datasource_id string
        if hasattr(self, "_eureqa"):
            return self._eureqa.get_data_source_by_id(self._datasource_id)

    @datasource.setter
    def datasource(self, val):
        self._datasource_id = val._data_source_id
        self._eureqa = val._eureqa
        self._update()


    @property
    def variable_name(self):
        """The name of the variable from this datasource to link to

        :rtype: str
        """
        return self._variable_name

    @variable_name.setter
    def variable_name(self, val):
        self._variable_name = val
        self._update()

    def _fields(self):
        return super(VariableLink, self)._fields() + [ 'datasource_id', 'variable_name' ]
