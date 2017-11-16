from builtins import int

import ctypes

from collections import namedtuple

from ..tecutil import _tecutil
from ..constant import *
from ..exception import *
from .. import session, version
from ..tecutil import ArgList, Index, IndexSet, sv, color_spec, lock
from .scatter import Symbol, TextSymbol, GeometrySymbol


class StreamtraceStyle(session.Style):
    def __init__(self, streamtrace, *sv_args):
        self.streamtrace = streamtrace
        kw = dict(uniqueid=streamtrace.plot.frame.uid)
        super().__init__(streamtrace._sv, *sv_args, **kw)

_XYZ = namedtuple('XYZ', ['x', 'y', 'z'])
_XYZ.__new__.__defaults__ = (None, None, None)


class StreamtraceTiming(StreamtraceStyle):
    """Timed markers for streamlines.

    Use `StreamtraceTiming` to control timed markers for streamlines, and timed
    dashes for all types of streamtraces. Stream markers are drawn at time
    locations along streamlines. The spacing between stream markers is
    proportional to the magnitude of the local vector field.

    .. code-block:: python
        :emphasize-lines: 22-24

        import tecplot
        from tecplot.constant import *
        import os

        examples_dir = tecplot.session.tecplot_examples_directory()
        datafile = os.path.join(examples_dir, 'SimpleData', 'VortexShedding.plt')
        dataset = tecplot.data.load_tecplot(datafile)

        frame = tecplot.active_frame()
        frame.plot_type = tecplot.constant.PlotType.Cartesian2D

        plot = frame.plot()
        plot.vector.u_variable = dataset.variable('U(M/S)')
        plot.vector.v_variable = dataset.variable('V(M/S)')
        plot.show_streamtraces = True
        plot.show_shade = True
        plot.fieldmap(0).shade.color = Color.LightBlue


        streamtraces = plot.streamtraces
        streamtraces.show_markers = True
        timing = streamtraces.timing
        timing.anchor = 0
        timing.delta = 0.0001

        streamtraces.marker_size = 1.5
        streamtraces.marker_symbol().shape =GeomShape.RTri
        streamtraces.marker_color = Color.Mahogany

        streamtraces.add_rake(start_position=(-0.003, 0.005),
                              end_position=(-0.003, -0.005),
                              stream_type=Streamtrace.TwoDLine,
                              num_seed_points=10)


        plot.axes.y_axis.min = -0.02
        plot.axes.y_axis.max = 0.02
        plot.axes.x_axis.min = -0.008
        plot.axes.x_axis.max = 0.04

        tecplot.export.save_png('streamtrace_timing.png', 600, supersample=3)

    .. figure:: /_static/images/streamtrace_timing.png
        :width: 300px
        :figwidth: 300px

    """

    def __init__(self, streamtrace):
        super().__init__(streamtrace, sv.STREAMTIMING)

    @lock()
    def reset_delta(self):
        """Reset the time delta for dashed streamtraces.


        The delta time is reset such that a stream dash in the vicinity of
        the maximum vector magnitude will have a length approximately equal
        to 10 percent of the frame width.

        Raises:
            `TecplotSystemError`: Streamtraces time delta could not be reset.

        Example usage::

            >>> plot.streamtraces.timing.reset_delta()
        """
        with self.streamtrace.plot.frame.activated():
            if not _tecutil.StreamtraceResetDelta():
                raise TecplotSystemError()

    @property
    def _show_dashes(self):
        return self._get_style(bool, sv.SHOWDASHES)

    @_show_dashes.setter
    def _show_dashes(self, value):
        self._set_style(bool(value), sv.SHOWDASHES)

    @property
    def _show_markers(self):
        return self._get_style(bool, sv.SHOWMARKERS)

    @_show_markers.setter
    def _show_markers(self, value):
        self._set_style(bool(value), sv.SHOWMARKERS)

    @property
    def _marker_color(self):
        return color_spec(self._get_style(Color, sv.MARKCOLOR),
                          self.streamtrace.plot)

    @_marker_color.setter
    def _marker_color(self, value):
        self._set_style(color_spec(value), sv.MARKCOLOR)

    @property
    def _marker_size(self):
        return self._get_style(float, sv.MARKSIZE)

    @_marker_size.setter
    def _marker_size(self, value):
        self._set_style(float(value), sv.MARKSIZE)

    @property
    def _dash_skip(self):
        return self._get_style(int, sv.DASHSKIP)

    @_dash_skip.setter
    def _dash_skip(self, value):
        self._set_style(int(value), sv.DASHSKIP)

    @property
    def _marker_symbol_type(self):
        return Symbol(self, sv.MARKSYMBOL)._symbol_type

    @_marker_symbol_type.setter
    def _marker_symbol_type(self, value):
        Symbol(self, sv.MARKSYMBOL)._symbol_type = value

    def _marker_symbol(self, symbol_type=None):
        _dispatch = {
            SymbolType.Text: TextSymbol,
            SymbolType.Geometry: GeometrySymbol}
        return _dispatch[symbol_type or self._marker_symbol_type](
            self, sv.MARKSYMBOL)

    @property
    def start(self):
        """Time at which the first marker should be drawn.

        :type: `float`

        A start time of zero means that the first marker is drawn at the
        starting point. A start time of 2.5 means that the first stream
        marker is drawn 2.5 time units downstream of the starting point.

        Example usage::

            >>> plot.streamtraces.timing.start = 2.5
        """
        return self._get_style(float, sv.TIMESTART)

    @start.setter
    def start(self, value):
        self._set_style(float(value), sv.TIMESTART)

    @property
    def end(self):
        """Time after which no stream markers are drawn.

        :type: `float`

        Example usage::

            >>> plot.streamtraces.timing.end = 3.0
        """
        return self._get_style(float, sv.TIMEEND)

    @end.setter
    def end(self, value):
        self._set_style(float(value), sv.TIMEEND)

    @property
    def anchor(self):
        """Time that a dash is guaranteed to start.

        :type: `float`

        A dash is guaranteed to start at `anchor`, provided the start
        and end time surround the dash.

        Example usage::

            >>> plot.streamtraces.timing.anchor = 1.1
        """
        return self._get_style(float, sv.TIMEANCHOR)

    @anchor.setter
    def anchor(self, value):
        self._set_style(float(value), sv.TIMEANCHOR)

    @property
    def delta(self):
        """Time between stream markers.

        :type: `float`

        `delta` is the time interval that measures the time between
        stream markers. The actual distance between markers is the product
        of this number and the local `Vector` magnitude.

        Call `StreamtraceTiming.reset_delta()` to reset this to the default.

        Example usage::

            >>> plot.streamtraces.timing.delta = 0.1
        """
        return self._get_style(float, sv.TIMEDELTA)

    @delta.setter
    def delta(self, value):
        self._set_style(float(value), sv.TIMEDELTA)


class StreamtraceTerminationLine(StreamtraceStyle):
    """Streamtraces termination line attributes.

    A streamtrace termination line is a polyline that terminates any
    streamtraces that cross it. The termination line is useful for stopping
    streamtraces before they spiral or stall.

    .. note::
        Before setting any `StreamtraceTerminationLine` properties, you must
        `add a termination line <set_termination_line>`.

    Streamtraces are terminated whenever any of the following occur:

        * The maximum number of integration steps is reached.
        * Any point where a streamtrace passes outside the available data.
        * The streamtrace reaches a point where the velocity magnitude is zero.

    .. code-block:: python
        :emphasize-lines: 19-29

        import tecplot
        from tecplot.constant import *
        import os

        examples_dir = tecplot.session.tecplot_examples_directory()
        datafile = os.path.join(examples_dir, 'SimpleData', 'VortexShedding.plt')
        dataset = tecplot.data.load_tecplot(datafile)

        frame = tecplot.active_frame()
        frame.plot_type = tecplot.constant.PlotType.Cartesian2D

        plot = frame.plot()
        plot.vector.u_variable = dataset.variable('U(M/S)')
        plot.vector.v_variable = dataset.variable('V(M/S)')
        plot.show_streamtraces = True
        plot.show_shade = True
        plot.fieldmap(0).shade.color = Color.LightBlue

        streamtraces = plot.streamtraces
        streamtraces.set_termination_line([(0.03, 0.005),
                                           (0.03, -0.005),])

        term_line = streamtraces.termination_line
        term_line.is_active = True
        term_line.show = True
        term_line.color = Color.Red
        term_line.line_pattern = LinePattern.Dashed
        term_line.pattern_length = .5
        term_line.line_thickness = .5

        streamtraces.add_rake(start_position=(-0.003, 0.005),
                              end_position=(-0.003, -0.005),
                              stream_type=Streamtrace.TwoDLine,
                              num_seed_points=10)

        plot.axes.y_axis.min = -0.02
        plot.axes.y_axis.max = 0.02
        plot.axes.x_axis.min = -0.01
        plot.axes.x_axis.max = 0.04

        tecplot.export.save_png('streamtrace_term_line.png', 600, supersample=3)

    .. figure:: /_static/images/streamtrace_term_line.png
        :width: 300px
        :figwidth: 300px
    """

    def __init__(self, streamtrace):
        super().__init__(streamtrace, sv.TERMLINE)

    @property
    def is_active(self):
        """Activate/disable the streamtrace termination line.

        :type: `boolean <bool>`

        Set to `True` to activate the termination line and terminate any
        streamtraces that cross it. Set to `False` and redraw the plot
        with unterminated streamtraces.

        .. note::
            To display the termination line itself, set `show` to `True`.

        Example usage::

            >>> plot.streamtraces.termination_line.is_active = True
        """
        return self._get_style(bool, sv.ISACTIVE)

    @is_active.setter
    def is_active(self, value):
        self._set_style(bool(value), sv.ISACTIVE)

    @property
    def show(self):
        """Display the termination line.

        :type: `boolean <bool>`

        Set to `True` to display the termination line. Set to `False` and
        redraw the plot to display terminated streamlines (if `is_active` is
        set to `True`), but not the termination line itself.

        .. note::
            To display terminated streamtraces, `is_active` must be set to
            `True`.

        Example usage::

            >>> plot.streamtraces.termination_line.show = True
        """
        return self._get_style(bool, sv.SHOW)

    @show.setter
    def show(self, value):
        self._set_style(bool(value), sv.SHOW)

    @property
    def color(self):
        """Color of the termination line.

        :type: `Color`

        Example usage::

            >>> plot.streamtraces.termination_line.color = Color.Red
        """
        return self._get_style(Color, sv.COLOR)

    @color.setter
    def color(self, value):
        self._set_style(Color(value), sv.COLOR)

    @property
    def line_pattern(self):
        """Pattern of the terminating line.

        :type: `LinePattern`

        Example usage::

            >>> plot.streamtraces.termination_line.line_pattern = LinePattern.Dotted
        """
        return self._get_style(LinePattern, sv.LINEPATTERN)

    @line_pattern.setter
    def line_pattern(self, value):
        self._set_style(LinePattern(value), sv.LINEPATTERN)

    @property
    def pattern_length(self):
        """Length of the pattern as a percentage of frame height.

        :type: `float`

        Example usage::

            >>> plot.streamtraces.termination_line.pattern_length = 2
        """
        return self._get_style(float, sv.PATTERNLENGTH)

    @pattern_length.setter
    def pattern_length(self, value):
        self._set_style(float(value), sv.PATTERNLENGTH)

    @property
    def line_thickness(self):
        """Thickness of the termination line as a percentage of frame height.

        :type: `float`

        Example usage::

            >>> plot.streamtraces.termination_line.line_thickness = 0.1
        """
        return self._get_style(float, sv.LINETHICKNESS)

    @line_thickness.setter
    def line_thickness(self, value):
        self._set_style(float(value), sv.LINETHICKNESS)


class StreamtraceRodRibbonMesh(StreamtraceStyle):
    """Streamtraces rod/ribbon mesh attributes.

    .. note::
        To set the mesh color or line thickness, see `Streamtraces.color`
        and `Streamtraces.line_thickness`.

    .. code-block:: python
        :emphasize-lines: 25-28

        import os
        import tecplot
        from tecplot.constant import *

        examples_dir = tecplot.session.tecplot_examples_directory()
        datafile = os.path.join(examples_dir, 'SimpleData', 'DownDraft.plt')
        dataset = tecplot.data.load_tecplot(datafile)

        frame = tecplot.active_frame()
        frame.plot_type = tecplot.constant.PlotType.Cartesian3D

        plot = frame.plot()
        plot.fieldmap(0).surfaces.surfaces_to_plot = SurfacesToPlot.BoundaryFaces
        plot.show_mesh = False
        plot.show_shade = False
        plot.show_edge = True

        plot.vector.u_variable_index = 4
        plot.vector.v_variable_index = 5
        plot.vector.w_variable_index = 6
        plot.show_streamtraces = True

        ribbon = plot.streamtraces.rod_ribbon
        ribbon.width = .008
        ribbon.mesh.show = True
        ribbon.mesh.line_thickness = 0.2
        #Ribbon mesh color inherited from streamtrace color
        plot.streamtraces.color = Color.AquaGreen

        plot.streamtraces.add_rake(
            start_position=(0, 0.22, 0),
            end_position=(0, 0.22, 0.1),
            stream_type=Streamtrace.VolumeRibbon)

        plot.view.width = 0.644
        plot.view.alpha = 66.4
        plot.view.theta = -122.4
        plot.view.psi   = 124.5
        plot.view.position = (5.3, 3.56, -4.3)

        tecplot.export.save_png('streamtrace_ribbon_mesh.png', 600, supersample=3)


    .. figure:: /_static/images/streamtrace_ribbon_mesh.png
        :width: 300px
        :figwidth: 300px

    """
    def __init__(self, streamtrace):
        super().__init__(streamtrace, sv.MESH)

    @property
    def show(self):
        """Display mesh.

        .. note::

            The mesh color for streamtraces is determined by the line color.

        :type: `boolean <bool>`

        Example usage::

            >>> plot.streamtraces.rod_ribbon.mesh.show = True
        """
        return self._get_style(bool, sv.SHOW)

    @show.setter
    def show(self, value):
        self._set_style(bool(value), sv.SHOW)

    @property
    def line_thickness(self):
        """ Get/Set streamtrace rod/ribbon mesh line thickness as a percentage
        of frame height.

        Typical values are **.02, .1, .4, .8, 1.5**

        :type: `float`

        Example usage::

            >>> plot.streamtraces.rod_ribbon.mesh.line_thickness = 0.2
        """
        return self._get_style(float, sv.LINETHICKNESS)

    @line_thickness.setter
    def line_thickness(self, value):
        self._set_style(float(value), sv.LINETHICKNESS)


class StreamtraceRodRibbonContour(StreamtraceStyle):
    """Contour flooding display for streamtrace rod/ribbons.

    .. code-block:: python
        :emphasize-lines: 15-16,28-29

        import os
        import numpy as np
        import tecplot
        from tecplot.constant import *

        examples_dir = tecplot.session.tecplot_examples_directory()
        datafile = os.path.join(examples_dir, 'SimpleData', 'DownDraft.plt')
        dataset = tecplot.data.load_tecplot(datafile)

        frame = tecplot.active_frame()
        frame.plot_type = tecplot.constant.PlotType.Cartesian3D

        plot = frame.plot()
        plot.fieldmap(0).surfaces.surfaces_to_plot = SurfacesToPlot.BoundaryFaces
        plot.contour(0).variable = dataset.variable(3)
        plot.contour(0).levels.reset_levels(np.linspace(1.15,1.25,11))
        plot.show_mesh = False
        plot.show_shade = False
        plot.show_edge = True

        plot.vector.u_variable_index = 4
        plot.vector.v_variable_index = 5
        plot.vector.w_variable_index = 6
        plot.show_streamtraces = True

        rod = plot.streamtraces.rod_ribbon
        rod.width = .008
        rod.contour.show = True
        rod.contour.use_lighting_effect = True

        plot.streamtraces.add_rake(
            start_position=(0, 0.22, 0),
            end_position=(0, 0.22, 0.1),
            stream_type=Streamtrace.VolumeRod)

        plot.view.width = 0.644
        plot.view.alpha = 66.4
        plot.view.theta = -122.4
        plot.view.psi   = 124.5
        plot.view.position = (5.3, 3.56, -4.3)

        tecplot.export.save_png('streamtrace_rod_contour.png', 600, supersample=3)

    .. figure:: /_static/images/streamtrace_rod_contour.png
        :width: 300px
        :figwidth: 300px
    """

    def __init__(self, streamtrace):
        super().__init__(streamtrace, sv.CONTOUR)

    @property
    def use_lighting_effect(self):
        """Enable lighting effect for streamtrace rod/ribbons.

        .. note::
            Setting `StreamtraceRodRibbonContour.use_lighting_effect` will also set
            the same value for `StreamtraceRodRibbonShade.use_lighting_effect`,
            and vice-versa.

        The lighting effect is set with `StreamtraceRodRibbonEffects.lighting_effect`, and may
        be one of `LightingEffect.Gouraud` or `LightingEffect.Paneled`.

        :type: `boolean <bool>`

        Example usage::

            >>> ribbon = plot.streamtraces.rod_ribbon
            >>> contour = ribbon.contour
            >>> contour.use_lighting_effect = True
            >>> ribbon.effects.lighting_effect = LightingEffect.Paneled
        """
        return self._get_style(bool, sv.USELIGHTINGEFFECT)

    @use_lighting_effect.setter
    def use_lighting_effect(self, value):
        self._set_style(bool(value), sv.USELIGHTINGEFFECT)

    @property
    def show(self):
        """Enable or disable contour flooding display.

        :type: `boolean <bool>`

        Example usage::

            >>> plot.streamtraces.rod_ribbon.contour.show = True
        """
        return self._get_style(bool, sv.SHOW)

    @show.setter
    def show(self, value):
        self._set_style(bool(value), sv.SHOW)

    @property
    def flood_contour_group_index(self):
        """The `Index` of the `ContourGroup` to use for flooding.

        :type: `Index` (zero-based index)

        This property sets and gets, by `Index`, the `ContourGroup` used for
        flooding. Changing style on this `ContourGroup` will affect all
        fieldmaps on the same `Frame` that use it.

        Example usage::

            >>> contour = plot.streamtraces.rod_ribbon.contour
            >>> contour.flood_contour_group_index = 0  # First contour group
        """
        return self._get_style(Index, sv.FLOODCOLORING)

    @flood_contour_group_index.setter
    def flood_contour_group_index(self, index):
        self._set_style(Index(index), sv.FLOODCOLORING)

    @property
    def flood_contour_group(self):
        """Contour group to use for flooding.

        :type: `ContourGroup`

        This property sets and gets the ContourGroup used for flooding.
        Changing style on this `ContourGroup` will affect all fieldmaps on
        the same `Frame` that use it.

        Example usage::

            >>> group = plot.contour(1)
            >>> contour = plot.streamtraces.rod_ribbon.contour
            >>> contour.flood_contour_group = group
        """
        return self.streamtrace.plot.contour(self.flood_contour_group_index)

    @flood_contour_group.setter
    def flood_contour_group(self, flood_contour_group):
        self.flood_contour_group_index = flood_contour_group.index


class StreamtraceRodRibbonShade(StreamtraceStyle):
    """Color and lighting display for rod/ribbons.

    .. code-block:: python
        :emphasize-lines: 25-29

        import os
        import tecplot
        from tecplot.constant import *

        examples_dir = tecplot.session.tecplot_examples_directory()
        datafile = os.path.join(examples_dir, 'SimpleData', 'DuctFlow.plt')
        dataset = tecplot.data.load_tecplot(datafile)

        frame = tecplot.active_frame()
        frame.plot_type = tecplot.constant.PlotType.Cartesian3D

        plot = frame.plot()
        plot.show_mesh = False
        plot.show_shade = False
        plot.show_edge = True
        plot.fieldmap(0).edge.edge_type = EdgeType.Creases

        plot.vector.u_variable_index = 3
        plot.vector.v_variable_index = 4
        plot.vector.w_variable_index = 5

        plot.show_streamtraces = True
        plot.streamtraces.show_paths = True

        ribbon = plot.streamtraces.rod_ribbon
        ribbon.shade.show = True
        ribbon.shade.color = Color.Blue
        ribbon.shade.use_lighting_effect = True
        ribbon.width = .03


        plot.streamtraces.add_rake(start_position=(1.5, 0, .45),
                                   end_position=(1.5, 1, 0),
                                   stream_type=Streamtrace.VolumeRibbon)

        tecplot.export.save_png('streamtrace_ribbon_shade.png', 600, supersample=3)

    .. figure:: /_static/images/streamtrace_ribbon_shade.png
        :width: 300px
        :figwidth: 300px
    """
    def __init__(self, streamtrace):
        super().__init__(streamtrace, sv.SHADE)

    @property
    def show(self):
        """Show shade attributes.

        :type: `boolean <bool>`

        Example usage::

            >>> plot.streamtraces.rod_ribbon.shade.show = True
        """
        return self._get_style(bool, sv.SHOW)

    @show.setter
    def show(self, value):
        self._set_style(bool(value), sv.SHOW)

    @property
    def color(self):
        """Shade color.

        :type: `Color`

        `Color.MultiColor` and `Color.RGBColor` coloring are not available.
        Use flooded contours for multi-color or RGB flooding.

        Example usage::

            >>> plot.streamtraces.rod_ribbon.shade.show = True
            >>> plot.streamtraces.rod_ribbon.shade.color = Color.Blue
        """
        return self._get_style(Color, sv.COLOR)

    @color.setter
    def color(self, value):
        self._set_style(Color(value), sv.COLOR)

    @property
    def use_lighting_effect(self):
        """Use lighting effect.

        When set to `True`, the lighting effect may be selected with the
        `SliceEffects.lighting_effect` attribute.

        .. note::
            Setting `SliceShade.use_lighting_effect` will also set
            the same value for `SliceContour.use_lighting_effect`,
            and vice-versa.

        :type: `Boolean <bool>`

        Example usage::

            >>> plot.streamtraces.rod_ribbon.shade.use_lighting_effect = True
            >>> plot.streamtraces.rod_ribbon.effects.lighting_effect = LightingEffect.Paneled
        """
        return self._get_style(bool, sv.USELIGHTINGEFFECT)

    @use_lighting_effect.setter
    def use_lighting_effect(self, value):
        self._set_style(bool(value), sv.USELIGHTINGEFFECT)


class StreamtraceRodRibbonEffects(StreamtraceStyle):
    """Controls how lighting and translucency interacts with streamtrace rods and ribbons.

    .. code-block:: python
        :emphasize-lines: 28-29

        import os
        import tecplot
        from tecplot.constant import *

        examples_dir = tecplot.session.tecplot_examples_directory()
        datafile = os.path.join(examples_dir, 'SimpleData', 'DuctFlow.plt')
        dataset = tecplot.data.load_tecplot(datafile)

        frame = tecplot.active_frame()
        frame.plot_type = tecplot.constant.PlotType.Cartesian3D

        plot = frame.plot()
        plot.show_mesh = False
        plot.show_shade = False
        plot.show_edge = True
        plot.fieldmap(0).edge.edge_type = EdgeType.Creases

        plot.show_mesh = False
        plot.show_shade = False

        plot.vector.u_variable_index = 3
        plot.vector.v_variable_index = 4
        plot.vector.w_variable_index = 5
        plot.show_streamtraces = True
        plot.streamtraces.rod_ribbon.width = .03
        plot.streamtraces.rod_ribbon.shade.color = Color.Green

        plot.streamtraces.rod_ribbon.effects.use_translucency = True
        plot.streamtraces.rod_ribbon.effects.surface_translucency = 80

        plot.streamtraces.add_rake(start_position=(1.5, 0, .45),
                                       end_position=(1.5, 1, 0),
                                       stream_type=Streamtrace.VolumeRibbon)

        tecplot.export.save_png('streamtrace_ribbon_effects.png', 600, supersample=3)

    .. figure:: /_static/images/streamtrace_ribbon_effects.png
        :width: 300px
        :figwidth: 300px
    """

    def __init__(self, streamtrace):
        super().__init__(streamtrace, sv.EFFECTS)

    @property
    def lighting_effect(self):
        """Get/set the lighting algorithm used when lighting
           streamtrace rods and ribbons.

        :type: `LightingEffect`

        Ribbon lighting effects must be enabled by setting
        `StreamtraceRodRibbonShade.use_lighting_effect` to `True` when
        setting this value.

        Note that setting `StreamtraceRodRibbonShade.use_lighting_effect` will also set
        this value for `ribbon contours <StreamtraceRodRibbonContour>`.

        There are two types of lighting effects: Paneled and Gouraud:

            * `Paneled`: Within each cell, the color assigned to each area by
                shading or contour flooding is tinted by a shade constant
                across the cell. This shade is based on the orientation
                of the cell relative to your 3D light source.
            * `Gouraud`: This offers smoother, more continuous shading than
                Paneled shading, but it also results in slower plotting
                and larger print files. `Gouraud` shading is not continuous
                across zone boundaries unless face neighbors are specified
                in the data. `Gouraud` shading is not available for finite
                element volume `Zone <data_access>` when blanking is active.
                The zone's lighting effect reverts to `Paneled`
                shading in this case.

        Example usage::

            >>> plot.streamtraces.rod_ribbon.shade.use_lighting_effect = True
            >>> plot.streamtraces.rod_ribbon.effects.lighting_effect = LightingEffect.Paneled
        """
        return self._get_style(LightingEffect, sv.LIGHTINGEFFECT)

    @lighting_effect.setter
    def lighting_effect(self, value):
        self._set_style(LightingEffect(value), sv.LIGHTINGEFFECT)

    @property
    def surface_translucency(self):
        """Surface translucency of the streamtraces ribbon.

        :type: `integer <int>`

        Surface translucency must be enabled by setting
        `StreamtraceRodRibbonEffects.use_translucency` = `True`
        when setting this value.

        Valid translucency values range from one (opaque) to 99 (translucent).

        Example usage::

            >>> plot.streamtraces.rod_ribbon.effects.use_translucency = True
            >>> plot.streamtraces.rod_ribbon.effects.surface_translucency = 20
        """
        return self._get_style(int, sv.SURFACETRANSLUCENCY)

    @surface_translucency.setter
    def surface_translucency(self, value):
        self._set_style(int(value), sv.SURFACETRANSLUCENCY)

    @property
    def use_translucency(self):
        """Enable surface translucency.

        :type: `boolean <bool>`

        The surface translucency value can be changed by setting
        `StreamtraceRodRibbonEffects.surface_translucency`.

        Example usage::

            >>> plot.streamtraces.rod_ribbon.effects.use_translucency = True
            >>> plot.streamtraces.rod_ribbon.effects.surface_translucency = 20
        """
        return self._get_style(bool, sv.USETRANSLUCENCY)

    @use_translucency.setter
    def use_translucency(self, value):
        self._set_style(bool(value), sv.USETRANSLUCENCY)


class StreamtraceRodRibbon(StreamtraceStyle):
    """Get/Set streamtrace rod/ribbon attributes.

    The `StreamtraceRodRibbon` class allows you to query and set attributes
    of streamtrace rod/ribbon types:

    * `Streamtrace.SurfaceRibbon`
    * `Streamtrace.VolumeRibbon`
    * `Streamtrace.VolumeRod`

    In addition to attributes common to all rod/ribbon
    streamtrace types such as `width <StreamtraceRodRibbon.width>`,
    some attributes are further divided into subcategories:

    * `Rod/ribbon mesh <StreamtraceRodRibbonMesh>`
    * `Rod/ribbon contour <StreamtraceRodRibbonContour>`
    * `Rod/ribbon shade <StreamtraceRodRibbonShade>`
    * `Rod/ribbon effects <StreamtraceRodRibbonEffects>`

    .. note::
        To change the color of streamtrace rods/ribbons, set
        `StreamtraceRodRibbonShade.color`.

    .. code-block:: python
        :emphasize-lines: 25-35

        import os
        import tecplot
        from tecplot.constant import *

        examples_dir = tecplot.session.tecplot_examples_directory()
        datafile = os.path.join(examples_dir, 'SimpleData', 'DuctFlow.plt')
        dataset = tecplot.data.load_tecplot(datafile)

        frame = tecplot.active_frame()
        frame.plot_type = tecplot.constant.PlotType.Cartesian3D

        plot = frame.plot()
        plot.show_mesh = False
        plot.show_shade = False
        plot.show_edge = True
        plot.fieldmap(0).edge.edge_type = EdgeType.Creases
        plot.contour(0).variable = dataset.variable(3)
        plot.contour(0).levels.reset_to_nice()

        plot.vector.u_variable_index = 3
        plot.vector.v_variable_index = 4
        plot.vector.w_variable_index = 5

        plot.show_streamtraces = True
        plot.streamtraces.rod_ribbon.width = .03
        plot.streamtraces.rod_ribbon.contour.show = True

        plot.streamtraces.add_rake(start_position=(1.5, 0.1, .4),
                                   end_position=(1.5, .9, 0.1),
                                   stream_type=Streamtrace.VolumeRibbon,
                                   num_seed_points=3)
        plot.streamtraces.add_rake(start_position=(1.5, 0.1, 0.1),
                                   end_position=(1.5, .9, .4),
                                   stream_type=Streamtrace.VolumeRod,
                                   num_seed_points=4)

        tecplot.export.save_png('streamtrace_ribbon.png', 600, supersample=3)

    .. figure:: /_static/images/streamtrace_ribbon.png
        :width: 300px
        :figwidth: 300px

    """
    def __init__(self, streamtrace):
        super().__init__(streamtrace, sv.RODRIBBON)
        self.plot = streamtrace.plot

    @property
    def mesh(self):
        """Streamtraces rod/ribbon mesh attributes.

        :type: `StreamtraceRodRibbonMesh`

        Example usage::

            >>> plot.streamtraces.rod_ribbon.mesh.show = True
        """
        return StreamtraceRodRibbonMesh(self)

    @property
    def contour(self):
        """Streamtraces rod/ribbon contour attributes.

        :type: `StreamtraceRodRibbonContour`

        Example usage::

            >>> plot.streamtraces.rod_ribbon.contour.show = True
        """
        return StreamtraceRodRibbonContour(self)

    @property
    def shade(self):
        """Streamtraces rod/ribbon color and lighting attributes.

        :type: `StreamtraceRodRibbonShade`

        Example usage::

            >>> plot.streamtraces.rod_ribbon.shade.color = Color.Magenta
        """
        return StreamtraceRodRibbonShade(self)

    @property
    def effects(self):
        """Streamtraces rod/ribbon effects.

        :type: `StreamtraceRodRibbonEffects`

        Example usage::

            >>> plot.streamtraces.rod_ribbon.effects.use_translucency = True
        """
        return StreamtraceRodRibbonEffects(self)

    @property
    def width(self):
        """Rod/ribbon width in grid units.

        :type: `float`

        Example usage::

            >>> plot.streamtraces.rod_ribbon.width = 0.01
        """
        return self._get_style(float, sv.WIDTH)

    @width.setter
    def width(self, value):
        self._set_style(float(value), sv.WIDTH)

    @property
    def num_rod_points(self):
        """Number of rod points.

        :type: `integer <int>`, valid range 3-100

        Volume rods have a polygonal cross-section; this parameter tells
        |Tecplot 360| what that cross-section should be.
        (Three is an equilateral triangle, four is a square,
        five is a regular pentagon, and so on.) If you want two sets
        of volume rods with different cross-sections, you must create one
        set and then extract the set as a zone, then configure a new
        set of streamtraces with the second cross-section.

        Example usage::

            >>> plot.streamtraces.rod_ribbon.num_rod_points = 10
        """
        return self._get_style(int, sv.NUMRODPOINTS)

    @num_rod_points.setter
    def num_rod_points(self, value):
        self._set_style(int(value), sv.NUMRODPOINTS)


class Streamtraces(session.Style):
    """Streamtrace attributes for the plot.

    A streamtrace is the path traced by a massless particle placed at an
    arbitrary location in a steady-state vector field.
    Streamtraces may be used to illustrate the nature of the vector
    field flow in a particular region of the `Plot`.

    Note:
        Because streamtraces are dependent upon a vector field, you must
        define vector components before creating streamtraces.
        However, it is not necessary to activate the Vector zone layer to
        use streamtraces.

    .. code-block:: python
        :emphasize-lines: 22-29

        import os
        import tecplot
        from tecplot.constant import *

        examples_dir = tecplot.session.tecplot_examples_directory()
        datafile = os.path.join(examples_dir, 'SimpleData', 'Eddy.plt')
        dataset = tecplot.data.load_tecplot(datafile)

        frame = tecplot.active_frame()
        frame.plot_type = tecplot.constant.PlotType.Cartesian3D

        plot = frame.plot()
        plot.fieldmap(0).surfaces.surfaces_to_plot = SurfacesToPlot.BoundaryFaces
        plot.show_mesh = True
        plot.show_shade = False

        plot.vector.u_variable_index = 4
        plot.vector.v_variable_index = 5
        plot.vector.w_variable_index = 6
        plot.show_streamtraces = True

        streamtraces = plot.streamtraces
        streamtraces.color = Color.Blue

        streamtraces.show_arrows = True
        streamtraces.arrowhead_size = 2
        streamtraces.step_size = .25
        streamtraces.line_thickness = .2
        streamtraces.max_steps = 100

        streamtraces.add_rake(start_position=(45.49, 15.32, 59.1),
                              end_position=(48.89, 53.2, 47.6),
                              stream_type=Streamtrace.SurfaceLine,
                              num_seed_points=4)


        tecplot.export.save_png('streamtrace_example.png', 600, supersample=3)

    .. figure:: /_static/images/streamtrace_example.png
        :width: 300px
        :figwidth: 300px
    """

    def __init__(self, plot):
        super().__init__(sv.STREAMATTRIBUTES, uniqueid=plot.frame.uid)
        self.plot = plot

    @property
    def rod_ribbon(self):
        """Streamtrace rod/ribbon attributes.

        :type: `StreamtraceRodRibbon`

        Example usage::

            >>> streamtraces.rod_ribbon.mesh.show = True
        """
        return StreamtraceRodRibbon(self)

    @property
    def timing(self):
        """Streamtraces timing attributes.

        :type: `StreamtraceTiming`

        Example usage::

            >>> timing = plot.streamtraces.timing
            >>> timing.start = 0.01
        """
        return StreamtraceTiming(self)

    @property
    def termination_line(self):
        """Streamtraces termination line attributes.

        A streamtrace termination line is a polyline that terminates any
        streamtraces that cross it. The termination line is useful for stopping
        streamtraces before they spiral or stall.

        :type: `StreamtraceTerminationLine`

        Example usage::

            >>> term_line = plot.streamtraces.termination_line
            >>> term_line.show = True
        """
        return StreamtraceTerminationLine(self)

    @property
    def show_dashes(self):
        """Display streamtrace dashes.

        The lengths of the dashes and the spaces between the dashes are
        controlled by the value of `StreamtraceTiming.delta`. Set the
        `Streamtraces.dash_skip` attribute to control the number of
        time deltas used for the "off" sections of the streamtraces.

        :type: `boolean <bool>`

        Example usage::

            >>> plot.streamtraces.show_dashes = True
        """
        return self.timing._show_dashes

    @show_dashes.setter
    def show_dashes(self, value):
        self.timing._show_dashes = value

    @property
    def show_markers(self):
        """Display streamtrace markers.

        :type: `boolean <bool>`

        Stream markers are only available for surface and volume
        type streamlines.

        You may also specify the `size <Streamtraces.marker_size>`,
        `color <Streamtraces.marker_color>`, and
        `shape <Streamtraces.marker_symbol>` of the markers.

        Example usage::

            >>> plot.streamtraces.show_markers = True

        """
        return self.timing._show_markers

    @show_markers.setter
    def show_markers(self, value):
        self.timing._show_markers = value

    @property
    def marker_color(self):
        """`Color` of the streamline markers.

        :type: `Color` or `ContourGroup`

        Streamtrace markers can be a solid color or be colored by a
        `ContourGroup` as obtained through the ``plot.contour`` property.

        Example usage::

            >>> plot.streamtraces.marker_color = Color.Blue
        """

        return self.timing._marker_color

    @marker_color.setter
    def marker_color(self, value):
        self.timing._marker_color = value

    @property
    def marker_size(self):
        """Size of streamline markers.

         :type: `float`

         Example usage::

            >>> plot.streamtraces.marker_size = 1.1
         """
        return self.timing._marker_size

    @marker_size.setter
    def marker_size(self, value):
        self.timing._marker_size = value

    @property
    def dash_skip(self):
        """Number of time deltas used for the "off" sections of the streamlines.

        .. note::
            The ``dash_skip`` value must be greater than 0.

        :type: `integer <int>`

        Example usage::

            >>> plot.streamtraces.dash_skip = 2
        """

        return int(self.timing._dash_skip)

    @dash_skip.setter
    def dash_skip(self, value):
        self.timing._dash_skip = value

    @property
    def marker_symbol_type(self):
        """The `SymbolType` to use for stream markers.

        :type: `SymbolType`

        This sets the active symbol type for streamtrace markers.
        Use `Streamtraces.marker_symbol` to access the symbol::

            >>> from tecplot.constant import SymbolType
            >>> streamtrace = plot.streamtraces
            >>> streamtraces.marker_symbol_type = SymbolType.Text
            >>> symbol = streamtraces.marker_symbol(SymbolType.Text)
            >>> symbol.text = 'a'
        """
        return self.timing._marker_symbol_type

    @marker_symbol_type.setter
    def marker_symbol_type(self, value):
        self.timing._marker_symbol_type = value

    def marker_symbol(self, symbol_type=None):
        """Returns a streamline symbol style object.

        Parameters:
            symbol_type (`SymbolType`, optional): The type of symbol to return.
                By default, this will return the active marker symbol type
                which is obtained from `Streamtraces.marker_symbol_type`.


        Returns: `TextSymbol` or `GeometrySymbol`, depending on `marker_symbol_type`

        Example usage::

            >>> from tecplot.constant import SymbolType
            >>> streamtrace = plot.streamtraces
            >>> streamtraces.marker_symbol_type = SymbolType.Text
            >>> symbol = streamtraces.marker_symbol(SymbolType.Text)
            >>> symbol.text = 'a'
        """
        return self.timing._marker_symbol(symbol_type)

    @property
    def show_arrows(self):
        """Display arrowheads along all streamlines.

        :type: `boolean <bool>`

        Example usage::

            >>> plot.streamtraces.show_arrows = True
        """
        return self._get_style(bool, sv.ADDARROWS)

    @show_arrows.setter
    def show_arrows(self, value):
        self._set_style(bool(value), sv.ADDARROWS)

    @property
    def arrowhead_size(self):
        """Arrowhead size as a percentage of frame height.

        :type: `float`

        Recommend values are one of 1, 3, 5, 8, or 12.

        Example usage::

            >>> plot.streamtraces.show_arrows = True
            >>> plot.streamtraces.arrowhead_size = 1.0
        """
        return self._get_style(float, sv.ARROWHEADSIZE)

    @arrowhead_size.setter
    def arrowhead_size(self, value):
        self._set_style(float(value), sv.ARROWHEADSIZE)

    @property
    def arrowhead_spacing(self):
        """Distance between arrowheads in terms of Y-frame units.

        :type: `float`

        For example, a value of 10 will space arrowheads approximately
        ten percent of the frame height apart from each other along each
        streamline.

        Example usage::

            >>> plot.streamtraces.show_arrows = True
            >>> plot.streamtraces.arrowhead_spacing = 10
        """
        return self._get_style(float, sv.ARROWHEADSPACING)

    @arrowhead_spacing.setter
    def arrowhead_spacing(self, value):
        self._set_style(float(value), sv.ARROWHEADSPACING)

    @property
    def step_size(self):
        """Maximum fraction of the distance across a cell that a streamtrace
        moves in one step.

        :type: `float`

        The step size is the maximum fraction of the distance across a cell
        that a streamtrace moves in one step. A streamtrace adjusts its
        step size between `step_size` and `min_step_size`, depending
        on local curvature of the streamtrace.

        A typical value (and the default) is **0.25**, which results in
        four integration steps through each cell or element.
        The value for Step Size affects the accuracy of the integration.

        .. warning::
            Setting step size too small can result in round-off errors,
            while setting it too large can result in truncation
            errors and missed cells.

        Example usage::

            >>> plot.streamtraces.step_size = .25
        """
        return self._get_style(float, sv.CELLFRACTION)

    @step_size.setter
    def step_size(self, value):
        self._set_style(float(value), sv.CELLFRACTION)

    @property
    def color(self):
        """Color of streamtraces line (not rods or ribbons).

        :type: `Color` or `ContourGroup`

        Streamtraces can be a solid color or be colored by a
        `ContourGroup` as obtained through the ``plot.contour`` property.

        Example usage::

            >>> plot.streamtraces.color = Color.Red
        """
        return color_spec(self._get_style(Color, sv.COLOR),
                          self.plot)

    @color.setter
    def color(self, value):
        self._set_style(color_spec(value), sv.COLOR)

    @property
    def line_thickness(self):
        """Streamtrace line thickness.

        :type: `float`

        Line thickness as a percentage of the frame height for 2D lines,
        or a percentage of the median axis length for 3D surface lines and
        volume lines.

        Suggested values are .02, .1, .4, .8, 1.5

        Example usage::

            >>> plot.streamtraces.line_thickness = 1.1
        """
        return self._get_style(float, sv.LINETHICKNESS)

    @line_thickness.setter
    def line_thickness(self, value):
        self._set_style(float(value), sv.LINETHICKNESS)

    @property
    def max_steps(self):
        """Maximum number of steps before the streamtrace is terminated.

        :type: `integer <int>`

        `max_steps` prevents streamtraces from spinning forever in a vortex,
        or from wandering into a region where the vector components are very
        small, very random, or both.

        If a small `step_size` is selected, the `max_steps`
        should be a large value.

        Example usage::

            >>> plot.streamtraces.max_steps = 5000
        """
        return self._get_style(int, sv.MAXSTEPS)

    @max_steps.setter
    def max_steps(self, value):
        self._set_style(int(value), sv.MAXSTEPS)

    @property
    def min_step_size(self):
        """Smallest step size to use as a percentage of cell distance.

        A typical minimum step size value is 0.00001, which is the default.

        :type: `float`

        .. Warning::
            Setting this too small results in integration problems. Setting this
            greater than or equal to the `step_size` results in a constant step
            size.

        Example usage::

            >>> plot.streamtraces.min_step_size = .0002
        """

        return self._get_style(float, sv.MINCELLFRACTION)

    @min_step_size.setter
    def min_step_size(self, value):
        self._set_style(float(value), sv.MINCELLFRACTION)

    @property
    def obey_source_zone_blanking(self):
        """Obey source zone blanking.

        :type: `boolean <bool>`

        When `True`, streamtraces are generated for non-blanked regions only.
        When `False`, streamtraces are generated for both blanked and
        unblanked regions.

        Example usage::

            >>> plot.streamtraces.obey_source_zone_blanking = True
        """
        return self._get_style(bool, sv.OBEYSOURCEZONEBLANKING)

    @obey_source_zone_blanking.setter
    def obey_source_zone_blanking(self, value):
        self._set_style(bool(value), sv.OBEYSOURCEZONEBLANKING)

    @property
    def show_paths(self):
        """Draw streamtrace paths (lines, ribbons, or rods).

        :type: `boolean <bool>`

        A streamtrace path may be a line, ribbon or rod.

        Example usage::

            >>> plot.streamtraces.show_paths = True

        See also `Streamtraces.show_markers`
        """
        return self._get_style(bool, sv.SHOWPATHS)

    @show_paths.setter
    def show_paths(self, value):
        self._set_style(bool(value), sv.SHOWPATHS)

    def add_on_zone_surface(self, stream_type, zones=None, num_seed_points=10,
                            direction=StreamDir.Both):
        """Add streamtraces to one or more zones in a plot.

        The plot type must be either `Cartesian2D` or `Cartesian3D`.

        .. note:: For volume zones the streamtraces are propagated from the surfaces of the volume.

        Parameters:
            stream_type: (`Streamtrace`): Type of streamtraces to add.

            zones (`set` of `integers <int>`, optional):
                Set of `Zones <data_access>` on which to add streamtraces. If
                `None`, then streamtraces will be added to the currently
                active zones.

            num_seed_points: (`integer <int>`, optional):
                Number of seed points for distributing along a rake or on
                defined surfaces.

            direction: (`StreamDir`, optional): Direction of propagation
                of the streamtraces being added.

        .. code-block:: python

            import tecplot
            from tecplot.constant import *
            import os

            examples_dir = tecplot.session.tecplot_examples_directory()
            datafile = os.path.join(examples_dir, 'OneraM6wing', 'OneraM6_SU2_RANS.plt')
            dataset = tecplot.data.load_tecplot(datafile)

            frame = tecplot.active_frame()
            frame.plot_type = tecplot.constant.PlotType.Cartesian3D

            plot = frame.plot()

            plot.vector.u_variable_index = 4
            plot.vector.v_variable_index = 5
            plot.vector.w_variable_index = 6
            plot.show_streamtraces = True

            plot.streamtraces.add_on_zone_surface(
                        # To add streamtraces to the currently active zones,
                        # pass zones=None
                        zones=[1],  # Add streamtraces on 2nd zone only
                        stream_type=Streamtrace.SurfaceLine,
                        num_seed_points=200)

            tecplot.export.save_png('streamtrace_add_on_zone_surface.png', 600, supersample=3)

        .. figure:: /_static/images/streamtrace_add_on_zone_surface.png
            :width: 300px
            :figwidth: 300px

        """
        if __debug__ and zones is not None:
            sdk_version_required = (2017, 2)
            if version.sdk_version_info < sdk_version_required:
                raise TecplotOutOfDateEngineError(
                    sdk_version_required,
                    'Streamtraces.add_on_zone_surface() not supported.')

        if zones is None:
            self._add(stream_type=stream_type,
                      distribution_region=
                      DistributionRegion.SurfacesOfActiveZones,
                      stream_direction=direction,
                      num_points=num_seed_points)
        else:
            with IndexSet(zones) as zone_set:
                self._add(stream_type=stream_type,
                          distribution_region=
                          DistributionRegion.SurfacesOfSuppliedZones,
                          stream_direction=direction,
                          num_points=num_seed_points, zones=zone_set)

    def add_rake(self, start_position, end_position, stream_type,
                 num_seed_points=10, direction=StreamDir.Both):
        """Add a rake of streamtraces to the plot of the current frame.

        The plot type must be either `Cartesian2D` or `Cartesian3D`.

        Parameters:
            start_position: (2- or 3- `tuple` of `floats <float>`):
                Pass a 2-`tuple` of `float` for a
                `Cartesian2DFieldPlot`, or a 3-`tuple` of `float` for a
                `Cartesian3DFieldPlot`.

            end_position: (2- or 3- `tuple` of `floats <float>`):
                Pass a 2-`tuple` of `float` for a
                `Cartesian2DFieldPlot`, or a 3-`tuple` of `float` for a
                `Cartesian3DFieldPlot`.

            stream_type: (`Streamtrace`): Type of streamtraces to add.

            num_seed_points: (`integer <int>`, optional):
                Number of seed points for distributing along a rake or on
                defined surfaces.

            direction: (`StreamDir`, optional): Direction of propagation
                of the streamtraces being added.

        .. code-block:: python
            :emphasize-lines: 23-25

            import tecplot
            from tecplot.constant import *
            import os

            examples_dir = tecplot.session.tecplot_examples_directory()
            datafile = os.path.join(examples_dir, 'SimpleData', 'Eddy.plt')
            dataset = tecplot.data.load_tecplot(datafile)

            frame = tecplot.active_frame()
            frame.plot_type = tecplot.constant.PlotType.Cartesian3D

            plot = frame.plot()
            plot.fieldmap(0).surfaces.surfaces_to_plot = SurfacesToPlot.BoundaryFaces
            plot.show_mesh = True
            plot.show_shade = False

            plot.vector.u_variable_index = 4
            plot.vector.v_variable_index = 5
            plot.vector.w_variable_index = 6
            plot.show_streamtraces = True

            streamtraces = plot.streamtraces
            streamtraces.add_rake(start_position=[.5, .5, .5],
                                  end_position=[20, 20, 20],
                                  stream_type=Streamtrace.VolumeLine)
            tecplot.export.save_png('streamtrace_add_rake.png', 600, supersample=3)

        .. figure:: /_static/images/streamtrace_add_rake.png
            :width: 300px
            :figwidth: 300px

        """

        self._add(stream_type, DistributionRegion.Rake, direction,
                  num_seed_points, start_position, end_position)

    def add(self, seed_point, stream_type, direction=StreamDir.Both):
        """Add a single streamtrace to the plot of the current frame.

        The plot type must be either `Cartesian2D` or `Cartesian3D`.

        Parameters:
            seed_point: (2- or 3- `tuple` of `floats <float>`):
                Pass a 2-`tuple` of `float` for a
                `Cartesian2DFieldPlot`, or a 3-`tuple` of `float` for a
                `Cartesian3DFieldPlot`.

            stream_type: (`Streamtrace`): Type of streamtraces to add.

            direction: (`StreamDir`, optional): Direction of propagation
                of the streamtraces being added.

        .. note::
            *stream_type* is automatically set to `Streamtrace.SurfaceLine`
            if the plot type is `Cartesian2DFieldPlot`. The only stream
            type available for 2D plots is `Streamtrace.SurfaceLine`.

        Raises:
            `TecplotSystemError`: The streamtraces could not be added.

        .. code-block:: python
            :emphasize-lines: 42

            import os
            import tecplot
            from tecplot.constant import *
            import numpy as np

            examples_dir = tecplot.session.tecplot_examples_directory()
            datafile = os.path.join(examples_dir, 'SimpleData', 'DuctFlow.plt')
            dataset = tecplot.data.load_tecplot(datafile)

            frame = tecplot.active_frame()
            frame.plot_type = tecplot.constant.PlotType.Cartesian3D

            plot = frame.plot()
            plot.contour(0).variable = dataset.variable('P(N/m2)')
            plot.contour(0).levels.reset_to_nice()
            plot.contour(0).legend.show = False

            plot.vector.u_variable = dataset.variable('U(M/S)')
            plot.vector.v_variable = dataset.variable('V(M/S)')
            plot.vector.w_variable = dataset.variable('W(M/S)')

            # Goal: create a grid of 12 stream trace ribbons
            x_slice_location = .79
            y_start = .077
            y_end = .914
            z_start = .052
            z_end = .415

            num_left_right_slices = 4  # Must be >= 2
            num_top_bottom_slices = 3  # Must be >= 2

            plot.show_streamtraces = True
            streamtraces = plot.streamtraces
            streamtraces.show_paths = True

            rod = streamtraces.rod_ribbon
            rod.width = .03
            rod.contour.show = True


            for y in np.linspace(y_start, y_end, num=num_left_right_slices):
                for z in np.linspace(z_start, z_end, num=num_top_bottom_slices):
                    streamtraces.add([x_slice_location,y,z], Streamtrace.VolumeRibbon)

            tecplot.export.save_png('streamtrace_add_xyz.png', 600, supersample=3)

        .. figure:: /_static/images/streamtrace_add_xyz.png
            :width: 300px
            :figwidth: 300px

        """

        self._add(stream_type=stream_type,
                  distribution_region=DistributionRegion.Point,
                  stream_direction=direction,
                  start_position=seed_point,
                  end_position=seed_point if stream_type in (
                     Streamtrace.SurfaceRibbon, Streamtrace.VolumeRibbon,
                     Streamtrace.VolumeRod) else None)

    @lock()
    def _add(self, stream_type, distribution_region, stream_direction,
             num_points=None,
             start_position=None,
             end_position=None,
             zones=None):

        def _assign_position(arg_list, point_ordinal, value):
            try:
                if __debug__:
                    frame = self.plot.frame
                    if frame.plot_type == PlotType.Cartesian2D and (
                                len(value) != 2):
                        raise TecplotTypeError(
                                '[x,y] position for streamtrace '
                                'requires 2D plot type.')
                    elif frame.plot_type == PlotType.Cartesian3D and (
                                len(value) != 3):
                        raise TecplotTypeError(
                                '[x,y] position for streamtrace '
                                'requires 2D plot type.')

                arg_list['X' + point_ordinal], arg_list['Y' + point_ordinal] = (
                    float(value[0]), float(value[1]))
                if len(value) == 3:
                    arg_list['Z' + point_ordinal] = float(value[2])
            except TypeError:
                raise TecplotTypeError('streamtrace position must be a '
                                       '2- or 3- tuple of floats.')

        with ArgList() as arglist:
            arglist[sv.STREAMTYPE] = stream_type
            arglist[sv.DISTRIBUTIONREGION] = distribution_region
            arglist[sv.STREAMDIRECTION] = stream_direction
            if zones is not None:
                arglist[sv.ZONESET] = zones

            if num_points is not None:
                arglist[sv.NUMPTS] = int(num_points)
            if start_position is not None:
                _assign_position(arglist, '1', start_position)
            if end_position is not None:
                _assign_position(arglist, '2', end_position)

            with self.plot.frame.activated():
                if not _tecutil.StreamtraceAddX(arglist):
                    raise TecplotSystemError()

    @lock()
    def delete_all(self):
        """Delete all streamtraces for the current plot type.

        2D and 3D streamtraces are independent of each other.

        If the plot type is `Cartesian2D`, all 2D streamtraces are deleted.
        If the plot type is `Cartesian3D`, all 3D streamtraces are deleted.

        Raises:
            `TecplotSystemError`: The streamtraces could not be deleted.

        Example usage::

            >>> plot.streamtraces.delete_all()
        """

        with self.plot.frame.activated():
            if not _tecutil.StreamtraceDeleteAll():
                raise TecplotSystemError()

    @lock()
    def delete_range(self, range_start, range_end):
        """Delete a range of streamtraces.

        Parameters:
            range_start: (`integer <int>`): 0-based start streamtrace number to delete.

            range_end: (`integer <int>`): 0-based end streamtrace number to delete.

        Raises:
            `TecplotSystemError`: The streamtraces in the range could not be deleted.

        Example usage::

            >>> # Delete the first 100 streamtraces
            >>> plot.streamtraces.delete_range(0, 99)
        """

        with self.plot.frame.activated():
            if not _tecutil.StreamtraceDeleteRange(range_start + 1, range_end + 1):
                raise TecplotSystemError()

    @lock()
    def set_termination_line(self, line_points):
        """Set the position of the termination line for streamtraces.

        Parameters:
            line_points: (array of `float` `tuple`) Points of the termination line.

        Raises:
            `TecplotSystemError`: Termination line could not be set.

        Example usage::

            >>> # Multi-segment line between points (0,0)-(5,8)-(3,6)
            >>> line_points = [(0, 0), (5, 8), (3,6)]
            >>> plot.streamtraces.set_termination_line(line_points)
        """

        num_points = len(line_points)

        #
        # __mul__() is used below because the alternative:
        #  (c_double * num_points)(*P[0]... causes a lint warning in PyCharm
        #
        x_points = (ctypes.c_double.__mul__(num_points)
                    )(*[P[0] for P in line_points])
        y_points = (ctypes.c_double.__mul__(num_points)
                    )(*[P[1] for P in line_points])

        with self.plot.frame.activated():
            if not _tecutil.StreamtraceSetTermLine(
                    len(line_points),
                    x_points,
                    y_points):
                raise TecplotSystemError()

    @property
    def count(self):
        """Query the number of active streamtraces for the current plot type.

        Returns:
            `integer <int>`

        .. note:: This property is read-only.

        >>> num_active_streamtraces = plot.streamtraces.count

        """
        with self.plot.frame.activated():
            return _tecutil.StreamtraceGetCount()

    def position(self, stream_number):
        """Query the starting position of a streamtrace.

        Parameters:
            stream_number: (`integer <int>`): 0-based stream number to query.

        Returns:
            `tuple` of `floats <float>`

        Get the position of streamtrace number 3::

            >>> position = plot.streamtraces.position(2) # Note: 0-based
            >>> position.x  # == position[0]
            0.1
            >>> position.y  # == position[1]
            0.2
            >>> position.z  # == position[2]
            0.3
            """

        with self.plot.frame.activated():
            position = _tecutil.StreamtraceGetPos(stream_number + 1)
            return _XYZ(position[0], position[1], position[2])

    def streamtrace_type(self, stream_number):
        """Query the type of a streamtrace by streamtrace number.

        Parameters:
            stream_number: (`integer <int>`): 0-based stream number to query.

        Returns:
            `Streamtrace`

        Get the type of streamtrace 3. Note 0-based stream number::

            >>> streamtrace_type = plot.streamtraces.streamtrace_type(2) # streamtrace 3
            >>> streamtrace_type
            <Streamtrace.VolumeLine: 2>
        """

        with self.plot.frame.activated():
            return Streamtrace(
                _tecutil.StreamtraceGetType(stream_number+1))

    @property
    def has_terminating_line(self):
        """Determine if the streamtraces have the terminating line.

        .. note:: This property is read-only.

        Returns:
            `boolean <bool>`. `True` if the streamtraces have the terminating
            line, `False` otherwise.

        Example usage::

            >>> has_terminating_line = plot.streamtraces.has_terminating_line

        """
        with self.plot.frame.activated():
            with lock():
                return _tecutil.StreamtraceHasTermLine()

    @property
    def are_active(self):
        """Determine if there are active streamtraces in the current plot type.

        .. note:: This property is read-only.

        Returns:
            `boolean <bool>`. `True` if there are active streamtraces
            in the current plot type.

        Example usage::

            >>> streamtraces_are_active = plot.streamtraces.are_active
        """
        with self.plot.frame.activated():
            return _tecutil.QueryStreamtracesAreActive()
