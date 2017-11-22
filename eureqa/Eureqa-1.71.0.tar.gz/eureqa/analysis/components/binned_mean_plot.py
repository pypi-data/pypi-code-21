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

from eureqa.analysis.components.base import _TwoVariablePlotComponent
from eureqa.utils.jsonrest import _JsonREST

class BinnedMeanPlot(_TwoVariablePlotComponent):
    """Represents a binned mean plot component on the server.

    For example::

        p = BinnedMeanPlot(d, axis_labels={'x': 'the x var', 'y' : 'the y var'}, label_format={'y':'.3s'}, x_var='W', y_var='A', needs_guides=True)
        analysis.create_card(p)


    :param DataSource datasource: The data source containing the data to be plotted.
    :param str x_var: The X-axis variable for the card's plot.
    :param str y_var: The Y-axis variable for the card's plot.
    :param bool needs_guides: Whether the card needs guides.
    :param XYMap axis_labels: Axis labels for this card's plot.  Set keys "x" and "y" to set the X and Y axis labels.
    :param XYMap label_format: Label format for this card.  Set keys "x" and "y" to set the X and Y axis printf-style format-strings; for example, ".3s".

    :var str ~eureqa.analysis_cards.two_variable_plot.TwoVariablePlot.title: The title of the card
    :var str ~eureqa.analysis_cards.two_variable_plot.TwoVariablePlot.x_var: The X-axis variable for the card's plot
    :var str ~eureqa.analysis_cards.two_variable_plot.TwoVariablePlot.y_var: The Y-axis variable for the card's plot
    :var bool ~eureqa.analysis_cards.two_variable_plot.TwoVariablePlot.needs_guides: Whether the card needs guides
    :var XYMap ~eureqa.analysis_cards.two_variable_plot.TwoVariablePlot.axis_labels: Axis labels for this card's plot.  Set member fields "x" and "y" to set the X and Y axis labels.
    :var XYMap ~eureqa.analysis_cards.two_variable_plot.TwoVariablePlot.label_format: Label format for this card.  Set member fields "x" and "y" to set the X and Y axis printf-style format-strings; for example, ".3s".
    """

    _component_type_str = 'BINNED_MEAN_PLOT'

    def __init__(self, datasource=None, axis_labels=None,
                 label_format=None, needs_guides=None, x_var=None, y_var=None,
                 _analysis=None, _component_id=None, _component_type=None):
        if datasource is not None:
            # Set the property.  Also sets the ID.
            self.datasource = datasource
            self._eureqa = datasource._eureqa

        if axis_labels is not None:
            self.axis_labels = axis_labels

        if label_format is not None:
            self.label_format = label_format

        if needs_guides is not None:
            self.needs_guides = needs_guides

        if x_var is not None:
            self.x_var = x_var

        if y_var is not None:
            self.y_var = y_var

        super(BinnedMeanPlot, self).__init__(_analysis=_analysis, _component_id=_component_id, _component_type=_component_type)

    @property
    def datasource(self):
        """The data source providing data for this component

        :return: data source providing data for this card
        """
        if hasattr(self, "_eureqa"):
            return self._eureqa.get_data_source_by_id(self._datasource_id)

    @datasource.setter
    def datasource(self, val):
        self._datasource_id = val._data_source_id
        self._eureqa = val._eureqa
        self._update()


    @property
    def axis_labels(self):
        """The axis labels for this card

        defaults to:
        ::

            { 'x': x_var, 'y': y_var }

        :return: Axis labels for this card
        :rtype: XYMap
        """
        return self.XYMap(self, getattr(self, "_axisLabels", {"x":"","y":""}))

    @axis_labels.setter
    def axis_labels(self, val):
        if hasattr(val, "x") and hasattr(val, "y"):
            val = {"x": val.x, "y": val.y}
        self._axisLabels = val
        self._update()


    @property
    def label_format(self):
        """Label format for this card.  Set keys "x" and "y" to set the X and Y axis printf-style format-strings; for example, ".3s".

        defaults to:
        ::

            { 'x': '.3s', 'y': '.2f' }

        :rtype: XYMap
        """
        return self.XYMap(self, getattr(self, "_labelFormat", {"x":"","y":""}))

    @label_format.setter
    def label_format(self, val):
        if hasattr(val, "x") and hasattr(val, "y"):
            val = {"x": val.x, "y": val.y}
        self._labelFormat = val
        self._update()


    @property
    def needs_guides(self):
        """Does this card need guides?

         :return: Whether this card needs guides
         :rtype: bool
         """
        return getattr(self, "_needsGuides", None)

    @needs_guides.setter
    def needs_guides(self, val):
        self._needsGuides = val
        self._update()


    @property
    def x_var(self):
        """The X variable for this card.

        :return: X variable for this card
        :rtype: str
        """
        return getattr(self, "_x_var", None)

    @x_var.setter
    def x_var(self, val):
        self._x_var = val
        self._update()


    @property
    def y_var(self):
        """The Y variable for this card.

        :return: Y variable for this card
        :rtype: str
        """
        return getattr(self, "_y_var", None)

    @y_var.setter
    def y_var(self, val):
        self._y_var = val
        self._update()


    def _fields(self):
        return super(BinnedMeanPlot, self)._fields() + \
               [ 'datasource_id', 'axisLabels', 'labelFormat', 'needsGuides', 'x_var', 'y_var' ]
