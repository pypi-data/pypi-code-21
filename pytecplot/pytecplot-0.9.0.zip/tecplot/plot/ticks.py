from builtins import int

from ..tecutil import _tecutil
from ..constant import *
from ..exception import *
from .. import session
from ..tecutil import Index, StringList, flatten_args, lock, sv
from ..text import Font, LabelFormat


class Ticks(session.Style):
    def __init__(self, axis):
        self.axis = axis
        super().__init__(axis._sv, sv.TICKS, **axis._style_attrs)

    @property
    def show(self):
        """Draw ticks along axis.

        :type: `boolean <bool>`

        Example usage::

            >>> axis.ticks.show = True
        """
        return self._get_style(bool, sv.SHOWONAXISLINE)

    @show.setter
    def show(self, value):
        self._set_style(bool(value), sv.SHOWONAXISLINE)

    @property
    def direction(self):
        """How to draw the ticks with respect the axis line.

        :type: `TickDirection`

        Possible values: `TickDirection.In`, `TickDirection.Out` or
        `TickDirection.Centered`::

            >>> from tecplot.constant import TickDirection
            >>> axis.ticks.direction = TickDirection.Centered
        """
        return self._get_style(TickDirection, sv.TICKDIRECTION)

    @direction.setter
    def direction(self, value):
        self._set_style(TickDirection(value), sv.TICKDIRECTION)

    @property
    def length(self):
        """Size of the major tick lines to draw.

        :type: `float` (percent of frame height)

        Example usage::

            >>> axis.ticks.length = 2
        """
        return self._get_style(float, sv.LENGTH)

    @length.setter
    def length(self, value):
        self._set_style(float(value), sv.LENGTH)

    @property
    def line_thickness(self):
        """Width of the major tick lines to be drawn.

        :type: `float`

        Example usage::

            >>> axis.ticks.line_thickness = 0.4
        """
        return self._get_style(float, sv.LINETHICKNESS)

    @line_thickness.setter
    def line_thickness(self, value):
        self._set_style(float(value), sv.LINETHICKNESS)

    @property
    def minor_num_ticks(self):
        """Number of minor ticks between each major tick.

        :type: `int`

        Example usage::

            >>> axis.ticks.minor_num_ticks = 3
        """
        return self._get_style(int, sv.NUMMINORTICKS)

    @minor_num_ticks.setter
    def minor_num_ticks(self, value):
        self._set_style(int(value), sv.NUMMINORTICKS)

    @property
    def minor_length(self):
        """Size of the minor tick lines to draw.

        :type: `float` (percent of frame height)

        Example usage::

            >>> axis.ticks.minor_length = 1.2
        """
        return self._get_style(float, sv.MINORLENGTH)

    @minor_length.setter
    def minor_length(self, value):
        self._set_style(float(value), sv.MINORLENGTH)

    @property
    def minor_line_thickness(self):
        """Width of the minor tick lines to be drawn.

        :type: `float`

        Example usage::

            >>> axis.ticks.minor_line_thickness = 0.1
        """
        return self._get_style(float, sv.MINORLINETHICKNESS)

    @minor_line_thickness.setter
    def minor_line_thickness(self, value):
        self._set_style(float(value), sv.MINORLINETHICKNESS)

    @property
    def auto_spacing(self):
        """Automatically set the spacing between tick marks.

        :type: `boolean <bool>`

        Example usage::

            >>> axis.ticks.auto_spacing = True
        """
        return self.axis._get_style(bool, sv.AUTOGRID)

    @auto_spacing.setter
    def auto_spacing(self, value):
        self.axis._set_style(bool(value), sv.AUTOGRID)

    @property
    def spacing(self):
        """Distance between major ticks.

        :type: `float` (axis data units)

        The ``auto_spacing`` attribute must be set to `False`::

            >>> axis.ticks.auto_spacing = False
            >>> axis.ticks.spacing = 0.2
        """
        return self.axis._get_style(float, sv.GRSPACING)

    @spacing.setter
    def spacing(self, value):
        self.axis._set_style(float(value), sv.GRSPACING)

    @property
    def spacing_anchor(self):
        """Value to place the first major tick mark.

        :type: `float`

        All ticks will placed around this anchor position::

            >>> axis.ticks.spacing_anchor = 0.05
        """
        return self.axis._get_style(float, sv.GRANCHOR)

    @spacing_anchor.setter
    def spacing_anchor(self, value):
        self.axis._set_style(float(value), sv.GRANCHOR)


class Ticks2D(Ticks):
    """Tick marks (major and minor) along axes in 2D.

    .. code-block:: python
        :emphasize-lines: 25-26,29-33

        import tecplot as tp
        from os import path
        from tecplot.constant import PlotType, AxisMode, AxisAlignment, TickDirection

        examples_dir = tp.session.tecplot_examples_directory()
        infile = path.join(examples_dir, 'SimpleData', 'CircularContour.plt')
        dataset = tp.data.load_tecplot(infile)

        frame = tp.active_frame()
        plot = frame.plot(PlotType.Cartesian2D)

        plot.show_contour = True
        plot.contour(0).colormap_name = 'Sequential - Yellow/Green/Blue'

        plot.axes.x_axis.line.show = False

        yaxis = plot.axes.y_axis
        yaxis.max = 0.15
        yaxis.line.show = False
        yaxis.line.alignment = AxisAlignment.WithOpposingAxisValue
        yaxis.line.opposing_axis_value = 0
        yaxis.tick_labels.transparent_background = True
        yaxis.tick_labels.offset = -5

        yticks = yaxis.ticks
        yticks.direction = TickDirection.Centered

        for ticks in [plot.axes.x_axis.ticks, yticks]:
            ticks.auto_spacing = False
            ticks.spacing = 0.5
            ticks.minor_num_ticks = 3
            ticks.length *= 3
            ticks.line_thickness *= 2

        plot.view.fit()
        tp.export.save_png('ticks_2d.png', 600, supersample=3)

    ..  figure:: /_static/images/ticks_2d.png
        :width: 300px
        :figwidth: 300px
    """

    @property
    def show_on_border_min(self):
        """Draw ticks along the lower border of the axes grid.

        :type: `boolean <bool>`

        Example usage::

            >>> axis.ticks.show_on_border_min = True
        """
        return self._get_style(bool, sv.SHOWONGRIDBORDERMIN)

    @show_on_border_min.setter
    def show_on_border_min(self, value):
        self._set_style(bool(value), sv.SHOWONGRIDBORDERMIN)

    @property
    def show_on_border_max(self):
        """Draw ticks along the upper border of the axes grid.

        :type: `boolean <bool>`

        Example usage::

            >>> axis.ticks.show_on_border_max = True
        """
        return self._get_style(bool, sv.SHOWONGRIDBORDERMAX)

    @show_on_border_max.setter
    def show_on_border_max(self, value):
        self._set_style(bool(value), sv.SHOWONGRIDBORDERMAX)


class RadialTicks(Ticks2D):
    """Tick marks (major and minor) along the radial axis.

    .. code-block:: python
        :emphasize-lines: 18-21

        from os import path
        import tecplot as tp
        from tecplot.constant import PlotType, ThetaMode, Color, TickDirection

        examples_dir = tp.session.tecplot_examples_directory()
        datafile = path.join(examples_dir, 'SimpleData', 'IndependentDependent.lpk')
        dataset = tp.load_layout(datafile)

        plot = tp.active_frame().plot(PlotType.PolarLine)
        plot.activate()

        plot.axes.theta_axis.mode = ThetaMode.Radians

        raxis = plot.axes.r_axis
        raxis.line.color = Color.Red
        raxis.tick_labels.offset = -4

        raxis.ticks.direction =TickDirection.Centered
        raxis.ticks.line_thickness = 0.8
        raxis.ticks.length = 4
        raxis.ticks.minor_length = 4

        tp.export.save_png('ticks_radial.png', 600, supersample=3)

    ..  figure:: /_static/images/ticks_radial.png
        :width: 300px
        :figwidth: 300px
    """

    @property
    def show_on_all_radial_axes(self):
        """Draw ticks along all radial axis lines.

        :type: `boolean <bool>`

        Example usage::

            >>> plot.axes.r_axis.line.show_perpendicular = True
            >>> plot.axes.r_axis.ticks.show_on_all_radial_axes = True
        """
        return self._get_style(bool, sv.SHOWONALLAXES)

    @show_on_all_radial_axes.setter
    def show_on_all_radial_axes(self, value):
        self._set_style(bool(value), sv.SHOWONALLAXES)


class Ticks3D(Ticks):
    """Tick marks (major and minor) along axes in 3D.

    .. code-block:: python
        :emphasize-lines: 21-22

        from os import path
        import tecplot as tp
        from tecplot.constant import PlotType, TickDirection

        examples_dir = tp.session.tecplot_examples_directory()
        infile = path.join(examples_dir, 'SimpleData', 'F18.plt')
        dataset = tp.data.load_tecplot(infile)

        frame = tp.active_frame()
        plot = frame.plot(PlotType.Cartesian3D)
        plot.activate()

        plot.show_contour = True
        plot.contour(0).legend.show = False
        plot.axes.grid_area.filled = False

        for axis in plot.axes:
            axis.show = True
            axis.grid_lines.show = False

            axis.ticks.length *= 4
            axis.ticks.minor_length *= 4

        plot.view.fit()

        tp.export.save_png('ticks_3d.png', 600, supersample=3)

    ..  figure:: /_static/images/ticks_3d.png
        :width: 300px
        :figwidth: 300px
    """

    @property
    def show_on_opposite_edge(self):
        """Draw ticks along the opposite border of the axes grid.

        :type: `boolean <bool>`

        Example usage::

            >>> axis.ticks.show_on_opposite_edge = True
        """
        return self._get_style(bool, sv.SHOWONOPPOSITEEDGE)

    @show_on_opposite_edge.setter
    def show_on_opposite_edge(self, value):
        self._set_style(bool(value), sv.SHOWONOPPOSITEEDGE)


class TickLabels(session.Style):
    def __init__(self, axis):
        self.axis = axis
        super().__init__(axis._sv, sv.TICKLABEL, **axis._style_attrs)

    @property
    def show(self):
        """Draw labels for the major tick marks.

        :type: `boolean <bool>`

        Example usage::

            >>> axis.tick_labels.show = True
        """
        return self._get_style(bool, sv.SHOWONAXISLINE)

    @show.setter
    def show(self, value):
        self._set_style(bool(value), sv.SHOWONAXISLINE)

    @property
    def alignment(self):
        """Angle at which to render the label text.

        :type: `float` (degrees) or `LabelAlignment`

        Possible values: `LabelAlignment.ByAngle`, `LabelAlignment.AlongAxis`
        or `LabelAlignment.PerpendicularToAxis`.

        Example usage::

            >>> from tecplot.constant import LabelAlignment
            >>> axis.tick_labels.alignment = LabelAlignment.AlongAxis
        """
        return self._get_style(LabelAlignment, sv.LABELALIGNMENT)

    @alignment.setter
    def alignment(self, value):
        self._set_style(LabelAlignment(value), sv.LABELALIGNMENT)

    @property
    def angle(self):
        """Angle at which to render the label text.

        :type: `float` (degrees)

        The ``alignment`` attribute must be set to `LabelAlignment.ByAngle`::

            >>> from tecplot.constant import LabelAlignment
            >>> axis.tick_labels.alignment = LabelAlignment.ByAngle
            >>> axis.tick_labels.angle = 30
        """
        return self._get_style(float, sv.ANGLE)

    @angle.setter
    def angle(self, value):
        self._set_style(float(value), sv.ANGLE)

    @property
    def color(self):
        """Color of the tick labels.

        :type: `Color`

        Example usage::

            >>> from tecplot.constant import Color
            >>> axis.tick_labels.color = Color.Blue
        """
        return self._get_style(Color, sv.COLOR)

    @color.setter
    def color(self, value):
        self._set_style(Color(value), sv.COLOR)

    @property
    def offset(self):
        """Relative offset of the tick labels.

        :type: `float`

        Positive values will be outside the grid area, negative values are
        inside the grid area::

            >>> axis.tick_labels.offset = 5
        """
        return self._get_style(float, sv.OFFSET)

    @offset.setter
    def offset(self, value):
        self._set_style(float(value), sv.OFFSET)

    @property
    def step(self):
        """Step for labels placed on major ticks.

        :type: `int`

        A value of 1 will place a label on every major tick mark::

            >>> axis.tick_labels.step = 1
        """
        return self._get_style(int, sv.SKIP)

    @step.setter
    def step(self, value):
        self._set_style(int(value), sv.SKIP)

    @property
    def format(self):
        """Label format and style control.

        :type: `LabelFormat`

        Example usage::

            >>> axis.tick_labels.format.format_type = NumberFormat.BestFloat
        """
        return LabelFormat(self)

    @property
    def font(self):
        """Text style control including typeface and size.

        :type: `text.Font`

        Example usage::

            >>> axis.tick_labels.font.typeface = 'Times'
        """
        return Font(self)


class TickLabels2D(TickLabels):
    """Tick labels along axes in 2D.

    .. code-block:: python

        from datetime import datetime
        import tecplot as tp
        from tecplot.constant import (PlotType, AxisMode, AxisAlignment, NumberFormat,
                                      Color)

        # tecplot dates are in days after Midnight, Dec 30, 1899
        origin = datetime(1899, 12, 30)
        start = (datetime(1955, 11,  5) - origin).days
        stop  = (datetime(1985, 10, 26) - origin).days

        tp.new_layout()
        plot = tp.active_frame().plot(tp.constant.PlotType.Sketch)
        plot.activate()

        plot.axes.viewport.left = 15
        plot.axes.viewport.right = 95

        xaxis = plot.axes.x_axis
        xaxis.show = True
        xaxis.min, xaxis.max = start, stop
        xaxis.line.alignment = AxisAlignment.WithViewport
        xaxis.line.position = 50
        xaxis.ticks.auto_spacing = False
        xaxis.ticks.spacing = (stop - start) // 4
        xaxis.ticks.spacing_anchor = start

        xaxis.tick_labels.format.format_type = NumberFormat.TimeDate
        xaxis.tick_labels.format.datetime_format = 'mmm d, yyyy'
        xaxis.tick_labels.color = Color.Blue
        xaxis.tick_labels.angle = 45

        tp.export.save_png('tick_labels_2d.png', 600, supersample=3)

    ..  figure:: /_static/images/tick_labels_2d.png
        :width: 300px
        :figwidth: 300px
    """

    @property
    def show_on_border_max(self):
        """Draw labels along the upper grid area border.

        :type: `bool`

        Example usage::

            >>> axis.tick_labels.show_on_border_max = True
        """
        return self._get_style(bool, sv.SHOWONGRIDBORDERMAX)

    @show_on_border_max.setter
    def show_on_border_max(self, value):
        self._set_style(bool(value), sv.SHOWONGRIDBORDERMAX)

    @property
    def show_on_border_min(self):
        """Draw labels along the lower grid area border.

        :type: `bool`

        Example usage::

            >>> axis.tick_labels.show_on_border_min = True
        """
        return self._get_style(bool, sv.SHOWONGRIDBORDERMIN)

    @show_on_border_min.setter
    def show_on_border_min(self, value):
        self._set_style(bool(value), sv.SHOWONGRIDBORDERMIN)

    @property
    def show_at_axis_intersection(self):
        """Include the labels at the intersection of other axes.

        :type: `bool`

        Example usage::

            >>> axis.tick_labels.show_at_axis_intersection = True
        """
        return self._get_style(bool, sv.SHOWATAXISINTERSECTION)

    @show_at_axis_intersection.setter
    def show_at_axis_intersection(self, value):
        self._set_style(bool(value), sv.SHOWATAXISINTERSECTION)

    @property
    def transparent_background(self):
        """Make the text box around each label transparent.

        :type: `bool`

        Example usage::

            >>> axis.tick_labels.transparent_background = True
        """
        return not self._get_style(bool, sv.ERASEBEHINDLABELS)

    @transparent_background.setter
    def transparent_background(self, value):
        self._set_style(not bool(value), sv.ERASEBEHINDLABELS)


class RadialTickLabels(TickLabels2D):
    """Tick mark labels along the radial axis.

    .. code-block:: python
        :emphasize-lines: 16-18

        from os import path
        import tecplot as tp
        from tecplot.constant import PlotType, ThetaMode, Color

        examples_dir = tp.session.tecplot_examples_directory()
        datafile = path.join(examples_dir, 'SimpleData', 'IndependentDependent.lpk')
        dataset = tp.load_layout(datafile)

        plot = tp.active_frame().plot(PlotType.PolarLine)
        plot.activate()

        plot.axes.theta_axis.mode = ThetaMode.Radians

        raxis = plot.axes.r_axis
        raxis.line.color = Color.Red
        raxis.tick_labels.offset = -4
        raxis.tick_labels.color = Color.Red
        raxis.tick_labels.font.bold = True

        tp.export.save_png('tick_labels_radial.png', 600, supersample=3)

    ..  figure:: /_static/images/tick_labels_radial.png
        :width: 300px
        :figwidth: 300px
    """

    @property
    def show_on_all_radial_axes(self):
        """Draw labels along all radial axis lines.

        :type: `boolean <bool>`

        Example usage::

            >>> plot.axes.r_axis.line.show_perpendicular = True
            >>> plot.axes.r_axis.tick_labels.show_on_all_radial_axes = True
        """
        return self._get_style(bool, sv.SHOWONALLAXES)

    @show_on_all_radial_axes.setter
    def show_on_all_radial_axes(self, value):
        self._set_style(bool(value), sv.SHOWONALLAXES)


class TickLabels3D(TickLabels):
    """Tick labels along axes in 3D.

    .. code-block:: python
        :emphasize-lines: 23-27

        from os import path
        import tecplot as tp
        from tecplot.constant import PlotType, Color

        examples_dir = tp.session.tecplot_examples_directory()
        infile = path.join(examples_dir, 'SimpleData', 'F18.plt')
        dataset = tp.data.load_tecplot(infile)

        frame = tp.active_frame()
        plot = frame.plot(PlotType.Cartesian3D)
        plot.activate()

        plot.show_contour = True
        plot.contour(0).legend.show = False

        for ax in [plot.axes.x_axis, plot.axes.y_axis]:
            xaxis = plot.axes.x_axis
            ax.show = True
            ax.title.show = False
            ax.line.show_on_opposite_edge = True
            ax.ticks.show_on_opposite_edge = True

            ax.tick_labels.color = Color.Blue
            ax.tick_labels.show_on_opposite_edge = True
            ax.tick_labels.font.typeface = 'Times'
            ax.tick_labels.font.size = 8
            ax.tick_labels.font.italic = True

        plot.view.fit()

        tp.export.save_png('tick_labels_3d.png', 600, supersample=3)

    ..  figure:: /_static/images/tick_labels_3d.png
        :width: 300px
        :figwidth: 300px
    """

    @property
    def show_on_opposite_edge(self):
        """Draw labels on the opposite edge of the grid.

        :type: `boolean <bool>`

        Example usage::

            >>> axis.tick_labels.show_on_opposite_edge = True
        """
        return self._get_style(bool, sv.SHOWONOPPOSITEEDGE)

    @show_on_opposite_edge.setter
    def show_on_opposite_edge(self, value):
        self._set_style(bool(value), sv.SHOWONOPPOSITEEDGE)
