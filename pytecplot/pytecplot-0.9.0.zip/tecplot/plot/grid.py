from builtins import super

from ..constant import *
from .. import session
from ..tecutil import sv


class GridArea(session.Style):
    """Grid area for polar 2D plots.

    .. code-block:: python
        :emphasize-lines: 15-18

        from os import path
        import tecplot as tp
        from tecplot.constant import PlotType, ThetaMode, Color

        examples_dir = tp.session.tecplot_examples_directory()
        datafile = path.join(examples_dir, 'SimpleData', 'IndependentDependent.lpk')
        dataset = tp.load_layout(datafile)

        plot = tp.active_frame().plot(PlotType.PolarLine)
        plot.activate()

        plot.axes.theta_axis.mode = ThetaMode.Radians
        plot.axes.grid_area.fill_color = Color.Creme

        grid_area = plot.axes.grid_area
        grid_area.filled = True
        grid_area.fill_color = Color.SkyBlue
        grid_area.show_border = True

        tp.export.save_png('grid_area_polar.png', 600, supersample=3)

    ..  figure:: /_static/images/grid_area_polar.png
        :width: 300px
        :figwidth: 300px
    """

    def __init__(self, axes):
        self.axes = axes
        super().__init__(axes._sv, sv.GRIDAREA, **axes._style_attrs)

    @property
    def filled(self):
        """Fill the axes area background color.

        :type: `boolean <bool>`

        Example usage::

            >>> from tecplot.constant import Color
            >>> plot.axes.grid_area.filled = True
            >>> plot.axes.grid_area.fill_color = Color.LightGreen
        """
        return self._get_style(bool, sv.ISFILLED)

    @filled.setter
    def filled(self, value):
        self._set_style(bool(value), sv.ISFILLED)

    @property
    def fill_color(self):
        """Axes area background color.

        :type: `Color`

        This requires the ``filled`` attribute to be `True`::

            >>> from tecplot.constant import Color
            >>> plot.axes.grid_area.filled = True
            >>> plot.axes.grid_area.fill_color = Color.LightGreen
        """
        return self._get_style(Color, sv.FILLCOLOR)

    @fill_color.setter
    def fill_color(self, value):
        self._set_style(Color(value), sv.FILLCOLOR)

    @property
    def show_border(self):
        """Draw border around axes area.

        :type: `boolean <bool>`

        Example usage::

            >>> plot.axes.grid_area.show_border = True
        """
        return self._get_style(bool, sv.DRAWBORDER)

    @show_border.setter
    def show_border(self, value):
        self._set_style(bool(value), sv.DRAWBORDER)


class Cartesian2DGridArea(GridArea):
    """Grid area for cartesian 2D plots.

    .. code-block:: python
        :emphasize-lines: 15-18

        from os import path
        import tecplot as tp
        from tecplot.constant import PlotType, Color

        examples_dir = tp.session.tecplot_examples_directory()
        infile = path.join(examples_dir, 'SimpleData', 'SunSpots.plt')
        dataset = tp.data.load_tecplot(infile)

        frame = tp.active_frame()
        plot = frame.plot(PlotType.XYLine)

        plot.linemap(0).line.color = Color.DarkBlue
        plot.linemap(0).line.line_thickness = 1.0

        grid_area = plot.axes.grid_area
        grid_area.filled = True
        grid_area.fill_color = Color.SkyBlue
        grid_area.show_border = True

        tp.export.save_png('grid_area_2d.png', 600, supersample=3)

    ..  figure:: /_static/images/grid_area_2d.png
        :width: 300px
        :figwidth: 300px
    """

    @property
    def border_color(self):
        """Border line color.

        :type: `Color`

        Example usage::

            >>> from tecplot.constant import Color
            >>> plot.axes.grid_area.show_border = True
            >>> plot.axes.grid_area.border_color = Color.LightGreen
        """
        return self._get_style(Color, sv.COLOR)

    @border_color.setter
    def border_color(self, value):
        self._set_style(Color(value), sv.COLOR)

    @property
    def border_thickness(self):
        """Width of the border lines to be drawn.

        :type: `float`

        Example usage::

            >>> plot.axes.grid_area.border_thickness = 0.5
        """
        return self._get_style(float, sv.LINETHICKNESS)

    @border_thickness.setter
    def border_thickness(self, value):
        self._set_style(float(value), sv.LINETHICKNESS)


class Cartesian3DGridArea(GridArea):
    """Grid area for 3D field plots.

    .. code-block:: python
        :emphasize-lines: 21-24

        from os import path
        import tecplot as tp
        from tecplot.constant import PlotType, SurfacesToPlot, Color

        examples_dir = tp.session.tecplot_examples_directory()
        infile = path.join(examples_dir, 'SimpleData', 'Pyramid.plt')
        dataset = tp.data.load_tecplot(infile)

        frame = tp.active_frame()
        plot = frame.plot(PlotType.Cartesian3D)

        for fmap in plot.fieldmaps():
            fmap.contour.show = True
            fmap.surfaces.surfaces_to_plot = SurfacesToPlot.BoundaryFaces
        plot.show_contour = True
        plot.contour(0).legend.show = False

        for axis in plot.axes:
            axis.show = True

        grid_area = plot.axes.grid_area
        grid_area.fill_color = Color.SkyBlue
        grid_area.show_border = True
        grid_area.use_lighting_effect = True

        plot.view.fit()

        tp.export.save_png('grid_area_3d.png', 600, supersample=3)

    ..  figure:: /_static/images/grid_area_3d.png
        :width: 300px
        :figwidth: 300px
    """

    @property
    def use_lighting_effect(self):
        """Enable lighting effect shading on grid area.

        :type: `boolean <bool>`

        Example usage::

            >>> plot.axes.grid_area.use_lighting_effect = True
        """
        return self._get_style(bool, sv.USELIGHTSOURCETOFILL)

    @use_lighting_effect.setter
    def use_lighting_effect(self, value):
        self._set_style(bool(value), sv.USELIGHTSOURCETOFILL)


class PreciseGrid(session.Style):
    """Grid of precise dots aligned with all tick marks.

    .. code-block:: python
        :emphasize-lines: 19-21

        from os import path
        import tecplot as tp
        from tecplot.constant import PlotType, LinePattern, Color

        examples_dir = tp.session.tecplot_examples_directory()
        datafile = path.join(examples_dir, 'SimpleData', 'RainierElevation.plt')
        dataset = tp.data.load_tecplot(datafile)

        plot = tp.active_frame().plot(PlotType.Cartesian2D)
        plot.activate()

        plot.show_contour = True
        plot.contour(0).colormap_name = 'Elevation - Above Ground Level'

        xaxis = plot.axes.x_axis
        plot.axes.preserve_scale = True
        xaxis.max = xaxis.variable.values(0).max()

        grid = plot.axes.precise_grid
        grid.show = True
        grid.size = 0.05

        tp.export.save_png('precise_grid.png', 600, supersample=3)

    ..  figure:: /_static/images/precise_grid.png
        :width: 300px
        :figwidth: 300px
    """
    def __init__(self, axes):
        self.axes = axes
        super().__init__(axes._sv[-1], sv.PRECISEGRID, **axes._style_attrs)

    @property
    def show(self):
        """Draw precise grid dots in axes area.

        :type: `boolean <bool>`

        Example usage::

            >>> plot.axes.precise_grid.show = True
        """
        return self._get_style(bool, sv.INCLUDE)

    @show.setter
    def show(self, value):
        self._set_style(bool(value), sv.INCLUDE)

    @property
    def size(self):
        """Size of the dots for precise grid.

        :type: `float` (cm)

        Example usage::

            >>> plot.axes.precise_grid.size = 0.2
        """
        return self._get_style(float, sv.SIZE)

    @size.setter
    def size(self, value):
        self._set_style(float(value), sv.SIZE)

    @property
    def color(self):
        """Color of the dots for precise grid.

        :type: `Color`

        Example usage::

            >>> plot.axes.precise_grid.color = Color.DarkBlue
        """
        return self._get_style(Color, sv.COLOR)

    @color.setter
    def color(self, value):
        self._set_style(Color(value), sv.COLOR)


class GridLinesStyle(session.Style):
    def __init__(self, axis, *svargs):
        self.axis = axis
        super().__init__(axis._sv, *svargs, **axis._style_attrs)

    @property
    def show(self):
        """Draw grid lines as tick locations.

        :type: `boolean <bool>`

        Example usage::

            >>> grid_lines.show = True
        """
        return self._get_style(bool, sv.SHOW)

    @show.setter
    def show(self, value):
        self._set_style(bool(value), sv.SHOW)

    @property
    def color(self):
        """`Color` of the grid lines to be drawn.

        :type: `Color`

        Example usage::

            >>> from tecplot.constant import Color
            >>> grid_lines.color = Color.Blue
        """
        return self._get_style(Color, sv.COLOR)

    @color.setter
    def color(self, value):
        self._set_style(Color(value), sv.COLOR)

    @property
    def line_thickness(self):
        """Width of the grid lines to be drawn.

        :type: `float`

        Example usage::

            >>> grid_lines.line_thickness = 0.5
        """
        return self._get_style(float, sv.LINETHICKNESS)

    @line_thickness.setter
    def line_thickness(self, value):
        self._set_style(float(value), sv.LINETHICKNESS)

    @property
    def line_pattern(self):
        """Pattern style of the grid lines to be drawn.

        :type: `LinePattern`

        Possible values: `Solid <LinePattern.Solid>`, `Dashed`, `DashDot`,
        `Dotted`, `LongDash`, `DashDotDot`.

        Example usage::

            >>> from tecplot.constant import LinePattern
            >>> grid_lines.line_pattern = LinePattern.LongDash
        """
        return self._get_style(LinePattern, sv.LINEPATTERN)

    @line_pattern.setter
    def line_pattern(self, value):
        self._set_style(LinePattern(value), sv.LINEPATTERN)

    @property
    def pattern_length(self):
        """Segment length of the repeated line pattern.

        :type: `float`

        Example usage::

            >>> from tecplot.constant import LinePattern
            >>> grid_lines.line_pattern = LinePattern.LongDash
            >>> grid_lines.pattern_length = 3.5
        """
        return self._get_style(float, sv.PATTERNLENGTH)

    @pattern_length.setter
    def pattern_length(self, value):
        self._set_style(float(value), sv.PATTERNLENGTH)


class GridLines(GridLinesStyle):
    """Major grid lines.

    .. code-block:: python
        :emphasize-lines: 15-18

        from os import path
        import tecplot as tp
        from tecplot.constant import LinePattern, Color

        examples_dir = tp.session.tecplot_examples_directory()
        datafile = path.join(examples_dir, 'SimpleData', 'Sphere.lpk')
        dataset = tp.load_layout(datafile)

        plot = tp.active_frame().plot()

        plot.axes.grid_area.fill_color = Color.Grey

        for axis in (plot.axes.x_axis, plot.axes.y_axis):
            axis.show = True
            grid_lines = axis.grid_lines
            grid_lines.show = True
            grid_lines.line_pattern = LinePattern.LongDash
            grid_lines.color = Color.Cyan

        plot.view.fit()

        tp.export.save_png('grid_lines.png', 600, supersample=3)

    .. figure:: /_static/images/grid_lines.png
        :width: 300px
        :figwidth: 300px
    """
    def __init__(self, axis):
        GridLinesStyle.__init__(self, axis, sv.GRIDLINES)


class GridLines2D(GridLines):
    """Major grid lines following the primary tick mark locations.

    The lines drawn are determined by the placement of major tick marks along
    the axis.

    .. code-block:: python
        :emphasize-lines: 10-13

        from os import path
        import tecplot as tp
        from tecplot.constant import LinePattern, Color

        examples_dir = tp.session.tecplot_examples_directory()
        datafile = path.join(examples_dir, 'SimpleData', 'IndependentDependent.lpk')
        dataset = tp.load_layout(datafile)

        for axis in tp.active_frame().plot().axes:
            grid_lines = axis.grid_lines
            grid_lines.show = True
            grid_lines.line_pattern = LinePattern.LongDash
            grid_lines.color = Color.Green

        tp.export.save_png('grid_lines_2d.png', 600, supersample=3)

    ..  figure:: /_static/images/grid_lines_2d.png
        :width: 300px
        :figwidth: 300px
    """

    @property
    def draw_last(self):
        """Draw grid behind all other plot elements.

        :type: `boolean <bool>`

        Example usage::

            >>> axis.grid_lines.draw_last = True
        """
        return self._get_style(bool, sv.DRAWGRIDLAST)

    @draw_last.setter
    def draw_last(self, value):
        self._set_style(bool(value), sv.DRAWGRIDLAST)


class MinorGridLines(GridLinesStyle):
    """Minor grid lines.

    .. code-block:: python
        :emphasize-lines: 19-22

        from os import path
        import tecplot as tp
        from tecplot.constant import LinePattern, Color

        examples_dir = tp.session.tecplot_examples_directory()
        datafile = path.join(examples_dir, 'SimpleData', 'Sphere.lpk')
        dataset = tp.load_layout(datafile)

        plot = tp.active_frame().plot()

        plot.axes.grid_area.fill_color = Color.Grey

        for axis in (plot.axes.x_axis, plot.axes.y_axis):
            axis.show = True

            grid_lines = axis.grid_lines
            grid_lines.show = True

            minor_grid_lines = axis.minor_grid_lines
            minor_grid_lines.show = True
            minor_grid_lines.line_pattern = LinePattern.Dotted
            minor_grid_lines.color = Color.Cyan

        plot.view.fit()

        tp.export.save_png('minor_grid_lines.png', 600, supersample=3)

    .. figure:: /_static/images/minor_grid_lines.png
        :width: 300px
        :figwidth: 300px
    """
    def __init__(self, axis):
        GridLinesStyle.__init__(self, axis, sv.MINORGRIDLINES)


class MinorGridLines2D(MinorGridLines, GridLines2D):
    """Minor grid lines following the secondary tick mark locations.

    The lines drawn are determined by the placement of minor tick marks along
    the axis. Example usage::

        from os import path
        import tecplot as tp
        from tecplot.constant import LinePattern, Color

        examples_dir = tp.session.tecplot_examples_directory()
        datafile = path.join(examples_dir, 'SimpleData', 'IndependentDependent.lpk')
        dataset = tp.load_layout(datafile)

        for axis in tp.active_frame().plot().axes:
            grid_lines = axis.grid_lines
            grid_lines.show = True

            minor_grid_lines = axis.minor_grid_lines
            minor_grid_lines.show = True
            minor_grid_lines.line_pattern = LinePattern.Dotted
            minor_grid_lines.color = Color.Green

        tp.export.save_png('minor_grid_lines_2d.png', 600, supersample=3)

    ..  figure:: /_static/images/minor_grid_lines_2d.png
        :width: 300px
        :figwidth: 300px
    """


class PolarAngleGridLines(GridLines2D):
    """Major grid lines along the theta axis.

    The lines drawn are determined by the placement of minor tick marks along
    the axis. Example usage:

    .. code-block:: python
        :emphasize-lines: 17-20

        from os import path
        import tecplot as tp
        from tecplot.constant import PlotType, ThetaMode, LinePattern, Color

        examples_dir = tp.session.tecplot_examples_directory()
        datafile = path.join(examples_dir, 'SimpleData', 'IndependentDependent.lpk')
        dataset = tp.load_layout(datafile)

        plot = tp.active_frame().plot(PlotType.PolarLine)
        plot.activate()

        plot.axes.theta_axis.mode = ThetaMode.Radians
        plot.axes.grid_area.filled = True
        plot.axes.grid_area.fill_color = Color.Creme

        for axis in plot.axes:
            grid_lines = axis.grid_lines
            grid_lines.show = True
            grid_lines.line_pattern = LinePattern.LongDash
            grid_lines.color = Color.Green

        for lmap in plot.linemaps():
            lmap.show_in_legend = False
            lmap.line.line_pattern = LinePattern.Solid
            lmap.line.line_thickness = 0.8

        tp.export.save_png('grid_lines_polar.png', 600, supersample=3)

    ..  figure:: /_static/images/grid_lines_polar.png
        :width: 300px
        :figwidth: 300px
    """

    @property
    def radial_cutoff(self):
        """Minimum radial position of theta grid lines.

        :type: `float` in percent along r-axis.

        Example usage::

            >>> plot.axes.theta_axis.grid_lines.radial_cutoff = 5
        """
        return self._get_style(float, sv.CUTOFF)

    @radial_cutoff.setter
    def radial_cutoff(self, value):
        self._set_style(float(value), sv.CUTOFF)


class PolarAngleMinorGridLines(MinorGridLines2D, PolarAngleGridLines):
    """Minor grid lines along the theta axis.

    The lines drawn are determined by the placement of minor tick marks along
    the axis. Example usage:

    .. code-block:: python
        :emphasize-lines: 20-23

        from os import path
        import tecplot as tp
        from tecplot.constant import PlotType, ThetaMode, LinePattern, Color

        examples_dir = tp.session.tecplot_examples_directory()
        datafile = path.join(examples_dir, 'SimpleData', 'IndependentDependent.lpk')
        dataset = tp.load_layout(datafile)

        plot = tp.active_frame().plot(PlotType.PolarLine)
        plot.activate()

        plot.axes.theta_axis.mode = ThetaMode.Radians
        plot.axes.grid_area.filled = True
        plot.axes.grid_area.fill_color = Color.Creme

        for axis in plot.axes:
            grid_lines = axis.grid_lines
            grid_lines.show = True

            minor_grid_lines = axis.minor_grid_lines
            minor_grid_lines.show = True
            minor_grid_lines.line_pattern = LinePattern.Dotted
            minor_grid_lines.color = Color.Green

        for lmap in plot.linemaps():
            lmap.show_in_legend = False
            lmap.line.line_pattern = LinePattern.Solid
            lmap.line.line_thickness = 0.8

        tp.export.save_png('minor_grid_lines_polar.png', 600, supersample=3)

    ..  figure:: /_static/images/minor_grid_lines_polar.png
        :width: 300px
        :figwidth: 300px
    """
    def __init__(self, axis):
        GridLinesStyle.__init__(self, axis, sv.MINORGRIDLINES)


class MarkerGridLine(GridLinesStyle):
    """Marker line to indicate a particular position along an axis.

    .. code-block:: python
        :emphasize-lines: 17-21,23-27

        from os import path
        import tecplot as tp
        from tecplot.constant import PlotType, Color, PositionMarkerBy

        examples_dir = tp.session.tecplot_examples_directory()
        datafile = path.join(examples_dir, 'SimpleData', 'Sphere.lpk')
        dataset = tp.load_layout(datafile)

        plot = tp.active_frame().plot(PlotType.Cartesian3D)
        plot.activate()

        plot.axes.grid_area.fill_color = Color.Grey

        plot.axes.x_axis.show = True
        plot.axes.y_axis.show = True

        marker = plot.axes.x_axis.marker_grid_line
        marker.show = True
        marker.position_by = PositionMarkerBy.Constant
        marker.position = 1.5
        marker.color = Color.Cyan

        marker = plot.axes.y_axis.marker_grid_line
        marker.show = True
        marker.position_by = PositionMarkerBy.Constant
        marker.position = 0.5
        marker.color = Color.Yellow

        plot.view.fit()

        tp.export.save_png('marker_grid_line.png', 600, supersample=3)

    .. figure:: /_static/images/marker_grid_line.png
        :width: 300px
        :figwidth: 300px
    """
    def __init__(self, axis):
        GridLinesStyle.__init__(self, axis, sv.MARKERGRIDLINE)

    @property
    def position_by(self):
        """Position of the marker line in axes coordinates.

        :type: `PositionMarkerBy`

        Possible values: `PositionMarkerBy.Constant` or
            `PositionMarkerBy.SolutionTime`.

        The position can be set to a constant or to the solution time of the
        linked frame::

            >>> from tecplot.constant import PositionMarkerBy
            >>> marker_line = plot.axes.x_axis.marker_grid_line
            >>> marker_line.position_by = PositionMarkerBy.SolutionTime
        """
        return self._get_style(PositionMarkerBy, sv.POSITIONMARKERBY)

    @position_by.setter
    def position_by(self, value):
        self._set_style(PositionMarkerBy(value), sv.POSITIONMARKERBY)

    @property
    def position(self):
        """Position of the marker line in axes coordinates.

        :type: `float`

        The ``position_by`` attribute must be set to
        `PositionMarkerBy.Constant`::

            >>> from tecplot.constant import PositionMarkerBy
            >>> marker_line = plot.axes.x_axis.marker_grid_line
            >>> marker_line.position_by = PositionMarkerBy.Constant
            >>> marker_line.position = 3.14
        """
        return self._get_style(float, sv.CONSTANTVALUE)

    @position.setter
    def position(self, value):
        self._set_style(float(value), sv.CONSTANTVALUE)


class MarkerGridLine2D(MarkerGridLine, GridLines2D):
    """Marker line to indicate a particular position along an axis.

    .. code-block:: python
        :emphasize-lines: 12-16,18-22

        from os import path
        import tecplot as tp
        from tecplot.constant import PlotType, Color, PositionMarkerBy

        examples_dir = tp.session.tecplot_examples_directory()
        datafile = path.join(examples_dir, 'SimpleData', 'IndependentDependent.lpk')
        dataset = tp.load_layout(datafile)

        plot = tp.active_frame().plot(PlotType.XYLine)
        plot.activate()

        marker = plot.axes.x_axis(0).marker_grid_line
        marker.show = True
        marker.position_by = PositionMarkerBy.Constant
        marker.position = -0.4
        marker.color = Color.Blue

        marker = plot.axes.y_axis(0).marker_grid_line
        marker.show = True
        marker.position_by = PositionMarkerBy.Constant
        marker.position = -0.88
        marker.color = Color.Blue

        tp.export.save_png('marker_grid_line_2d.png', 600, supersample=3)

    ..  figure:: /_static/images/marker_grid_line_2d.png
        :width: 300px
        :figwidth: 300px
    """

class PolarAngleMarkerGridLine(MarkerGridLine2D, PolarAngleGridLines):
    """The marker grid line for the theta axis."""
