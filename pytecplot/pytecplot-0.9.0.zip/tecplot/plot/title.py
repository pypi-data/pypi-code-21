from .. import session
from ..constant import *
from ..exception import *
from ..tecutil import sv
from .. import text


class AxisTitle(session.Style):
    def __init__(self, axis):
        self.axis = axis
        super().__init__(axis._sv, sv.TITLE, **axis._style_attrs)

    @property
    def text(self):
        """The text of the title for this axis.

        :type: `string <str>`

        Example usage::

            >>> axis.title.text = 'distance (m)'
        """
        return self._get_style(str, sv.TEXT)

    @text.setter
    def text(self, value):
        self._set_style(str(value), sv.TEXT)

    @property
    def show(self):
        """Place title along the axis.

        :type: `boolean <bool>`

        Example usage::

            >>> axis.title.show = False
        """
        return self._get_style(bool, sv.SHOWONAXISLINE)

    @show.setter
    def show(self, show):
        self._set_style(bool(show), sv.SHOWONAXISLINE)

    @property
    def position(self):
        """Percent along axis line to place title.

        :type: `float`

        Example usage::

            >>> axis.title.position = 50
        """
        return self._get_style(float, sv.PERCENTALONGLINE)

    @position.setter
    def position(self, value):
        self._set_style(float(value), sv.PERCENTALONGLINE)

    @property
    def color(self):
        """Text color of axis title.

        :type: `Color`

        Example usage::

            >>> from tecplot.constant import Color
            >>> axis.title.color = Color.Blue
        """
        return self._get_style(Color, sv.COLOR)

    @color.setter
    def color(self, value):
        self._set_style(Color(value), sv.COLOR)

    @property
    def offset(self):
        """Transverse offset of the title from the axis.

        :type: `float` in percent of frame height.

        Positive values are outside the axes, negative numbers
        are inside the axes. Example usage::

            >>> axis.title.offset = 5
        """
        return self._get_style(float, sv.OFFSET)

    @offset.setter
    def offset(self, value):
        self._set_style(float(value), sv.OFFSET)

    @property
    def font(self):
        """Typeface and size of the text.

        :type: `text.Font`

        Example usage::

            >>> axis.title.font.size = 5
        """
        return text.Font(self)


class Axis2DTitle(AxisTitle):
    """Sketch plot axis label string, font and style control.

    .. code-block:: python
        :emphasize-lines: 1

        import tecplot as tp
        from tecplot.constant import PlotType, Color

        plot = tp.active_frame().plot(PlotType.Sketch)

        viewport = plot.axes.viewport
        viewport.left = 10
        viewport.right = 90
        viewport.bottom = 10

        xaxis = plot.axes.x_axis
        xaxis.show = True
        xaxis.title.text = 'distance (m)'
        xaxis.title.color = Color.DarkTurquoise
        xaxis.title.offset = -7

        tp.export.save_png('axis_title_sketch.png', 600, supersample=3)

    ..  figure:: /_static/images/axis_title_sketch.png
        :width: 300px
        :figwidth: 300px
    """
    @property
    def show_on_border_min(self):
        """Draw title along the lower grid area border.

        :type: `bool`

        Example usage::

            >>> axis.title.show_on_border_min = True
        """
        return self._get_style(bool, sv.SHOWONGRIDBORDERMIN)

    @show_on_border_min.setter
    def show_on_border_min(self, value):
        self._set_style(bool(value), sv.SHOWONGRIDBORDERMIN)

    @property
    def show_on_border_max(self):
        """Draw title along the upper grid area border.

        :type: `bool`

        Example usage::

            >>> axis.title.show_on_border_max = True
        """
        return self._get_style(bool, sv.SHOWONGRIDBORDERMAX)

    @show_on_border_max.setter
    def show_on_border_max(self, value):
        self._set_style(bool(value), sv.SHOWONGRIDBORDERMAX)


class Axis3DTitle(AxisTitle):
    @property
    def show_on_opposite_edge(self):
        """Draw the title on the opposite edge of the grid.

        :type: `boolean <bool>`

        Example usage::

            >>> axis.title.show_on_opposite_edge = True
        """
        return self._get_style(bool, sv.SHOWONOPPOSITEEDGE)

    @show_on_opposite_edge.setter
    def show_on_opposite_edge(self, value):
        self._set_style(bool(value), sv.SHOWONOPPOSITEEDGE)


class DataAxisTitle(AxisTitle):
    @property
    def title_mode(self):
        """Define the source for the axis title.

        :type: `AxisTitleMode`

        Possible values: `AxisTitleMode.UseText` or `AxisTitleMode.UseVarName`.

        Example usage::

            >>> from tecplot.constant import AxisTitleMode
            >>> axis.title.title_mode = AxisTitleMode.UseVarName
        """
        return self._get_style(AxisTitleMode, sv.TITLEMODE)

    @title_mode.setter
    def title_mode(self, value):
        value = AxisTitleMode(value)
        if __debug__:
            if value not in [AxisTitleMode.UseText, AxisTitleMode.UseVarName]:
                msg = dedent('''\
                    title_mode must be one of: AxisTitleMode.UseText,
                    AxisTitleMode.UseVarName.''')
                raise TecplotLogicError(msg)
        self._set_style(value, sv.TITLEMODE)

    @property
    def text(self):
        """The text of the title for this axis.

        :type: `string <str>`

        The ``title_mode`` attribute must be set to `AxisTitleMode.UseText`::

            >>> from tecplot.constant import AxisTitleMode
            >>> axis.title.title_mode = AxisTitleMode.UseText
            >>> axis.title.text = 'distance (m)'
        """
        return self._get_style(str, sv.TEXT)

    @text.setter
    def text(self, value):
        self._set_style(str(value), sv.TEXT)


class DataAxis2DTitle(DataAxisTitle, Axis2DTitle):
    """Axis label string, font and style control for 2D data plots.

    .. code-block:: python
        :emphasize-lines: 20-22,25,28-30,33

        from os import path
        import tecplot as tp
        from tecplot.constant import PlotType, SurfacesToPlot, Color, AxisTitleMode

        examples_dir = tp.session.tecplot_examples_directory()
        infile = path.join(examples_dir, 'SimpleData', 'F18.plt')
        dataset = tp.data.load_tecplot(infile)

        plot = tp.active_frame().plot(PlotType.Cartesian2D)
        plot.activate()

        plot.show_contour = True
        plot.contour(0).variable = dataset.variable('S')
        plot.contour(0).colormap_name = 'Sequential - Yellow/Green/Blue'
        plot.contour(0).legend.show = False

        plot.fieldmap(0).surfaces.surfaces_to_plot = SurfacesToPlot.BoundaryFaces

        xaxis = plot.axes.x_axis
        xaxis.title.title_mode = AxisTitleMode.UseText
        xaxis.title.text = 'Longitudinal (m)'
        xaxis.title.color = Color.Blue

        # place the x-axis title at the x-coordinate 10.0
        xaxis.title.position = 100 * (10.0 - xaxis.min) / (xaxis.max - xaxis.min)

        yaxis = plot.axes.y_axis
        yaxis.title.title_mode = AxisTitleMode.UseText
        yaxis.title.text = 'Transverse (m)'
        yaxis.title.color = Color.Blue

        # place the y-axis title at the y-coordinate 0.0
        yaxis.title.position = 100 * (0.0 - yaxis.min) / (yaxis.max - yaxis.min)

        tp.export.save_png('axis_title_2d.png', 600, supersample=3)

    ..  figure:: /_static/images/axis_title_2d.png
        :width: 300px
        :figwidth: 300px
    """


class DataAxis3DTitle(DataAxisTitle, Axis3DTitle):
    """Axis label string, font and style control for 3D plots.

    .. code-block:: python
        :emphasize-lines: 21-24,28-31,35-38

        from os import path
        import tecplot as tp
        from tecplot.constant import PlotType, SurfacesToPlot, Color, AxisTitleMode

        examples_dir = tp.session.tecplot_examples_directory()
        infile = path.join(examples_dir, 'SimpleData', 'F18.plt')
        dataset = tp.data.load_tecplot(infile)

        plot = tp.active_frame().plot(PlotType.Cartesian3D)
        plot.activate()

        plot.show_contour = True
        plot.contour(0).variable = dataset.variable('S')
        plot.contour(0).colormap_name = 'Sequential - Yellow/Green/Blue'
        plot.contour(0).legend.show = False

        plot.fieldmap(0).surfaces.surfaces_to_plot = SurfacesToPlot.BoundaryFaces

        xaxis = plot.axes.x_axis
        xaxis.show = True
        xaxis.title.title_mode = AxisTitleMode.UseText
        xaxis.title.text = 'Longitudinal (m)'
        xaxis.title.color = Color.BluePurple
        xaxis.title.position = 10

        yaxis = plot.axes.y_axis
        yaxis.show = True
        yaxis.title.title_mode = AxisTitleMode.UseText
        yaxis.title.text = 'Transverse (m)'
        yaxis.title.color = Color.BluePurple
        yaxis.title.position = 90

        zaxis = plot.axes.z_axis
        zaxis.show = True
        zaxis.title.title_mode = AxisTitleMode.UseText
        zaxis.title.text = 'Height (m)'
        zaxis.title.color = Color.BluePurple
        zaxis.title.offset = 13

        plot.view.fit()

        tp.export.save_png('axis_title_3d.png', 600, supersample=3)

    ..  figure:: /_static/images/axis_title_3d.png
        :width: 300px
        :figwidth: 300px
    """


class RadialAxisTitle(DataAxis2DTitle):
    """Radial axis label string, font and style control for polar plots.

    .. code-block:: python
        :emphasize-lines: 29-33

        import numpy as np
        import tecplot as tp
        from tecplot.constant import PlotType, Color, AxisTitleMode

        npoints = 300
        r = np.linspace(0, 2000, npoints)
        theta = np.linspace(0, 1000, npoints)

        frame = tp.active_frame()
        dataset = frame.create_dataset('Data', ['R', 'Theta'])
        zone = dataset.add_ordered_zone('Zone', (300,))
        zone.values('R')[:] = r
        zone.values('Theta')[:] = theta

        plot = frame.plot(PlotType.PolarLine)
        plot.activate()

        plot.axes.r_axis.max = np.max(r)

        plot.delete_linemaps()
        lmap = plot.add_linemap('Linemap', zone, dataset.variable('R'),
                                dataset.variable('Theta'))
        lmap.line.line_thickness = 0.8

        raxis = plot.axes.r_axis
        raxis.line.show_both_directions = True
        raxis.line.show_perpendicular = True

        raxis.title.title_mode = AxisTitleMode.UseText
        raxis.title.text = 'Radial Position (cm)'
        raxis.title.show_on_all_radial_axes = True
        raxis.title.color = Color.Blue
        raxis.title.position = 80

        plot.view.fit()

        tp.export.save_png('axis_title_radial.png', 600, supersample=3)

    ..  figure:: /_static/images/axis_title_radial.png
        :width: 300px
        :figwidth: 300px
    """

    @property
    def show_on_all_radial_axes(self):
        """Draw title along all radial axis lines.

        :type: `boolean <bool>`

        Example usage::

            >>> plot.axes.r_axis.line.show_perpendicular = True
            >>> plot.axes.r_axis.title.show_on_all_radial_axes = True
        """
        return self._get_style(bool, sv.SHOWONALLAXES)

    @show_on_all_radial_axes.setter
    def show_on_all_radial_axes(self, value):
        self._set_style(bool(value), sv.SHOWONALLAXES)
