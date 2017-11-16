from builtins import super

from collections import namedtuple

from ..tecutil import _tecutil
from ..constant import *
from ..exception import *
from .. import session
from ..tecutil import (ArgList, inherited_property, flatten_args, lock,
                       lock_attributes, sv)
from .axis import (Cartesian2DFieldAxis, Cartesian3DFieldAxis,
                   PolarAngleLineAxis, RadialLineAxis, SketchAxis, XYLineAxis)
from .grid import (Cartesian2DGridArea, Cartesian3DGridArea, GridArea,
                   PreciseGrid)
from .view import Cartesian2DViewport, PolarViewport, ReadOnlyViewport, Viewport


class Axes(session.Style):
    def __init__(self, plot, *svargs):
        self.plot = plot
        super().__init__(svargs, uniqueid=plot.frame.uid)

    def __eq__(self, that):
        return isinstance(that, type(self)) and (self.plot == that.plot)

    def __ne__(self, that):
        return not (self == that)

    def __iter__(self):
        self._iter_axes = ('x_axis', 'y_axis', 'z_axis', 'r_axis', 'theta_axis')
        self._iter_axis_index = 0
        return self

    def __next__(self):
        try:
            attr_name = self._iter_axes[self._iter_axis_index]
            self._iter_axis_index += 1
            attr = getattr(self, attr_name, None)
            if attr is not None:
                return attr
            else:
                return next(self)
        except IndexError:
            raise StopIteration

    def next(self):  # if sys.version_info < (3,)
        return self.__next__()

    @property
    def grid_area(self):
        """Area bounded by the axes.

        :type: `GridArea`

        This controls the background color and border of the axes::

            >>> from tecplot.constant import Color
            >>> plot.axes.grid_area.fill_color = Color.LightGreen
        """
        return GridArea(self)

    @property
    def preserve_scale(self):
        """Preserve scale (spacing between ticks) on range change.

        :type: `boolean <bool>`

        This maintains the axis scaling, i.e. the distance between values along
        the axis. If `False`, the axes length will be preserved when the range
        changes::

            >>> plot.axes.preserve_scale = False
            >>> # get axis via "plot.axes.x_axis(0)" for line plots
            >>> # or "plot.axes.x_axis" for field or sketch plots
            >>> axis.max = 10 # axis scale is changed (length is preserved)
        """
        return self._get_style(bool, sv.PRESERVEAXISSCALE)

    @preserve_scale.setter
    def preserve_scale(self, value):
        self._set_style(bool(value), sv.PRESERVEAXISSCALE)


class Axes2D(Axes):
    @property
    def precise_grid(self):
        """Precise dot grid.

        :type: `PreciseGrid`

        This is a set of small dots drawn at the intersection of every minor
        gridline. In line plots, the axis assignments for the first active
        mapping govern the precise dot grid. The precise dot grid option is
        disabled for the 3D Cartesian plots and Line plots when either axis for
        the first active line mapping uses a log scale::

            >>> plot.axes.precise_grid.show = True
        """
        return PreciseGrid(self)


class CartesianAxes(Axes):
    @property
    def xy_ratio(self):
        """X:Y axis scaling ratio.

        :type: `float` in percent

        This requires the axes to be in dependent mode::

            >>> from tecplot.constant import AxisMode
            >>> plot.axes.axis_mode = AxisMode.XYDependent
            >>> plot.axes.xy_ratio = 2
        """
        return self._get_style(float, sv.DEPXTOYRATIO)

    @xy_ratio.setter
    def xy_ratio(self, value):
        self._set_style(float(value), sv.DEPXTOYRATIO)


class Cartesian2DAxes(CartesianAxes):
    @property
    def auto_adjust_ranges(self):
        """Automatically adjust axis ranges to nice values.

        :type: `boolean <bool>`

        Axes limits will be adjusted to have the smallest number of significant
        digits possible::

            >>> plot.axes.auto_adjust_ranges = False
        """
        return self._get_style(bool, sv.AUTOADJUSTRANGESTONICEVALUES)

    @auto_adjust_ranges.setter
    def auto_adjust_ranges(self, value):
        self._set_style(bool(value), sv.AUTOADJUSTRANGESTONICEVALUES)

    @property
    def axis_mode(self):
        """Controls automatic adjustment of axis ranges.

        :type: `AxisMode`

        Possible values: `Independent`, `XYDependent`.

        If set to `XYDependent`, then setting the range of one axis
        automatically scales the other indicated axes proportionally to
        maintain the aspect ratio of the plot, effectively zooming in or out.
        If set to `Independent`, adjusting the range of one axis has no effect
        on other axes. Defaults to `Independent` for XY line plots,
        `XYDependent` for 2D Cartesian plots. Example usage::

            >>> from tecplot.constant import AxisMode
            >>> plot.axes.axis_mode = AxisMode.Independent
        """
        return self._get_style(AxisMode, sv.AXISMODE)

    @axis_mode.setter
    def axis_mode(self, value):
        self._set_style(AxisMode(value), sv.AXISMODE)

    @property
    def viewport(self):
        """Area of the frame used by the plot axes.

        :type: `Cartesian2DViewport`

        Example usage::

            >>> plot.axes.viewport.left = 5
            >>> plot.axes.viewport.right = 95
            >>> plot.axes.viewport.top = 95
            >>> plot.axes.viewport.bottom = 5
        """
        return Cartesian2DViewport(self)

    @property
    def grid_area(self):
        """Area bounded by the axes.

        :type: `GridArea`

        This controls the background color and border of the axes::

            >>> from tecplot.constant import Color
            >>> plot.axes.grid_area.fill_color = Color.LightGreen
        """
        return Cartesian2DGridArea(self)


class Cartesian3DAxes(CartesianAxes):
    @property
    def xz_ratio(self):
        """X:Z axis scaling ratio.

        :type: `float` in percent

        This requires the axes to be in dependent mode::

            >>> from tecplot.constant import AxisMode
            >>> plot.axes.axis_mode = AxisMode.XYZDependent
            >>> plot.axes.xy_ratio = 2
            >>> plot.axes.xz_ratio = 20
        """
        return self._get_style(float, sv.DEPXTOZRATIO)

    @xz_ratio.setter
    def xz_ratio(self, value):
        self._set_style(float(value), sv.DEPXTOZRATIO)

    @inherited_property(Cartesian2DAxes)
    def axis_mode(self):
        """Scale dependencies along each axis.

        :type: `AxisMode`

        Possible values: `Independent`, `XYDependent`, `XYZDependent`.

        If set to `XYDependent` or `XYZDependent`, then setting the range of
        one axis automatically scales the other indicated axes proportionally
        to maintain the aspect ratio of the plot, effectively zooming in or
        out. If set to `Independent`, adjusting the range of one axis has no
        effect on other axes. Defaults to `XYZDependent` for 3D Cartesian
        plots. Both dependent modes allow specifying the axes scaling ratios::

            >>> from tecplot.constant import AxisMode
            >>> plot.axes.axis_mode = AxisMode.XYZDependent
            >>> plot.axes.xy_ratio = 2
            >>> plot.axes.xz_ratio = 20
        """

    @property
    def aspect_ratio_limit(self):
        """Scale limit of the axes aspect ratio.

        :type: `float`

        This is the limit above which the axes relative scales will be pegged
        to `aspect_ratio_reset`. The following example will set the aspect
        ratio between scales to 1 if they first exceed a ratio of 10::

            >>> plot.axes.aspect_ratio_limit = 10
            >>> plot.axes.aspect_ratio_reset = 1
            >>> plot.axes.reset_scale()
        """
        return self._get_style(float, sv.ASPECTRATIOLIMIT)

    @aspect_ratio_limit.setter
    def aspect_ratio_limit(self, value):
        self._set_style(float(value), sv.ASPECTRATIOLIMIT)

    @property
    def aspect_ratio_reset(self):
        """Axes scale aspect ratio used when `aspect_ratio_limit` is exceeded.

        :type: `float`

        This is the aspect ratio used to scale the axes when the data's aspect
        ratio exceeds the value set to `aspect_ratio_limit`. The following
        example will set the aspect ratio between scales to 10 if they first
        exceed a ratio of 15::

            >>> plot.axes.aspect_ratio_limit = 15
            >>> plot.axes.aspect_ratio_reset = 10
            >>> plot.axes.reset_scale()
        """
        return self._get_style(float, sv.ASPECTRATIORESET)

    @aspect_ratio_reset.setter
    def aspect_ratio_reset(self, value):
        self._set_style(float(value), sv.ASPECTRATIORESET)

    @property
    def range_aspect_ratio_limit(self):
        """Range limit of the axes aspect ratio.

        :type: `float`

        This is the limit above which the axes' relative ranges will be pegged
        to `range_aspect_ratio_reset`. The following example will set the
        aspect ratio between ranges to 1 if they first exceed a ratio of 10::

            >>> plot.axes.range_aspect_ratio_limit = 10
            >>> plot.axes.range_aspect_ratio_reset = 1
            >>> plot.axes.reset_range()
        """
        return self._get_style(float, sv.BOXASPECTRATIOLIMIT)

    @range_aspect_ratio_limit.setter
    def range_aspect_ratio_limit(self, value):
        self._set_style(float(value), sv.BOXASPECTRATIOLIMIT)

    @property
    def range_aspect_ratio_reset(self):
        """Axes range aspect ratio used `range_aspect_ratio_limit` is exceeded.

        :type: `float`

        This is the aspect ratio used to set the ranges of the axes when the
        axes' aspect ratios exceed the value of `range_aspect_ratio_limit`. The
        following example will set the aspect ratio between ranges to 10 if
        they first exceed a ratio of 15::

            >>> plot.axes.range_aspect_ratio_limit = 15
            >>> plot.axes.range_aspect_ratio_reset = 10
            >>> plot.axes.reset_range()
        """
        return self._get_style(float, sv.BOXASPECTRATIORESET)

    @range_aspect_ratio_reset.setter
    def range_aspect_ratio_reset(self, value):
        self._set_style(float(value), sv.BOXASPECTRATIORESET)

    @property
    def auto_edge_assignment(self):
        """Enable automatically choosing which edges to label.

        :type: `bool`

        Example usage::

            >>> plot.axes.auto_edge_assignment = True
        """
        return self._get_style(bool, sv.EDGEAUTORESET)

    @auto_edge_assignment.setter
    def auto_edge_assignment(self, value):
        self._set_style(bool(value), sv.EDGEAUTORESET)

    @property
    def viewport(self):
        """Area of the frame used by the plot axes.

        :type: `ReadOnlyViewport`

        Example usage::

            >>> print(plot.axes.viewport.bottom)
            5
        """
        return ReadOnlyViewport(self)

    @lock()
    def reset_scale(self):
        """Recalculate and set the scale factors for each axis.

        Aspect ratio limits are taken into account::

            >>> plot.axes.reset_scale()
        """
        with self.plot.frame.activated():
            if not _tecutil.Reset3DScaleFactors():
                raise TecplotSystemError()

    @lock()
    def reset_range(self):
        """Recalculate and set the ranges for each axis.

        Example usage::

            >>> plot.axes.reset_range()
        """
        with self.plot.frame.activated():
            if not _tecutil.Reset3DAxes():
                raise TecplotSystemError()

    @lock()
    def reset_origin(self, location=OriginResetLocation.DataCenter):
        """Set the origin to the specified location.

        Parameters:
            location (`OriginResetLocation`, optional): Either the center of
                the data with `OriginResetLocation.DataCenter` (default) or the
                center of the viewport with `OriginResetLocation.ViewCenter`.

        Example usage::

            >>> from tecplot.constant import OriginResetLocation
            >>> plot.axes.reset_origin(OriginResetLocation.ViewCenter)
        """
        with self.plot.frame.activated():
            with ArgList() as arglist:
                arglist[sv.ORIGINRESETLOCATION] = OriginResetLocation(location)
                if not _tecutil.Reset3DOriginX(arglist):
                    raise TecplotSystemError()

    @property
    def grid_area(self):
        """Area of the viewport used by the axes.

        :type: `Cartesian3DGridArea`

        Example usage::

            >>> plot.axes.grid_area.fill_color = Color.LightGreen
        """
        return Cartesian3DGridArea(self)

    @property
    def padding(self):
        """Margin of axis padding around data.

        :type: `float` in percent of data extent.

        Example usage::

            >>> plot.axes.padding = 5
        """
        style = session.Style(**self._style_attrs)
        return style._get_style(float, sv.GLOBALTHREED, sv.AXISBOXPADDING)

    @padding.setter
    def padding(self, value):
        style = session.Style(**self._style_attrs)
        style._set_style(float(value), sv.GLOBALTHREED, sv.AXISBOXPADDING)

    @property
    def orientation_axis(self):
        """Get the 3D Orientation Axes.
        
        :type: `OrientationAxis`
        
        Example usage::
        
            >>> # Hide the orientation axes
            >>> plot.axes.orientation_axis.show = False
        """
        return OrientationAxis(self)


class SketchAxes(Cartesian2DAxes, Axes2D):
    """(X, Y) axes style control for sketch plots.

    Sketch plots have cartesian *x* and *y* axes which can be adjusted using
    the viewport:

    .. code-block:: python
        :emphasize-lines: 7-8,10-13

        import tecplot as tp
        from tecplot.constant import PlotType

        frame = tp.active_frame()
        plot = frame.plot(PlotType.Sketch)

        plot.axes.x_axis.show = True
        plot.axes.y_axis.show = True

        plot.axes.viewport.left = 10
        plot.axes.viewport.right = 90
        plot.axes.viewport.bottom = 10
        plot.axes.viewport.top = 90

        tp.export.save_png('axes_sketch.png', 600, supersample=3)

    ..  figure:: /_static/images/axes_sketch.png
        :width: 300px
        :figwidth: 300px
    """
    def __init__(self, plot):
        super().__init__(plot, sv.SKETCHAXIS)

    @property
    def x_axis(self):
        """X-axis style control.

        :type: `SketchAxis`

        Example usage::

            >>> plot.axes.x_axis.show = True
        """
        return SketchAxis(self, sv.X)

    @property
    def y_axis(self):
        """Y-axis style control.

        :type: `SketchAxis`

        Example usage::

            >>> plot.axes.y_axis.show = True
        """
        return SketchAxis(self, sv.Y)


class Cartesian2DFieldAxes(Cartesian2DAxes, Axes2D):
    """(X, Y) axes style control for 2D field plots.

    .. code-block:: python
        :emphasize-lines: 15-17

        from os import path
        import tecplot as tp
        from tecplot.constant import PlotType

        examples_dir = tp.session.tecplot_examples_directory()
        infile = path.join(examples_dir, 'SimpleData', 'HeatExchanger.plt')
        dataset = tp.data.load_tecplot(infile)

        frame = tp.active_frame()
        plot = frame.plot(PlotType.Cartesian2D)

        plot.show_shade = False
        plot.show_contour = True

        plot.axes.auto_adjust_ranges = True
        plot.axes.precise_grid.show = True
        plot.axes.precise_grid.size = 0.05

        plot.view.fit()

        tp.export.save_png('axes_2d.png', 600, supersample=3)

    ..  figure:: /_static/images/axes_2d.png
        :width: 300px
        :figwidth: 300px
    """
    def __init__(self, plot):
        super().__init__(plot, sv.TWODAXIS)

    @property
    def x_axis(self):
        """X-axis style control.

        :type: `Cartesian2DFieldAxis`

        Example usage::

            >>> plot.axes.x_axis.show = False
        """
        return Cartesian2DFieldAxis(self, sv.X)

    @property
    def y_axis(self):
        """Y-axis style control.

        :type: `Cartesian2DFieldAxis`

        Example usage::

            >>> plot.axes.y_axis.show = False
        """
        return Cartesian2DFieldAxis(self, sv.Y)


class Cartesian3DFieldAxes(Cartesian3DAxes):
    """(X, Y, Z) axes style control for 3D field plots.

    .. code-block:: python
        :emphasize-lines: 12-16

        from os import path
        import tecplot as tp
        from tecplot.constant import PlotType, Color

        examples_dir = tp.session.tecplot_examples_directory()
        infile = path.join(examples_dir, 'SimpleData', 'Sphere.lpk')
        dataset = tp.load_layout(infile)

        frame = tp.active_frame()
        plot = frame.plot()

        plot.axes.x_axis.show = True
        plot.axes.y_axis.show = True
        plot.axes.z_axis.show = True
        plot.axes.grid_area.fill_color = Color.SkyBlue
        plot.axes.padding = 20

        plot.view.fit()

        tp.export.save_png('axes_3d.png', 600, supersample=3)

    ..  figure:: /_static/images/axes_3d.png
        :width: 300px
        :figwidth: 300px
    """
    def __init__(self, plot):
        super().__init__(plot, sv.THREEDAXIS)

    @property
    def x_axis(self):
        """X-axis style control.

        :type: `Cartesian3DFieldAxis`

        Example usage::

            >>> plot.axes.x_axis.show = True
        """
        return Cartesian3DFieldAxis(self, sv.X)

    @property
    def y_axis(self):
        """Y-axis style control.

        :type: `Cartesian3DFieldAxis`

        Example usage::

            >>> plot.axes.y_axis.show = True
        """
        return Cartesian3DFieldAxis(self, sv.Y)

    @property
    def z_axis(self):
        """Z-axis style control.

        :type: `Cartesian3DFieldAxis`

        Example usage::

            >>> plot.axes.z_axis.show = True
        """
        return Cartesian3DFieldAxis(self, sv.Z)


class PolarLineAxes(Axes2D):
    """(R, Theta) axes style control for polar plots.

    Example usage:

    .. code-block:: python
        :emphasize-lines: 19-20

        import numpy as np
        import tecplot as tp
        from tecplot.constant import PlotType, ThetaMode

        frame = tp.active_frame()

        npoints = 300
        r = np.linspace(0, 2000, npoints)
        theta = np.linspace(0, 10, npoints)

        dataset = frame.create_dataset('Data', ['R', 'Theta'])
        zone = dataset.add_ordered_zone('Zone', (300,))
        zone.values('R')[:] = r
        zone.values('Theta')[:] = theta

        plot = frame.plot(PlotType.PolarLine)
        plot.activate()

        plot.axes.r_axis.max = np.max(r)
        plot.axes.theta_axis.mode = ThetaMode.Radians

        plot.delete_linemaps()
        lmap = plot.add_linemap('Linemap', zone, dataset.variable('R'),
                                dataset.variable('Theta'))
        lmap.line.line_thickness = 0.8

        plot.view.fit()

        tp.export.save_png('axes_polar.png', 600, supersample=3)

    ..  figure:: /_static/images/axes_polar.png
        :width: 300px
        :figwidth: 300px
    """
    def __init__(self, plot):
        super().__init__(plot, sv.POLARAXIS)

    @property
    def r_axis(self):
        """Radial axis style control.

        :type: `RadialLineAxis`

        Example usage::

            >>> plot.axes.r_axis.title.text = 'R (meters)'
        """
        return RadialLineAxis(self)

    @property
    def theta_axis(self):
        """Polar-angle axis style control.

        :type: `PolarAngleLineAxis`

        Example usage::

            >>> plot.axes.theta_axis.title.text = 'Theta (radians)'
        """
        return PolarAngleLineAxis(self)

    @property
    def viewport(self):
        """Area of the frame used by the plot axes outside the grid area.

        :type: `PolarViewport`

        Example usage::

            >>> from tecplot.constant import Color
            >>> plot.axes.viewport.fill_color = Color.LightGreen
        """
        return PolarViewport(self)


class XYLineAxes(Cartesian2DAxes, Axes2D):
    """(X, Y) axes style control for line plots.

    The ``axes`` property of a `XYLinePlot` allows access to the several ``x``
    and ``y`` axes by index. Linemaps can use any of the five such axes. In
    this example, we create two sets of data with different scales and the
    second y-axis is used on the right side of the plot:

    .. code-block:: python
        :emphasize-lines: 32,44

        import numpy as np
        import tecplot as tp
        from tecplot.constant import PlotType, Color

        frame = tp.active_frame()

        npoints = 100
        x = np.linspace(-10,10,npoints)
        t = x**2
        p = 0.1 * np.sin(x)

        dataset = frame.create_dataset('data', ['Position (m)', 'Temperature (K)',
                                                'Pressure (Pa)'])
        zone = dataset.add_ordered_zone('zone', (100,))
        zone.values('Position (m)')[:] = x
        zone.values('Temperature (K)')[:] = t
        zone.values('Pressure (Pa)')[:] = p

        plot = frame.plot(PlotType.XYLine)
        plot.activate()
        plot.delete_linemaps()

        temp = plot.add_linemap('temp', zone, dataset.variable('Position (m)'),
                         dataset.variable('Temperature (K)'))
        press = plot.add_linemap('press', zone, dataset.variable('Position (m)'),
                                 dataset.variable('Pressure (Pa)'))

        # Color the line and the y-axis for temperature
        temp.line.color = Color.RedOrange
        temp.line.line_thickness = 0.8

        ax = plot.axes.y_axis(0)
        ax.line.color = temp.line.color
        ax.tick_labels.color = temp.line.color
        ax.title.color = temp.line.color

        # set pressure linemap to second x-axis
        press.y_axis_index = 1

        # Color the line and the y-axis for pressure
        press.line.color = Color.Chartreuse
        press.line.line_thickness = 0.8

        ax = plot.axes.y_axis(1)
        ax.line.color = press.line.color
        ax.tick_labels.color = press.line.color
        ax.title.color = press.line.color

        tp.export.save_png('axes_line.png', 600, supersample=3)

    ..  figure:: /_static/images/axes_line.png
        :width: 300px
        :figwidth: 300px
    """
    def __init__(self, plot):
        super().__init__(plot, sv.XYLINEAXIS)

    def __iter__(self):
        self._iter_axes = ['x_axis', 'y_axis'] * 5
        self._iter_axis_index = 0
        return self

    def __next__(self):
        try:
            attr_name = self._iter_axes[self._iter_axis_index]
            index = self._iter_axis_index // 2
            self._iter_axis_index += 1
            return getattr(self, attr_name)(index)
        except IndexError:
            raise StopIteration

    def x_axis(self, index):
        """X-axis style control.

        :type: `XYLineAxis`

        There are five x-axes for each `XYLinePlot`, indexed from 0 to 4
        inclusive::

            >>> plot.axes.x_axis(0).show = True
        """
        return XYLineAxis(self, sv.X, index)

    def y_axis(self, index):
        """Y-axis style control.

        :type: `XYLineAxis`

        There are five y-axes for each `XYLinePlot`, indexed from 0 to 4
        inclusive::

            >>> plot.axes.y_axis(0).show = True
        """
        return XYLineAxis(self, sv.Y, index)


class OrientationAxis(session.Style):
    """The orientation axis for 3D Field plots.

    This is the small (x, y, z) reference axis object which can moved, resized
    and modified using this class. 
    
    By default, all 3D plots show the 3D orientation axis in the upper right 
    of the frame. It can be repositioned by setting `position` as shown
    below.
    
    .. code-block:: python
        :emphasize-lines: 12-13

        from os import path
        import tecplot as tp
        from tecplot.constant import Color
        
        examples_dir = tp.session.tecplot_examples_directory()
        infile = path.join(examples_dir, 'SimpleData', 'Sphere.lpk')
        dataset = tp.load_layout(infile)
        
        frame = tp.active_frame()
        plot = frame.plot()
        
        plot.axes.orientation_axis.position = 15, 15
        plot.axes.orientation_axis.color = Color.BrightCyan
        
        plot.axes.reset_range()
        plot.view.fit()
        
        tp.export.save_png('axes_orientation.png', 600, supersample=3)
        
    ..  figure:: /_static/images/axes_orientation.png
        :width: 300px
        :figwidth: 300px
    """
    def __init__(self, axes):
        self.axes = axes
        super().__init__(axes._sv, sv.FRAMEAXIS, **axes._style_attrs)

    @property
    def show(self):
        """Enable drawing of the orientation axis.

        :type: `boolean <bool>`

        Example usage::

            >>> plot.axes.orientation_axis.show = False
        """
        return self._get_style(bool, sv.SHOW)

    @show.setter
    def show(self, value):
        self._set_style(bool(value), sv.SHOW)

    @property
    def size(self):
        """Size of the orientation axis as a percentage of frame size (0-100).

        :type: `float`

        Example usage::

            >>> plot.axes.orientation_axis.size = 4.0
        """
        return self._get_style(float, sv.SIZE)

    @size.setter
    def size(self, value):
        self._set_style(float(value), sv.SIZE)

    @property
    def line_thickness(self):
        """Line thickness used when drawing the orientation axis as a percentage of frame height.
        
        :type: `float`

        Example usage::

            >>> plot.axes.orientation_axis.line_thickness = 0.8
        """
        return self._get_style(float, sv.LINETHICKNESS)

    @line_thickness.setter
    def line_thickness(self, value):
        self._set_style(float(value), sv.LINETHICKNESS)

    @property
    def color(self):
        """`Color` of the orientation axes.

        :type: `Color`

        Example usage::

            >>> from tecplot.constant import Color
            >>> plot.axes.orientation_axis.color = Color.Cyan
        """
        return self._get_style(Color, sv.COLOR)

    @color.setter
    def color(self, value):
        self._set_style(Color(value), sv.COLOR)

    _Position = namedtuple('Position', ['x', 'y'])

    @property
    def position(self):
        """``(x, y)`` position of the orientation axis as a percentage distance from the lower-left corner of the viewport.

        :type: 2-tuple of `floats <float>`: ``(x, y)``

        The position is in percent from the lower-left corner of the viewport::

            >>> plot.axes.orientation_axis.position = (15, 15)
        """
        x = self._get_style(float, sv.XYPOS, sv.X)
        y = self._get_style(float, sv.XYPOS, sv.Y)
        return OrientationAxis._Position(x, y)

    @position.setter
    def position(self, *pos):
        pos = OrientationAxis._Position(*flatten_args(*pos))
        self._set_style(float(pos.x), sv.XYPOS, sv.X)
        self._set_style(float(pos.y), sv.XYPOS, sv.Y)

    @property
    def show_variable_name(self):
        """Use variable names instead of 'X', 'Y' and 'Z'.

        :type: `boolean <bool>`

        Example usage::

            >>> plot.axes.orientation_axis.show_variable_name = True
        """
        return self._get_style(bool, sv.SHOWVARIABLENAME)

    @show_variable_name.setter
    def show_variable_name(self, value):
        self._set_style(bool(value), sv.SHOWVARIABLENAME)
