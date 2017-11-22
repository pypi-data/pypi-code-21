# Copyright (c) 2017, Nutonian Inc
# All rights reserved.
#
# Redistribution and use in source and binary forms, with or without
# modification, are permitted provided that the following conditions are met:
#   * Redistributions of source code must retain the above copyright
#     notice, this list of conditions and the following disclaimer.
#   * Redistributions in binary form must reproduce the above copyright
#     notice, this list of conditions and the following disclaimer in the
#     documentation and/or other materials provided with the distribution.
#   * Neither the name of the Nutonian Inc nor the
#     names of its contributors may be used to endorse or promote products
#     derived from this software without specific prior written permission.
#
# THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS "AS IS" AND
# ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE IMPLIED
# WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE ARE
# DISCLAIMED. IN NO EVENT SHALL NUTONIAN INC BE LIABLE FOR ANY
# DIRECT, INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY, OR CONSEQUENTIAL DAMAGES
# (INCLUDING, BUT NOT LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR SERVICES;
# LOSS OF USE, DATA, OR PROFITS; OR BUSINESS INTERRUPTION) HOWEVER CAUSED AND
# ON ANY THEORY OF LIABILITY, WHETHER IN CONTRACT, STRICT LIABILITY, OR TORT
# (INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT OF THE USE OF THIS
# SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.

from eureqa.analysis.components.base import _Component
from eureqa.utils.jsonrest import _JsonREST

class ByRowPlot(_Component):
    """
    Represents a line graph for plotting variables by row.

    For example::

       p = ByRowPlot(d, x_var='W', focus_variable='W', plotted_variables=['A'], should_center=True)
       analysis.create_card(p)


    :param eureqa.DataSource datasource: Data source for the component's data
    :param str x_var: Name of the variable to plot as the X axis
    :param list plotted_variables: List of variable names to plot.
    :param str focus_variable: Name of the variable in :attr:`plotted_variables` to bring to the foreground (required)
    :param bool should_center: Should the plot be centered?
    :param bool should_scale: Should the plot scale?

    :var str eureqa.analysis.components.variable_line_graph.ByRowPlot.focus_variable: Focused (foreground) variable for the component.  Must be a member of :attr:`plotted_variables`
    :var str eureqa.analysis.components.variable_line_graph.ByRowPlot.x_var: Name of the variable to plot as the X axis
    :var list eureqa.analysis.components.variable_line_graph.ByRowPlot.plotted_variables: Variables to plot.  (List of string variable names.)
    :var bool eureqa.analysis.components.variable_line_graph.ByRowPlot.should_center: Should the plot be centered?
    :var bool eureqa.analysis.components.variable_line_graph.ByRowPlot.should_scale: Should the plot scale?
    """

    _component_type_str = 'VARIABLE_LINE_GRAPH'

    def __init__(self, datasource=None, x_var=None, plotted_variables=None, focus_variable=None, should_center=None,
                 should_scale=None, _analysis=None, _component_id=None, _component_type=None):
        # Set 'self._options' first; property setters used below populate it
        self._options = {}

        if datasource is not None:
            self.datasource = datasource

        if x_var is not None:
            self.x_var = x_var

        if plotted_variables is not None:
            self.plotted_variables = plotted_variables

        if focus_variable is not None:
            self.focus_variable = focus_variable

        if should_center is not None:
            self.should_center = should_center

        if should_scale is not None:
            self.should_scale = should_scale

        super(ByRowPlot, self).__init__(_analysis=_analysis, _component_id=_component_id, _component_type=_component_type)

    @property
    def datasource(self):
        """The data source providing data for this component

        :return: data source providing data for this component
        """
        if hasattr(self, "_eureqa"):
            return self._eureqa.get_data_source_by_id(self._datasource_id)

    @datasource.setter
    def datasource(self, val):
        self._datasource_id = val._data_source_id
        self._eureqa = val._eureqa
        self._update()


    @property
    def focus_variable(self):
        """The variable that is currently in focus (in the foreground) for this component.
        Must be a member of :attr:`plotted_variables`.

        :return: focus_variable for this component
        :rtype: str
        """

        return self._options.get('focusVariable')

    @focus_variable.setter
    def focus_variable(self, val):
        self._options['focusVariable'] = val
        self._update()

    @property
    def x_var(self):
        """The X-axis variable for this component

        :return: the name of the X-axis variable for this component
        :rtype: str
        """

        return self._options.get('xAxisVariable')

    @x_var.setter
    def x_var(self, val):
        self._options['xAxisVariable'] = val
        self._update()

    @property
    def plotted_variables(self):
        """The plotted variables for this component.

        :return: List of the names of the variables being plotted against the X axis
        :rtype: list
        """
        return self._options.get('plottedVariables')

    @plotted_variables.setter
    def plotted_variables(self, val):
        self._options['plottedVariables'] = val
        self._update()

    @property
    def should_center(self):
        """The should_center option for this component.

        :return: whether this plot should be centered
        :rtype: bool
        """

        return self._options.get('shouldCenter')

    @should_center.setter
    def should_center(self, val):
        self._options['shouldCenter'] = val
        self._update()

    @property
    def should_scale(self):
        """The should_scale option for this component.

        :return: whether this plot should be scaled
        :rtype: bool
        """
        return self._options.get('shouldScale')

    @should_scale.setter
    def should_scale(self, val):
        self._options['shouldScale'] = val
        self._update()


    def _fields(self):
        return super(ByRowPlot, self)._fields() + [ 'datasource_id', 'options' ]
