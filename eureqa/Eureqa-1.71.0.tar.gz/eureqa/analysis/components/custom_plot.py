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
from eureqa.utils.data_holder import DataHolder
from eureqa.data_source import DataSource

import warnings

class CustomPlot(_Component):
    """
    Represents a plot to be displayed in an analysis plot card.

    By calling the plot() method multiple times on one instance of this class, multiple lines and scatter plots can
    be superimposed on this object.

    :param DataSource datasource: The data source containing the data to be plotted.
    :param str width: Set manual dimensions for the plot in "px" units (e.g. 350px). Defaults to full panel width.
    :param str height: Set manual dimensions for the plot in "px" units. Defaults to a constant height of 400px.
    :param str x_axis_label: The label to use on the x axis of the plot.
    :param str y_axis_label: The label to use on the y axis of the plot.
    :param bool show_legend: Controls whether or not a legend will be used in the plot.
    :param bool zero_x_line: Draws a horizontal line through the origin
    :param bool zero_y_line: Draws a vertical line through the origin
    :param str x_tick_format: Format for x axis tick labels. Valid values are "date" or anything supported by D3: https://github.com/mbostock/d3/wiki/Formatting#d3_format. Defaults to our internal number format
    :param str y_tick_format: Format for y axis tick labels. Valid values are "date" or anything supported by D3: https://github.com/mbostock/d3/wiki/Formatting#d3_format. Defaults to our internal number format
    :param str guides_type: The type of value-guides to show when hovering over a point in the graph. Valid values are "XY", "YY" or False. XY guides will show the x and y values for the point under the cursor. YY guides will show the x and y values of each component for the data point closest to the cursor. False will turn off value guides.
    """

    _component_type_str = 'CUSTOM_GRAPH'

    def _fields(self):
        return super(CustomPlot, self)._fields() + ['options']

    def __init__(self,
                 datasource=None,
                 width=None,
                 height='400px',
                 x_axis_label=None,
                 y_axis_label=None,
                 show_legend=True,
                 zero_x_line=False,
                 zero_y_line=False,
                 x_tick_format=None,
                 y_tick_format=None,
                 guides_type="XY",
                 _analysis=None,
                 _component_id=None,
                 _component_type=None):
        """ Plot init """
        self._options = {
            'datasource_id': None,
            'plot':{
                'dimensions': {
                    'width': width,
                    'height': height
                },
                'x_axis_label': x_axis_label,
                'y_axis_label': y_axis_label,
                'legend': show_legend,
                'zero_x_line': zero_x_line,
                'zero_y_line': zero_y_line,
                'x_tick_format': x_tick_format,
                'y_tick_format': y_tick_format,
                'num_x_ticks': None,
                'num_y_ticks': None,
                'number_of_rows': 200,
                'guides': {
                    'type': guides_type
                }
        }, 'components':[]}
        if datasource is not None:
            datasource = datasource
        if guides_type is not None: self._options['plot']['guides'] = {'type':guides_type}
        self._data_holder = DataHolder()
        self._var_counter = 0

        super(CustomPlot, self).__init__(_analysis=_analysis, _component_id=_component_id, _component_type=_component_type)


    # This property is an ugly hack.
    # Its purpose is to enable the legacy syntax "myCustomPlot.plot.plot()"
    # (for compatibility with older Analysis Cards)
    # while supporting the new flat syntax "myCustomPlot.plot()".
    # If/when we're able to delete it, we should rename the "_plot()" method below to "plot()".
    @property
    def plot(self):
        """
        Add new data to the plot with the specified options.

        If a datasource is specified, x and y can be provided as expressions in terms of the variables in that datasource. Otherwise, x and y must be lists of data of identical length.

        :param list x: X axis data. Either a list of input values, or if a datasource is specified, an expression in terms of that datasource's variables.
        :param list y: Y axis data. Either a list of input values, or if a datasource is specified, an expression in terms of that datasource's variables.
        :param DataSource datasource: If provided, a specific DataSource to use as a base for the variables to be plotted.
        :param str style: A matplotlib-like style string of 'o' or '-' or '-o' to indicate circle, line, or line-circle, respectively.
        :param str color: CSS color.
        :param int line_width: The width of the line, if applicable.
        :param int circle_radius: The radius of each circle, if applicable.
        :param bool use_in_plot_range: The chart auto-computes the x and y axis ranges based on the data for each component. If you want to add a component, but have its data not be used to compute the x and y axis ranges, set this value to False. For example, if you want to make a scatter plot, with a trend line going through it, then setting this field to False for the trend-line component will make the chart snugly fit the points, with the trend line extending beyond.
        :param list error_bars_upper_values: Specifies the tops of error bars. Either a list of values, or if a datasource is specified, an expression in terms of that datasource's variables. If input values is a list, then this must be a list as well.
        :param list error_bars_lower_values: Specifies the bottoms of error bars. Either a list of values, or if a datasource is specified, an expression in terms of that datasource's variables. If input values is a list, then this must be a list as well.
        :param str legend_label: A string label to be used in the legend. If unspecified, this plot will not appear in the legend.
        :param str tooltip_template: A basic template string that can be used to provide custom mouseover tooltips to plot points. It is passed the current point's x/y values as ``{{x_value}}`` and ``{{y_value}}``. It is also passed the current tooltip as ``{{tooltip}}`` if a ``tooltips`` parameter is provided.
        :param list tooltips: A list of per-point tooltip values. If specified, adds a mouseover tooltip to each point on the plot. If a ``tooltip_template`` has been provided, tooltips will be passed into the template context as ``{{tooltip}}``.

        **Tooltip examples:**

            * ``tooltips`` parameter::

                tooltips=["A", "B", "C"]

                # Point one will have a tooltip of "A"
                # Point two will have a tooltip of "B"
                # Point three will have a tooltip of "C"

            * ``tooltip_template`` parameter::

                tooltip_template="Point: {{x_value}}, {{y_value}}"

              Let's say we're plotting two points: ``[{x: 0, y: 0}, {x: 1, y: 1}]``. With the template above, their tooltips will render as::

                "Point: 0, 0" and "Point: 1, 1"

            * ``tooltips`` and ``tooltip_template`` parameters:

              Given points ``[{x: 0, y: 0}, {x: 1, y: 1}]``::

                tooltip_template="Item {{tooltip}} has a value of {{x_value}}, {{y_value}}",
                tooltips=["A", "B"]

              will generate the following tooltips::

                "Item A has a value of 0, 0"
                "Item B has a value of 1, 1"
        """
        class WrapperClass(object):
            def __init__(self, parent):
                self.__dict__["_parent"] = parent
            def __call__(self, *args, **kwargs):
                return self._parent._plot(*args, **kwargs)
            def __getattr__(self, name):
                warnings.warn("'CustomPlot.plot' field is deprecated.  Use 'CustomPlot' directly instead.",
                              DeprecationWarning)
                return getattr(self.__dict__["_parent"], name)
            def __setattr__(self, name, val):
                return setattr(self._parent, name, val)
            def __delattr__(self, name):
                return delattr(self._parent, name)
        return WrapperClass(self)

    @property
    def width(self):
        """
        The width of the plot.  Represented as a string containing a valid CSS "width" attribute; for example, '400px'.

        :rtype: str
        """
        return self._options.get("dimensions").get("width")

    @width.setter
    def width(self, val):
        self._options["dimensions"]["width"] = val


    @property
    def height(self):
        """
        The height of the plot.  Represented as a string containing a valid CSS "width" attribute; for example, '300px'.

        :rtype: str
        """
        return self._options.get("dimensions").get("height")

    @height.setter
    def height(self, val):
        self._options["dimensions"]["height"] = val
        self._update()


    @property
    def x_axis_label(self):
        """
        The label of the plot's X axis

        :rtype: str
        """
        return self._options.get("x_axis_label")

    @x_axis_label.setter
    def x_axis_label(self, val):
        self._options["x_axis_label"] = val
        self._update()


    @property
    def y_axis_label(self):
        """
        The label of the plot's Y axis

        :rtype: str
        """
        return self._options.get("y_axis_label")

    @y_axis_label.setter
    def y_axis_label(self, val):
        self._options["y_axis_label"] = val
        self._update()


    @property
    def show_legend(self):
        """
        Whether or not the legend should be shown

        :rtype: bool
        """
        return self._options.get("legend")

    @show_legend.setter
    def show_legend(self, val):
        self._options["legend"] = val
        self._update()


    @property
    def zero_x_line(self):
        """
        Whether an axis line should be shown for x=0

        :rtype: bool
        """
        return self._options.get("zero_x_line")

    @zero_x_line.setter
    def zero_x_line(self, val):
        self._options["zero_x_line"] = val
        self._update()


    @property
    def zero_y_line(self):
        """
        Whether an axis line should be shown for y=0

        :rtype: bool
        """
        return self._options.get("zero_y_line")

    @zero_y_line.setter
    def zero_y_line(self, val):
        self._options["zero_y_line"] = val
        self._update()


    @property
    def x_tick_format(self):
        """
        Format for x axis tick labels.
        Valid values are "date" or anything supported by D3:
        https://github.com/mbostock/d3/wiki/Formatting#d3_format. Defaults to our internal number format

        :return: str
        """
        return self._options.get("x_tick_format")

    @x_tick_format.setter
    def x_tick_format(self, val):
        self._options["x_tick_format"] = val
        self._update()


    @property
    def y_tick_format(self):
        """
        Format for y axis tick labels.
        Valid values are "date" or anything supported by D3:
        https://github.com/mbostock/d3/wiki/Formatting#d3_format. Defaults to our internal number format

        :return: str
        """
        return self._options.get("y_tick_format")

    @y_tick_format.setter
    def y_tick_format(self, val):
        self._options["y_tick_format"] = val
        self._update()


    @property
    def _num_x_ticks(self):
        """
        Number of x axis tick labels.
        Defaults to as many as fit comfortably without overlap

        :rtype: int
        """
        return self._options.get("num_x_ticks")

    @_num_x_ticks.setter
    def _num_x_ticks(self, val):
        self._options["zero_y_line"] = val
        self._update()


    @property
    def _num_y_ticks(self):
        """
        Number of y axis tick labels.
        Defaults to as many as fit comfortably without overlap

        :rtype: int
        """
        return self._options.get("num_y_ticks")

    @_num_y_ticks.setter
    def _num_y_ticks(self, val):
        self._options["num_y_ticks"] = val
        self._update()


    @property
    def _max_displayed_points(self):
        """
        Maximum number of data points to sample for each component

        :rtype: int
        """
        return self._options.get("number_of_rows")

    @_max_displayed_points.setter
    def _max_displayed_points(self, val):
        self._options["number_of_rows"] = val
        self._update()


    @property
    def guides_type(self):
        """
        The type of value-guides to show when hovering over a point in the graph.
        Valid values are "XY", "YY" or False.
        XY guides will show the x and y values for the point under the cursor.
        YY guides will show the x and y values of each component for the data point closest to the cursor.
        False will turn off value guides.

        :rtype: str
        """
        return self._options.get("guides").get("type")

    @guides_type.setter
    def guides_type(self, val):
        self._options["guides"]["type"] = val
        self._update()

    @property
    def datasource(self):
        """The data source providing data for this component

        :return: data source providing data for this component
        """
        if self._options.get("datasource_id") and hasattr(self, "_eureqa"):
            return self._eureqa.get_data_source_by_id(self._options["datasource_id"])

    @datasource.setter
    def datasource(self, val):
        self._datasource = val
        self._options["datasource_id"] = val._data_source_id
        self._eureqa = val._eureqa
        self._update()


    def upload_data(self, eureqa=None):
        """
        Upload the plot data to eureqa. This is required before the plot can be viewed.

        :param Eureqa eureqa: a eureqa connection
        """
        if eureqa is None:
            eureqa = self._analysis._eureqa

        csv_file = self._data_holder.get_csv_file()
        datasource = eureqa.create_data_source("Data Holder for Plot", csv_file, _hidden=True)
        self.datasource = datasource
        self._options['datasource_id'] = datasource._data_source_id

    @staticmethod
    def _plot_type(style):
        """
        For internal use only.

        Translate a matplotlib-like style string into one of the supported plot types

        :param str style: a matplotlib-like style string
        :return: internal plot type
        :rtype: str
        """
        if '-' in style and 'o' in style: return 'line_circle'
        if 'o' in style: return 'circle'
        if '-' in style: return 'line'
        return None

    def _plot_data(self, x_data, y_data, config):
        """
        For internal use only.

        Given two lists of data (and perhaps variable names to use for those lists), add the data to the plot with the specified options.

        :param list x_list: a list of input values for the x axis
        :param list y_list: a list of input values for the y axis
        :param str x_name: an optional name for the x variable. If unspecified, default is (Series %i X), where i is the plot number
        :param str y_name: an optional name for the y variable. If unspecified, default is (Series %i Y), where i is the plot number
        """
        if (config.get('error_bars_upper_values') is not None and not isinstance(config.get('error_bars_upper_values'), list))\
        or (config.get('error_bars_upper_values') is not None and not isinstance(config.get('error_bars_upper_values'), list)):
            raise Exception("CustomPlot.plot error: since x and y were inputted as lists, error bars must be provided as lists")

        self._options['datasource_id'] = None

        self._var_counter += 1
        x_name = config.get('x_name', '(Series %i %s)' % (self._var_counter, 'X'))
        y_name = config.get('y_name', '(Series %i %s)' % (self._var_counter, 'Y'))
        self._data_holder.add_column(x_name, x_data)
        self._data_holder.add_column(y_name, y_data)

        error_bars_upper_values_name = config.get('error_bars_upper_values_name')
        error_bars_lower_values_name = config.get('error_bars_lower_values_name')
        if config.get('error_bars_upper_values') is not None and config.get('error_bars_lower_values') is not None:
            error_bars_upper_values_name = error_bars_upper_values_name or '(Series %i upper error bars)' % (self._var_counter)
            error_bars_lower_values_name = error_bars_lower_values_name or '(Series %i lower error bars)' % (self._var_counter)
            self._data_holder.add_column(error_bars_upper_values_name, config.get('error_bars_upper_values'))
            self._data_holder.add_column(error_bars_lower_values_name, config.get('error_bars_lower_values'))

        plot_options = {
            'type': CustomPlot._plot_type(config.get('style')),
            'color': config.get('color'),
            'width': config.get('line_width'),
            'radius': config.get('circle_radius'),
            'x_values': x_name,
            'y_values': y_name,
            'use_in_plot_range': config.get('use_in_plot_range'),
            'error_bars_upper_values': error_bars_upper_values_name,
            'error_bars_lower_values': error_bars_lower_values_name,
            'inside_legend': config.get('legend_label') is not None,
            'legend_label': config.get('legend_label'),
            'tooltip_template': config.get('tooltip_template'),
            'tooltips': config.get('tooltips')
        }

        self._options['components'].append(plot_options)

    def _plot_expression(self, x_expr, y_expr, datasource, config):
        """
        For internal use only.

        Given a datasource and two expressions in terms of variables in that datasource, evaluate the expressions and add the data to the plot with the specified options.

        :param list x_expr: an expression for the x axis in terms of the datasource
        :param list y_expr: an expression for the y axis in terms of the datasource
        :param Datasource datasource: a datasource to evaluate the expressions on
        :param config: configuration as dictionary
        """
        if not datasource or not isinstance(datasource, DataSource): raise Exception("CustomPlot.plot error: an existing DataSource object must be provided if x and y are provided as strings referencing variables or expressions")
        if (config.get('error_bars_upper_values') is not None and not isinstance(config.get('error_bars_upper_values'), str))\
        or (config.get('error_bars_upper_values') is not None and not isinstance(config.get('error_bars_upper_values'), str)):
            raise Exception("CustomPlot.plot error: since x and y were inputted as expression strings, error bars must be provided as expression strings")

        x_data, y_data = datasource._eureqa._expression_values(datasource, x_expr, y_expr)
        config['x_name'] = '(Datasource %s: %s)' %(datasource.name, x_expr)
        config['y_name'] = '(Datasource %s: %s)' %(datasource.name, y_expr)
        config['error_bars_upper_values_name'] = None
        config['error_bars_lower_values_name'] = None
        if config.get('error_bars_upper_values') is not None and config.get('error_bars_lower_values') is not None:
            config['error_bars_upper_values_name'] = '(Datasource %s: %s)' %(datasource.name, config.get('error_bars_upper_values'))
            config['error_bars_lower_values_name'] = '(Datasource %s: %s)' %(datasource.name, config.get('error_bars_lower_values'))
            config['error_bars_upper_values'] = datasource._eureqa.evaluate_expression(datasource, config.get('error_bars_upper_values'))[config.get('error_bars_upper_values')]
            config['error_bars_lower_values'] = datasource._eureqa.evaluate_expression(datasource, config.get('error_bars_lower_values'))[config.get('error_bars_lower_values')]
        self._plot_data(x_data, y_data, config)

    def _plot(self, x, y,
             datasource=None,
             style='-',
             color='black',
             line_width=1,
             circle_radius=1,
             use_in_plot_range=True,
             error_bars_upper_values=None,
             error_bars_lower_values=None,
             legend_label=None,
             tooltip_template=None,
             tooltips=None):

        """
        See CustomPlot.plot above for full parameter docs
        """

        config = {
            'style': style,
            'color': color,
            'line_width': line_width,
            'circle_radius': circle_radius,
            'use_in_plot_range': use_in_plot_range,
            'error_bars_upper_values': error_bars_upper_values,
            'error_bars_lower_values': error_bars_lower_values,
            'legend_label': legend_label,
            'tooltip_template': tooltip_template,
            'tooltips': tooltips
        }

        # decide which overload to use
        if isinstance(x, list) and isinstance(y, list):
            return self._plot_data(x, y, config)
        elif isinstance(x, str) and isinstance(y, str):
            return self._plot_expression(x, y, datasource, config)
        else:
            raise Exception("CustomPlot.plot error: x and y inputs must be either lists of numbers or strings referencing a variable or expression")

    def delete(self):
        """
        Delete the Plot and any associated data which has been uploaded.
        """
        super(CustomPlot, self).delete()
        if self.datasource is not None: self.datasource.delete()
