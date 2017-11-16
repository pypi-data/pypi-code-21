from ..exception import *
from ..text import TextBox
from ..tecutil import sv
from .legend import Legend, LegendFont


class LineLegend(Legend):
    """Line plot legend attributes.

    The XY line legend shows the line and symbol attributes of XY mappings. In
    `XY line plots <XYLinePlot>`, this legend includes the bar chart
    information. The legend can be positioned anywhere within the line plot
    frame by setting the `position` attribute. By default, all mappings are
    shown, but |Tecplot 360| removes redundant entries.

    .. code-block:: python
        :emphasize-lines: 23-38

        import os

        import tecplot
        from tecplot.constant import *

        examples_dir = tecplot.session.tecplot_examples_directory()
        datafile = os.path.join(examples_dir, 'SimpleData', 'Rainfall.dat')
        dataset = tecplot.data.load_tecplot(datafile)

        frame = tecplot.active_frame()
        plot = frame.plot()
        frame.plot_type = tecplot.constant.PlotType.XYLine

        for i in range(3):
            plot.linemap(i).show = True
            plot.linemap(i).line.line_thickness = .4

        y_axis = plot.axes.y_axis(0)
        y_axis.title.title_mode = AxisTitleMode.UseText
        y_axis.title.text = 'Rainfall (in)'
        y_axis.fit_range_to_nice()

        legend = plot.legend
        legend.show = True
        legend.box.box_type = TextBox.Filled
        legend.box.color = Color.Purple
        legend.box.fill_color = Color.LightGrey
        legend.box.line_thickness = .4
        legend.box.margin = 5

        legend.anchor_alignment = AnchorAlignment.MiddleRight
        legend.row_spacing = 1.5
        legend.show_text = True
        legend.font.typeface = 'Arial'
        legend.font.italic = True

        legend.text_color = Color.Black
        legend.position = (90, 88)

        tecplot.export.save_png('legend_line.png', 600, supersample=3)

    .. figure:: /_static/images/legend_line.png
        :width: 300px
        :figwidth: 300px
    """
    def __init__(self, plot, *svargs):
        self.plot = plot
        super().__init__(sv.GLOBALLINEPLOT, sv.LEGEND, **plot._style_attrs)

    @property
    def show_text(self):
        """Show/hide mapping names in the legend.

        :type: `boolean <bool>`

        Example usage::

            >>> from tecplot.constant import PlotType
            >>> plot = frame.plot(PlotType.XYLine)
            >>> plot.legend.show_text = True
        """
        return self._get_style(bool, sv.SHOWTEXT)

    @show_text.setter
    def show_text(self, value):
        self._set_style(bool(value), sv.SHOWTEXT)

    @property
    def font(self):
        """Legend font attributes.

        .. note::
            The font `size_units <tecplot.text.Font.size_units>` property
            may only be set to `Units.Frame` or `Units.Point`.

        :type: `text.Font`

        Example usage::

            >>> from tecplot.constant import PlotType
            >>> plot = frame.plot(PlotType.XYLine)
            >>> plot.legend.font.italic = True
        """
        return LegendFont(self)

    @property
    def box(self):
        """Legend box attributes.

        :type: `text.TextBox`

        Example usage::

            >>> from tecplot.constant import PlotType, Color
            >>> plot = frame.plot(PlotType.XYLine)
            >>> plot.legend.box.color = Color.Blue
        """
        return TextBox(self)
