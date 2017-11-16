from builtins import super, int

from contextlib import contextmanager
from fnmatch import fnmatch

from ..tecutil import _tecutil, _tecutil_connector
from ..constant import *
from ..exception import *
from .. import session, version
from ..legend import LineLegend
from ..tecutil import Index, IndexSet, flatten_args, lock, lock_attributes, sv
from .axes import (Cartesian2DFieldAxes, Cartesian3DFieldAxes, SketchAxes,
                   PolarLineAxes, XYLineAxes)
from .contour import ContourGroup
from .fieldmap import Cartesian2DFieldmap, Cartesian3DFieldmap
from .isosurface import IsosurfaceGroup
from .linemap import PolarLinemap, XYLinemap
from .scatter import Scatter
from .slice import SliceGroup
from .streamtrace import StreamtraceRodRibbon, Streamtraces
from .vector import Vector2D, Vector3D
from .view import Cartesian2DView, Cartesian3DView, LineView, PolarView


class Plot(session.Style):
    def __init__(self, frame, *svargs):
        self.frame = frame
        super().__init__(*svargs, uniqueid=frame.uid)

    def __eq__(self, that):
        return isinstance(that, type(self)) and self.frame == that.frame

    def __ne__(self, that):
        return not (self == that)

    @contextmanager
    def activated(self):
        """Context to ensure this plot is active.

        Example usage::

            >>> from tecplot.constant import PlotType
            >>> frame = tecplot.active_frame()
            >>> frame.plot_type = PlotType.XYLine  # set active plot type
            >>> plot = frame.plot(PlotType.Cartesian3D)  # get inactive plot
            >>> print(frame.plot_type)
            PlotType.XYLine
            >>> with plot.activated():
            ...     print(frame.plot_type)  # 3D plot temporarily active
            PlotType.Cartesian3D
            >>> print(frame.plot_type)  # original plot type restored
            PlotType.XYLine
        """
        with self.frame.activated():
            orig_plot = self.frame.plot()
            try:
                self.activate()
                yield self
            finally:
                orig_plot.activate()


class SketchPlot(Plot):
    """A plot space with no data attached.

    .. code-block:: python
        :emphasize-lines: 5,8-9

        import tecplot as tp
        from tecplot.constant import PlotType

        frame = tp.active_frame()
        plot = frame.plot(PlotType.Sketch)

        frame.add_text('Hello, World!', (36, 50), size=34)
        plot.axes.x_axis.show = True
        plot.axes.y_axis.show = True

        tp.export.save_png('plot_sketch.png', 600, supersample=3)

    ..  figure:: /_static/images/plot_sketch.png
        :width: 300px
        :figwidth: 300px
    """

    def activate(self):
        """Make this the active plot type on the parent frame.

        Example usage::

            >>> from tecplot.constant import PlotType
            >>> plot = frame.plot(PlotType.Sketch)
            >>> plot.activate()
        """
        self.frame.plot_type = PlotType.Sketch

    @property
    def axes(self):
        """Axes (x and y) for the sketch plot.

        :type: `SketchAxes`

        Example usage::

            >>> from tecplot.constant import PlotType
            >>> frame.plot_type = PlotType.Sketch
            >>> frame.plot().axes.x_axis.show = True
        """
        return SketchAxes(self)


class FieldPlot(Plot):
    """Plot containing data associated with style through fieldmaps.

    .. code-block:: python
        :emphasize-lines: 8-12

        from os import path
        import tecplot as tp
        from tecplot.constant import PlotType

        examples_dir = tp.session.tecplot_examples_directory()
        infile = path.join(examples_dir, 'SimpleData', 'F18.plt')
        dataset = tp.data.load_tecplot(infile)

        frame = tp.active_frame()
        plot = frame.plot(PlotType.Cartesian3D)
        plot.activate()
        plot.show_contour = True
        plot.use_translucency = True
        plot.contour(0).variable = dataset.variable('S')

        # save image to file
        tp.export.save_png('plot_field.png', 600, supersample=3)

    ..  figure:: /_static/images/plot_field.png
        :width: 300px
        :figwidth: 300px
    """
    def __init__(self, frame):
        super().__init__(frame, sv.FIELDLAYERS)

    def contour(self, index):
        """Plot-local `ContourGroup` style control.

        :type: `ContourGroup`

        Example usage::

            >>> contour = frame.plot().contour(0)
            >>> contour.colormap_name = 'Magma'
        """
        return ContourGroup(index, self)

    @property
    def streamtraces(self):
        """Plot-local `streamtrace <Streamtraces>` attributes.

        :type: `Streamtraces`

        Example usage::

            >>> streamtraces = frame.plot().streamtraces
            >>> streamtraces.color = Color.Blue
        """
        return Streamtraces(self)

    def slice(self, index):
        """Plot-local `slice <SliceGroup>` style control.

        :type: `SliceGroup`

        Example usage::

            >>> slice_0 = frame.plot().slice(0)
            >>> slice_0.mesh.color = Color.Blue
        """
        return SliceGroup(index, self)

    def isosurface(self, index):
        """Plot-local `isosurface <IsosurfaceGroup>` settings.

        :type: `IsosurfaceGroup`

        Example usage::

            >>> isosurface_0 = frame.plot().isosurface(0)
            >>> isosurface_0.mesh.color = Color.Blue
        """
        return IsosurfaceGroup(index, self)

    @property
    def scatter(self):
        """Plot-local `Scatter` style control.

        :type: `Scatter`

        Example usage::

            >>> scatter = frame.plot().scatter
            >>> scatter.variable = dataset.variable('P')
        """
        return Scatter(self)

    @property
    def show_contour(self):
        """Enable contours for this plot.

        :type: `bool`

        Example usage::

            >>> frame.plot().show_contour = True
        """
        return self._get_style(bool, sv.SHOWCONTOUR)

    @show_contour.setter
    def show_contour(self, show):
        self._set_style(bool(show), sv.SHOWCONTOUR)

    @property
    def show_edge(self):
        """Enable zone edge lines for this plot.

        :type: `bool`

        Example usage::

            >>> frame.plot().show_edge = True
        """
        return self._get_style(bool, sv.SHOWEDGE)

    @show_edge.setter
    def show_edge(self, show):
        self._set_style(bool(show), sv.SHOWEDGE)

    @property
    def show_mesh(self):
        """Enable mesh lines for this plot.

        :type: `bool`

        Example usage::

            >>> frame.plot().show_mesh = True
        """
        return self._get_style(bool, sv.SHOWMESH)

    @show_mesh.setter
    def show_mesh(self, show):
        self._set_style(bool(show), sv.SHOWMESH)

    @property
    def show_scatter(self):
        """Enable scatter symbols for this plot.

        :type: `bool`

        Example usage::

            >>> frame.plot().show_scatter = True
        """
        return self._get_style(bool, sv.SHOWSCATTER)

    @show_scatter.setter
    def show_scatter(self, show):
        self._set_style(bool(show), sv.SHOWSCATTER)

    @property
    def show_shade(self):
        """Enable surface shading effect for this plot.

        :type: `bool`

        Example usage::

            >>> frame.plot().show_shade = True
        """
        return self._get_style(bool, sv.SHOWSHADE)

    @show_shade.setter
    def show_shade(self, show):
        self._set_style(bool(show), sv.SHOWSHADE)

    @property
    def show_slices(self):
        """Show slices for this plot.

        :type: `boolean <bool>`

        Example usage::
            >>>frame.plot().show_slices(True)

        """
        with self.frame.activated():
            return session.get_style(bool, sv.SLICELAYERS, sv.SHOW,
                                     uniqueid=self.frame.uid)

    @show_slices.setter
    def show_slices(self, show):
        with self.frame.activated():
            session.set_style(bool(show), sv.SLICELAYERS, sv.SHOW,
                              uniqueid=self.frame.uid)

    @property
    def show_isosurfaces(self):
        """Show isosurfaces for this plot.

        :type: `boolean <bool>`

        Example usage::
            >>>frame.plot().show_isosurfaces(True)
        """
        with self.frame.activated():
            return session.get_style(bool, sv.ISOSURFACELAYERS, sv.SHOW,
                                     uniqueid=self.frame.uid)

    @show_isosurfaces.setter
    def show_isosurfaces(self, show):
        with self.frame.activated():
            session.set_style(bool(show), sv.ISOSURFACELAYERS, sv.SHOW,
                              uniqueid=self.frame.uid)

    @property
    def show_streamtraces(self):
        """Enable drawing `Streamtraces` on this plot.

        :type: `bool`

        Example usage::

            >>> frame.plot().show_streamtraces = True
        """
        with self.frame.activated():
            return session.get_style(bool, sv.STREAMTRACELAYERS, sv.SHOW,
                                     uniqueid=self.frame.uid)

    @show_streamtraces.setter
    def show_streamtraces(self, show):
        with self.frame.activated():
            session.set_style(bool(show), sv.STREAMTRACELAYERS, sv.SHOW,
                              uniqueid=self.frame.uid)

    @property
    def show_vector(self):
        """Enable drawing of vectors.

        :type: `bool`

        Example usage::

            >>> frame.plot().show_vector = True
        """
        return self._get_style(bool, sv.SHOWVECTOR)

    @show_vector.setter
    def show_vector(self, show):
        self._set_style(bool(show), sv.SHOWVECTOR)

    @property
    def num_fieldmaps(self):
        """Number of all fieldmaps in this plot.

        :type: `integer <int>`

        Example usage::

            >>> print(frame.plot().num_fieldmaps)
            3
        """
        return _tecutil.FieldMapGetCountForFrame(self.frame.uid)

    def fieldmap_index(self, zone):
        """Returns the index of the fieldmap associated with a `Zone <data_access>`.

        Parameters:
            zone (`Zone <data_access>`): The `Zone <data_access>` object that
                belongs to the `Dataset` associated with this plot.

        Returns:
            `Index`

        Example usage::

            >>> fmap_index = plot.fieldmap_index(dataset.zone('Zone'))
            >>> plot.fieldmap(fmap_index).show_mesh = True
        """
        with self.frame.activated():
            return Index(_tecutil.ZoneGetFieldMap(zone.index + 1) - 1)

    def fieldmaps(self):
        """All fieldmaps in this plot.

        Returns:
            Iterator of `Cartesian2DFieldmap` or `Cartesian3DFieldmap`

        Example usage::

            >>> for fmap in plot.fieldmaps():
            ...     fmap.mesh.show = True

        .. versionchanged:: 0.9
            `fieldmaps` was changed from a property (0.8 and earlier) to a
            method requiring parentheses.
        """
        for i in range(self.num_fieldmaps):
            yield self.fieldmap(i)

    @property
    def active_fieldmap_indices(self):
        """Set of active fieldmaps by index.

        :type: `set`

        This example sets the first three fieldmaps active, disabling all
        others. It then turns on scatter symbols for just these three::

            >>> plot.active_fieldmap_indices = [0, 1, 2]
            >>> for i in plot.active_fieldmap_indices:
            ...     plot.fieldmap(i).scatter.show = True
        """
        return session.get_style(set, sv.ACTIVEFIELDMAPS,
                                 uniqueid=self.frame.uid)

    @active_fieldmap_indices.setter
    def active_fieldmap_indices(self, values):
        session.set_style(set(values), sv.ACTIVEFIELDMAPS,
                          uniqueid=self.frame.uid)

    @property
    def active_fieldmaps(self):
        """Active fieldmaps in this plot.

        Returns:
            `Cartesian2DFieldmap` or `Cartesian3DFieldmap`

        Example usage::

            >>> for fmap in plot.active_fieldmaps:
            ...     fmap.vector.show = True

        .. note:: **Possible side-effect when connected to Tecplot 360.**

                Changing the solution times in the dataset or modifying the
                active fieldmaps in a frame may trigger a change in the active
                plot's solution time by the Tecplot 360 interface. This is done
                to keep the GUI controls consistent. In batch mode, no such
                side-effect will take place and the user must take care to set
                the plot's solution time with the `plot.solution_time
                <Cartesian3DFieldPlot.solution_time>` or
                `plot.solution_timestep
                <Cartesian3DFieldPlot.solution_timestep>` properties.
        """
        return [self.fieldmap(i) for i in sorted(self.active_fieldmap_indices)]

    @active_fieldmaps.setter
    def active_fieldmaps(self, values):
        self.active_fieldmap_indices = [getattr(v, 'index', v) for v in values]

    @property
    def num_solution_times(self):
        """Number of solution times for all active fieldmaps.

        :type: `int`

        .. note::

            This only returns the number of *active* solution times. When
            assigning strands and solution times to zones, the zones are
            placed into an *inactive* fieldmap that must be subsequently
            activated. See example below.

        .. code-block:: python

            >>> # place all zones into a single fieldmap (strand: 1)
            >>> # with incrementing solution times
            >>> for time, zone in enumerate(dataset.zones()):
            ...     zone.strand = 1
            ...     zone.solution_time = time
            ...
            >>> # We must activate the fieldmap to ensure the plot's
            >>> # solution times have been updated. Since we placed
            >>> # all zones into a single fieldmap, we can assume the
            >>> # first fieldmap (index: 0) is the one we want.
            >>> plot.active_fieldmaps += [0]
            >>>
            >>> # now the plot's solution times are available.
            >>> print(plot.num_solution_times)
            10
            >>> print(plot.solution_times)
            [0.0, 1.0, 2.0, 3.0, 4.0, 5.0, 6.0, 7.0, 8.0, 9.0]

        .. versionadded:: 2017.2
            Solution time manipulation requires Tecplot 360 2017 R2 or later.
        """
        if __debug__:
            reqver = (2017, 2)
            if version.sdk_version_info < reqver:
                msg = 'Solution time manipulation requires 2017 R2 or later.'
                raise TecplotOutOfDateEngineError(reqver, msg)
        success, result = _tecutil.SolutionTimeGetNumTimeStepsForFrame(
            self.frame.uid)
        if not success:
            raise TecplotSystemError()
        return result

    @property
    def solution_times(self):
        """`List <list>` of active solution times.

        :type: `list` of `floats <float>`

        .. note::

            This only returns the list of *active* solution times. When
            assigning strands and solution times to zones, the zones are placed
            into an *inactive* fieldmap that must be subsequently activated.
            See example below.

        Example usage::

            >>> print(plot.solution_times)
            [0.0, 1.0, 2.0]

        .. versionadded:: 2017.2
            Solution time manipulation requires Tecplot 360 2017 R2 or later.
        """
        if __debug__:
            reqver = (2017, 2)
            if version.sdk_version_info < reqver:
                msg = 'Solution time manipulation requires 2017 R2 or later.'
                raise TecplotOutOfDateEngineError(reqver, msg)
        res = _tecutil.SolutionTimeGetSolutionTimesForFrame(self.frame.uid)
        success, ntimes, times = res
        if not success:
            raise TecplotSystemError()
        ret = list(times[:ntimes])
        if not _tecutil_connector.connected:
            _tecutil.ArrayDealloc(times)
        return ret

    @property
    def solution_time(self):
        """The current solution time.

        :type: `float`

        Example usage::

            >>> print(plot.solution_times)
            [0.0, 1.0, 2.0]
            >>> plot.solution_time = 1.0

        .. note:: **Possible side-effect when connected to Tecplot 360.**

                Changing the solution times in the dataset or modifying the
                active fieldmaps in a frame may trigger a change in the active
                plot's solution time by the Tecplot 360 interface. This is done
                to keep the GUI controls consistent. In batch mode, no such
                side-effect will take place and the user must take care to set
                the plot's solution time with the `plot.solution_time
                <Cartesian3DFieldPlot.solution_time>` or
                `plot.solution_timestep
                <Cartesian3DFieldPlot.solution_timestep>` properties.

        .. versionadded:: 2017.2
            Solution time manipulation requires Tecplot 360 2017 R2 or later.
        """
        if __debug__:
            reqver = (2017, 2)
            if version.sdk_version_info < reqver:
                msg = 'Solution time manipulation requires 2017 R2 or later.'
                raise TecplotOutOfDateEngineError(reqver, msg)
        return _tecutil.SolutionTimeGetCurrentForFrame(self.frame.uid)

    @solution_time.setter
    @lock()
    def solution_time(self, value):
        if __debug__:
            reqver = (2017, 2)
            if version.sdk_version_info < reqver:
                msg = 'Solution time manipulation requires 2017 R2 or later.'
                raise TecplotOutOfDateEngineError(reqver, msg)
        with self.frame.activated():
            res = _tecutil.SolutionTimeSetCurrent(float(value))
            if res not in [SetValueReturnCode.Ok,
                           SetValueReturnCode.DuplicateValue]:
                raise TecplotSystemError()

    @property
    def solution_timestep(self):
        """The zero-based index of the current solution time.

        :type: `int`

        Example usage::

            >>> print(plot.solution_times)
            [0.0, 1.0, 2.0]
            >>> print(plot.solution_time)
            0.0
            >>> plot.solution_timestep += 1
            >>> print(plot.solution_time)
            1.0

        .. note:: **Possible side-effect when connected to Tecplot 360.**

                Changing the solution times in the dataset or modifying the
                active fieldmaps in a frame may trigger a change in the active
                plot's solution time by the Tecplot 360 interface. This is done
                to keep the GUI controls consistent. In batch mode, no such
                side-effect will take place and the user must take care to set
                the plot's solution time with the `plot.solution_time
                <Cartesian3DFieldPlot.solution_time>` or
                `plot.solution_timestep
                <Cartesian3DFieldPlot.solution_timestep>` properties.

        .. versionadded:: 2017.2
            Solution time manipulation requires Tecplot 360 2017 R2 or later.
        """
        if __debug__:
            reqver = (2017, 2)
            if version.sdk_version_info < reqver:
                msg = 'Solution time manipulation requires 2017 R2 or later.'
                raise TecplotOutOfDateEngineError(reqver, msg)
        success, result = _tecutil.SolutionTimeGetCurrentTimeStepForFrame(
            self.frame.uid)
        if not success:
            raise TecplotSystemError()
        return result - 1

    @solution_timestep.setter
    def solution_timestep(self, timestep):
        if __debug__:
            reqver = (2017, 2)
            if version.sdk_version_info < reqver:
                msg = 'Solution time manipulation requires 2017 R2 or later.'
                raise TecplotOutOfDateEngineError(reqver, msg)
        success, time = _tecutil.SolutionTimeGetSolutionTimeAtTimeStepForFrame(
            self.frame.uid, int(timestep) + 1)
        if not success:
            raise TecplotSystemError()
        self.solution_time = time

    @lock()
    def _ensure_valid_solution_time(self):
        """Sets the plot's solution time to a valid value.

        To mimick behavior when connected to 360
        we have to update the plot's solution time
        to make sure it is always valid, i.e. within
        the dataset's solution time range.
        """
        with self.activated():
            if self.num_solution_times > 0:
                t = self.solution_time
                tmin = _tecutil.SolutionTimeGetMin()
                if t < tmin:
                    self.solution_time = tmin
                else:
                    tmax = _tecutil.SolutionTimeGetMax()
                    if t > tmax:
                        self.solution_time = tmax


class Cartesian2DFieldPlot(FieldPlot):
    """2D plot containing field data associated with style through fieldmaps.

    .. code-block:: python
        :emphasize-lines: 10-17,23-24

        from os import path
        import tecplot as tp
        from tecplot.constant import PlotType

        examples_dir = tp.session.tecplot_examples_directory()
        infile = path.join(examples_dir, 'SimpleData', 'HeatExchanger.plt')
        dataset = tp.data.load_tecplot(infile)

        frame = tp.active_frame()
        plot = frame.plot(PlotType.Cartesian2D)
        plot.activate()

        plot.vector.u_variable = dataset.variable('U(M/S)')
        plot.vector.v_variable = dataset.variable('V(M/S)')

        plot.contour(2).variable = dataset.variable('T(K)')
        plot.contour(2).colormap_name = 'Sequential - Yellow/Green/Blue'

        for z in dataset.zones():
            fmap = plot.fieldmap(z)
            fmap.contour.flood_contour_group = plot.contour(2)

        plot.show_contour = True
        plot.show_vector = True

        # save image to file
        tp.export.save_png('plot_field2d.png', 600, supersample=3)

    ..  figure:: /_static/images/plot_field2d.png
        :width: 300px
        :figwidth: 300px
    """

    def activate(self):
        """Make this the active plot type on the parent frame.

        Example usage::

            >>> from tecplot.constant import PlotType
            >>> plot = frame.plot(PlotType.Cartesian2D)
            >>> plot.activate()
        """
        self.frame.plot_type = PlotType.Cartesian2D

    @property
    def axes(self):
        """Axes style control for this plot.

        :type: `Cartesian2DFieldAxes`

        Example usage::

            >>> from tecplot.constant import PlotType
            >>> frame.plot_type = PlotType.Cartesian2D
            >>> axes = frame.plot().axes
            >>> axes.x_axis.variable = dataset.variable('U')
            >>> axes.y_axis.variable = dataset.variable('V')
        """
        return Cartesian2DFieldAxes(self)

    def fieldmap(self, key):
        """Returns a `Cartesian2DFieldmap` by `Zone <data_access>` or index.

        Parameters:
            key (`Zone <data_access>` or `integer <int>`): The
                `Zone <data_access>` must be in the `Dataset` attached to the
                assocated frame of this plot.

        Example usage::

            >>> fmap = plot.fieldmap(dataset.zone(0))
            >>> fmap.scatter.show = True
        """
        index = key if isinstance(key, int) else self.fieldmap_index(key)
        return Cartesian2DFieldmap(index, self)

    @property
    def vector(self):
        """Vector variable and style control for this plot.

        :type: `Vector2D`

        Example usage::

            >>> plot.vector.u_variable = dataset.variable('U')
        """
        return Vector2D(self)

    @property
    def draw_order(self):
        """The order in which objects are drawn to the screen.

        :type: `TwoDDrawOrder`

        Possible values: `TwoDDrawOrder.ByZone`, `TwoDDrawOrder.ByLayer`.

        The order is either by `Zone <data_access>` or by visual layer
        (contour, mesh, etc.)::

            >>> plot.draw_order = TwoDDrawOrder.ByZone
        """
        return self._get_style(TwoDDrawOrder, sv.TWODDRAWORDER)

    @draw_order.setter
    def draw_order(self, order):
        self._set_style(TwoDDrawOrder(order), sv.TWODDRAWORDER)

    @property
    def view(self):
        """Axes orientation and limits adjustments.

        :type: `Cartesian2DView`

        Example usage::

            >>> plot.view.fit()
        """
        return Cartesian2DView(self)


class Cartesian3DFieldPlot(FieldPlot):
    """3D plot containing field data associated with style through fieldmaps.

    .. code-block:: python
        :emphasize-lines: 10-14

        from os import path
        import tecplot as tp
        from tecplot.constant import PlotType

        examples_dir = tp.session.tecplot_examples_directory()
        infile = path.join(examples_dir, 'SimpleData', 'SpaceShip.lpk')
        dataset = tp.load_layout(infile)

        frame = tp.active_frame()
        plot = frame.plot(PlotType.Cartesian3D)
        plot.activate()
        plot.use_lighting_effect = False
        plot.show_streamtraces = False
        plot.use_translucency = True

        # save image to file
        tp.export.save_png('plot_field3d.png', 600, supersample=3)

    ..  figure:: /_static/images/plot_field3d.png
        :width: 300px
        :figwidth: 300px
    """

    def activate(self):
        """Make this the active plot type on the parent frame.

        Example usage::

            >>> from tecplot.constant import PlotType
            >>> plot = frame.plot(PlotType.Cartesian3D)
            >>> plot.activate()
        """
        self.frame.plot_type = PlotType.Cartesian3D

    @property
    def axes(self):
        """Axes style control for this plot.

        :type: `Cartesian3DFieldAxes`

        Example usage::

            >>> from tecplot.constant import PlotType
            >>> frame.plot_type = PlotType.Cartesian3D
            >>> axes = frame.plot().axes
            >>> axes.x_axis.variable = dataset.variable('U')
            >>> axes.y_axis.variable = dataset.variable('V')
            >>> axes.z_axis.variable = dataset.variable('W')
        """
        return Cartesian3DFieldAxes(self)

    def fieldmap(self, key):
        """Returns a `Cartesian3DFieldmap` by `Zone <data_access>` or index.

        Parameters:
            key (`Zone <data_access>` or `integer <int>`): The `Zone
                <data_access>` must be in the `Dataset` attached to the
                assocated frame of this plot.

        Example usage::

            >>> fmap = plot.fieldmap(dataset.zone(0))
            >>> fmap.scatter.show = True
        """
        index = key if isinstance(key, int) else self.fieldmap_index(key)
        return Cartesian3DFieldmap(index, self)

    @property
    def vector(self):
        """Vector variable and style control for this plot.

        :type: `Vector3D`

        Example usage::

            >>> plot.vector.u_variable = dataset.variable('U')
        """
        return Vector3D(self)

    @property
    def view(self):
        """Viewport, axes orientation and limits adjustments.

        :type: `Cartesian3DView`

        Example usage::

            >>> plot.view.fit()
        """
        return Cartesian3DView(self)

    @property
    def use_lighting_effect(self):
        """Enable lighting effect for all objects within this plot.

        :type: `bool`

        Example usage::

            >>> frame.plot().use_lighting_effect = True
        """
        return self._get_style(bool, sv.USELIGHTINGEFFECT)

    @use_lighting_effect.setter
    def use_lighting_effect(self, value):
        self._set_style(bool(value), sv.USELIGHTINGEFFECT)

    @property
    def use_translucency(self):
        """Enable translucent effect for all objects within this plot.

        :type: `bool`

        Example usage::

            >>> frame.plot().use_translucency = True
        """
        return self._get_style(bool, sv.USETRANSLUCENCY)

    @use_translucency.setter
    def use_translucency(self, show):
        self._set_style(bool(show), sv.USETRANSLUCENCY)


class LinePlot(Plot):
    """Plot with line data and associated style through linemaps.

    .. code-block:: python
        :emphasize-lines: 10-12

        from os import path
        import tecplot as tp
        from tecplot.constant import PlotType, Color, LinePattern

        examples_dir = tp.session.tecplot_examples_directory()
        infile = path.join(examples_dir, 'SimpleData', 'Rainfall.dat')
        dataset = tp.data.load_tecplot(infile)

        frame = tp.active_frame()
        frame.plot_type = PlotType.XYLine
        plot = frame.plot()
        plot.show_symbols = True

        # save image to file
        tp.export.save_png('plot_line.png', 600, supersample=3)

    ..  figure:: /_static/images/plot_line.png
        :width: 300px
        :figwidth: 300px
    """

    def __init__(self, frame):
        super().__init__(frame, sv.LINEPLOTLAYERS)

    @lock()
    def delete_linemaps(self, *linemaps):
        r"""Clear all linemaps within this plot.

        Parameters:
            \*linemaps (:ref:`Linemap`, `integer <int>` or `string <str>`):
                One or more of the following: :ref:`Linemap` objects, linemap
                indices (zero-based) or linemap names. If none are given, all
                linemaps will be deleted.

        Example usage::

            >>> plot.delete_linemaps()
            >>> print(plot.num_linemaps)
            0
        """
        if not linemaps:
            return _tecutil.LineMapDelete(None)
        with IndexSet() as indices:
            for lmap in flatten_args(*linemaps):
                try:
                    # try as a Linemap object
                    indices.append(lmap.index)
                except (AttributeError, TypeError):
                    try:
                        # try as a linemap index
                        indices.append(lmap)
                    except TypeError:
                        # assume name pattern
                        for submap in self.linemaps(lmap):
                            indices.append(submap.index)
            return _tecutil.LineMapDelete(indices)

    @property
    def num_linemaps(self):
        """Number of linemaps held by this plot.

        :type: `integer <int>`

        Example usage::

            >>> print(plot.num_linemaps)
            3
        """
        return _tecutil.LineMapGetCountForFrame(self.frame.uid)

    def linemaps(self, pattern=None):
        """Yields linemaps matching the given pattern

        Parameters:
            pattern (`string <str>`, optional): A name pattern to match. If no
                pattern is given, all linemaps are yielded.

        Returns:
            `XYLinemap` or `PolarLine` objects.

        Example usage::

            >>> for lmap in plot.linemaps():
            ...     lmap.show = True
        """
        with self.frame.activated():
            for i in range(self.num_linemaps):
                success, name = _tecutil.LineMapGetName(i + 1)
                if success:
                    if pattern is None or fnmatch(name, pattern):
                        yield self.linemap(i)

    def _linemap_unique_id(self, index):
        with self.frame.activated():
            return _tecutil.LineMapGetUniqueID(index + 1)

    @lock()
    def _add_linemap(self, name, zone, show=True):
        with self.frame.activated():
            new_linemap_index = self.num_linemaps
            if not _tecutil.LineMapCreate():
                raise TecplotSystemError()
            linemap = self.linemap(new_linemap_index)
            if name is not None:
                linemap.name = name
            if zone is not None:
                linemap.zone_index = getattr(zone, 'index', zone)
            if show is not None:
                linemap.show = show
            return linemap

    @property
    def legend(self):
        """Line plot legend style and placement control.

        :type: `LineLegend`

        Example usage::

            >>> plot.legend.show = True
        """
        return LineLegend(self, sv.GLOBALLINEPLOT)

    @property
    def active_linemap_indices(self):
        """`set` of all active linemaps by index.

        :type: `set` of `integers <int>`

        Numbers are zero-based indices to the linemaps::

            >>> active_indices = plot.active_linemap_indices
            >>> active_lmaps = [plot.linemap(i) for i in active_indices]
        """
        return session.get_style(set, sv.ACTIVELINEMAPS,
                                 uniqueid=self.frame.uid)

    @property
    def active_linemaps(self):
        """Yields all active linemaps.

        Returns:
            `XYLinemap` or `PolarLinemap`

        Example usage::

            >>> from tecplot.constant import Color
            >>> for lmap in plot.active_linemaps:
            ...     lmap.line.color = Color.Blue
        """
        for i in sorted(self.active_linemap_indices):
            yield self.linemap(i)

    @property
    def show_lines(self):
        """Enable lines for this plot.

        :type: `boolean <bool>`

        Example usage::

            >>> plot.show_lines = True
        """
        return self._get_style(bool, sv.SHOWLINES)

    @show_lines.setter
    def show_lines(self, value):
        self._set_style(bool(value), sv.SHOWLINES)

    @property
    def show_symbols(self):
        """Enable symbols at line vertices for this plot.

        :type: `boolean <bool>`

        Example usage::

            >>> plot.show_symbols = True
        """
        return self._get_style(bool, sv.SHOWSYMBOLS)

    @show_symbols.setter
    def show_symbols(self, value):
        self._set_style(bool(value), sv.SHOWSYMBOLS)


class XYLinePlot(LinePlot):
    """Cartesian plot with line data and associated style through linemaps.

    .. code-block:: python
        :emphasize-lines: 10-14

        from os import path
        import tecplot as tp
        from tecplot.constant import PlotType, FillMode

        examples_dir = tp.session.tecplot_examples_directory()
        infile = path.join(examples_dir, 'SimpleData', 'SunSpots.plt')
        dataset = tp.data.load_tecplot(infile)

        frame = tp.active_frame()
        plot = frame.plot(PlotType.XYLine)
        plot.activate()
        plot.show_symbols = True
        plot.linemap(0).symbols.fill_mode = FillMode.UseLineColor
        plot.linemap(0).symbols.size = 1

        tp.export.save_png('plot_xyline.png', 600, supersample=3)

    ..  figure:: /_static/images/plot_xyline.png
        :width: 300px
        :figwidth: 300px
    """

    def activate(self):
        """Make this the active plot type on the parent frame.

        Example usage::

            >>> from tecplot.constant import PlotType
            >>> plot = frame.plot(PlotType.XYLine)
            >>> plot.activate()
        """
        self.frame.plot_type = PlotType.XYLine

    def linemap(self, pattern):
        """Returns a specific linemap within this plot.

        Parameters:
            pattern (`integer <int>` or `string <str>`): This is either a
                zero-based index or a glob-like pattern which is matched to the
                linemap names. If more than one linemap shares the same name,
                the lowest indexed linemap will be returned.

        Returns:
            `XYLinemap`

        Example usage::

            >>> plot.linemap(0).error_bar.show = True
        """
        if isinstance(pattern, int):
            return XYLinemap(self._linemap_unique_id(pattern), self)
        else:
            try:
                return next(self.linemaps(pattern))
            except StopIteration:
                raise TecplotPatternMatchError(
                    pattern,
                    'no linemap found with name: "{}"'.format(pattern),
                    'glob')

    def add_linemap(self, name=None, zone=None, x=None, y=None, show=True):
        """Add a linemap using the specified zone and variables.

        Parameters:

            name (`string <str>`): Name of the linemap which can be used for
                retrieving with `XYLinePlot.linemap`. If `None`, then the
                linemap will not have a name. Default: `None`.
            zone (`Zone <data_access>`): The data to be used when drawing this
                linemap. If `None`, then |Tecplot Engine| will select a zone.
                Default: `None`.
            x (`Variable`): The ``x`` variable which must be from the same
                `Dataset` as ``y`` and ``zone``. If `None`, then
                |Tecplot Engine| will select an x variable. Default: `None`.
            y (`Variable`): The ``y`` variable which must be from the same
                `Dataset` as ``x`` and ``zone``. If `None`, then
                |Tecplot Engine| will select a ``y`` variable. Default: `None`.
            show (`boolean <bool>`, optional): Enable this linemap as soon as
                it's added. (default: `True`). If `None`, then |Tecplot Engine|
                will determine if the linemap should be enabled.

        Returns:
            `XYLinemap`

        Example usage::

            >>> lmap = plot.add_linemap('Line 1', dataset.zone('Zone'),
            ...                         dataset.variable('X'),
            ...                         dataset.variable('Y'))
            >>> lmap.line.line_thickness = 0.8
        """
        lmap = self._add_linemap(name, zone, show)
        if x is not None:
            lmap.x_variable = x
        if y is not None:
            lmap.y_variable = y
        return lmap

    @property
    def axes(self):
        """Axes style control for this plot.

        :type: `XYLineAxes`

        Example usage::

            >>> from tecplot.constant import PlotType, AxisMode
            >>> frame.plot_type = PlotType.XYLine
            >>> axes = frame.plot().axes
            >>> axes.axis_mode = AxisMode.XYDependent
            >>> axes.xy_ratio = 2
        """
        return XYLineAxes(self)

    @property
    def show_bars(self):
        """Enable bar chart drawing mode for this plot.

        :type: `boolean <bool>`

        Example usage::

            >>> plot.show_bars = True
        """
        return self._get_style(bool, sv.SHOWBARCHARTS)

    @show_bars.setter
    def show_bars(self, value):
        self._set_style(bool(value), sv.SHOWBARCHARTS)

    @property
    def show_error_bars(self):
        """Enable error bars for this plot.

        :type: `boolean <bool>`

        The variable to be used for error bars must be set first on at least
        one linemap within this plot::

            >>> plot.linemap(0).error_bars.variable = dataset.variable('E')
            >>> plot.show_error_bars = True
        """
        return self._get_style(bool, sv.SHOWERRORBARS)

    @show_error_bars.setter
    def show_error_bars(self, value):
        self._set_style(bool(value), sv.SHOWERRORBARS)

    @property
    def view(self):
        """View control of the plot relative to the frame.

        :type: `LineView`

        Example usage::

            >>> plot.view.fit()
        """
        return LineView(self)


class PolarLinePlot(LinePlot):
    """Polar plot with line data and associated style through linemaps.

    .. code-block:: python
        :emphasize-lines: 16-22,25

        import numpy as np
        import tecplot as tp
        from tecplot.constant import *

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
        plot.axes.r_axis.max = r.max()
        plot.axes.theta_axis.mode = ThetaMode.Radians
        plot.delete_linemaps()
        lmap = plot.add_linemap('Linemap', zone, dataset.variable('R'),
                                    dataset.variable('Theta'))
        lmap.line.line_thickness = 0.8
        lmap.line.color = Color.Green

        plot.view.fit()

        tp.export.save_png('plot_polar.png', 600, supersample=3)

    ..  figure:: /_static/images/plot_polar.png
        :width: 300px
        :figwidth: 300px
    """

    def activate(self):
        """Make this the active plot type on the parent frame.

        Example usage::

            >>> from tecplot.constant import PlotType
            >>> plot = frame.plot(PlotType.PolarLine)
            >>> plot.activate()
        """
        self.frame.plot_type = PlotType.PolarLine

    @property
    def axes(self):
        """Axes style control for this plot.

        :type: `PolarLineAxes`

        Example usage::

            >>> from tecplot.constant import PlotType, ThetaMode
            >>> frame.plot_type = PlotType.PolarLine
            >>> axes = frame.plot().axes
            >>> axes.theta_mode = ThetaMode.Radians
        """
        return PolarLineAxes(self)

    @property
    def view(self):
        """View control of the plot relative to the frame.

        :type: `PolarView`

        Example usage::

            >>> plot.view.fit()
        """
        return PolarView(self)

    def add_linemap(self, name=None, zone=None, r=None, theta=None, show=True):
        """Add a linemap using the specified zone and variables.

        Parameters:
            name (`string <str>`): Name of the linemap which can be used for
                retrieving with `PolarLinePlot.linemap`. If `None`, then the
                linemap will not have a name. Default: `None`.
            zone (`Zone <data_access>`): The data to be used when drawing this
                linemap. If `None`, then |Tecplot Engine| will select a
                `Zone <data_access>`.
                Default: `None`.
            r (`Variable`): The ``r`` variable which must be from the same
                `Dataset` as ``theta`` and ``zone``. If `None`, then
                |Tecplot Engine| will select a variable. Default: `None`.
            theta (`Variable`): The ``theta`` variable which must be from the
                same `Dataset` as ``r`` and ``zone``. If `None`, then
                |Tecplot Engine| will select a variable. Default: `None`.
            show (`boolean <bool>`, optional): Enable this linemap as soon as
                it's added. (default: `True`)

        Returns:
            `PolarLinemap`

        Example usage::

            >>> lmap = plot.add_linemap('Line 1', dataset.zone('Zone'),
            ...                         dataset.variable('R'),
            ...                         dataset.variable('Theta'))
            >>> lmap.line.line_thickness = 0.8
        """
        lmap = self._add_linemap(name, zone, show)
        if r is not None:
            lmap.r_variable = r
        if theta is not None:
            lmap.theta_variable = theta
        return lmap

    def linemap(self, pattern):
        """Returns a specific linemap within this plot.

        Parameters:
            pattern (`integer <int>` or `string <str>`): This is either a
                zero-based index or a glob-like pattern which is matched to the
                linemap names. If more than one linemap shares the same name,
                the lowest indexed linemap will be returned.

        Returns:
            `PolarLinemap`

        Example usage::

            >>> plot.linemap(0).error_bar.show = True
        """
        if isinstance(pattern, int):
            return PolarLinemap(self._linemap_unique_id(pattern), self)
        else:
            try:
                return next(self.linemaps(pattern))
            except StopIteration:
                raise TecplotPatternMatchError(
                    pattern,
                    'no linemap found with name: "{}"'.format(pattern),
                    'glob')
