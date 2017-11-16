from builtins import super, int

from collections import Iterable, namedtuple
from ctypes import cast
from enum import Enum
from textwrap import dedent

from ..tecutil import _tecutil
from ..constant import *
from ..exception import TecplotLogicError, TecplotSystemError
from .. import session
from ..session import Style
from ..tecutil import Index, IndexRange, IndexSet, color_spec, flatten_args, sv
from .scatter import GeometryScatterSymbol, TextScatterSymbol, Symbol


class FieldmapStyle(Style):
    def __init__(self, fieldmap, *svargs):
        self.fieldmap = fieldmap
        kw = dict(uniqueid=fieldmap.plot.frame.uid, offset1=fieldmap.index,
                  multiset=True)
        super().__init__(fieldmap._sv, *svargs, **kw)

    def __eq__(self, that):
        return isinstance(that, type(self)) and self.fieldmap == that.fieldmap

    def __ne__(self, that):
        return not (self == that)


class FieldmapContour(FieldmapStyle):
    """Style control for flooding and contour lines.

    This object controls which contour groups are associated with flooding,
    line placement and line coloring. Three different contour groups may be
    used though there are eight total groups that can be configured in a single
    plot. In this example, we flood by the first contour group (index: 0),
    place contour lines by the second contour group (index: 1) and color the
    lines by the third contour group (index: 2)::

        import numpy as np

        import tecplot as tp
        from tecplot.constant import *
        from tecplot.data.operate import execute_equation

        # Get the active frame, setup a grid (30x30x30)
        # where each dimension ranges from 0 to 30.
        # Add variables P,Q,R to the dataset and give
        # values to the data.
        frame = tp.active_frame()
        dataset = frame.dataset
        for v in ['X','Y','Z','P','Q','R']:
            dataset.add_variable(v)
        zone = dataset.add_ordered_zone('Zone', (30,30,30))
        xx = np.linspace(0,30,30)
        for v,arr in zip(['X','Y','Z'],np.meshgrid(xx,xx,xx)):
            zone.values(v)[:] = arr.ravel()
        execute_equation('{P} = -10 * {X}    +      {Y}**2 + {Z}**2')
        execute_equation('{Q} =       {X}    - 10 * {Y}    - {Z}**2')
        execute_equation('{R} =       {X}**2 +      {Y}**2 - {Z}   ')

        # Enable 3D field plot and turn on contouring
        # with boundary faces
        frame.plot_type = PlotType.Cartesian3D
        plot = frame.plot()
        srf = plot.fieldmap(0).surfaces
        srf.surfaces_to_plot = SurfacesToPlot.BoundaryFaces
        plot.show_contour = True

        # get the contour group associated with the
        # newly created zone
        contour = plot.fieldmap(dataset.zone('Zone')).contour

        # turn on flooding and lines, increase line thickness
        contour.contour_type = ContourType.Overlay
        contour.line_thickness = 0.7

        # assign flooding to the first contour group
        contour.flood_contour_group = plot.contour(0)
        contour.flood_contour_group.variable = dataset.variable('P')
        contour.flood_contour_group.colormap_name = 'Sequential - Yellow/Green/Blue'
        contour.flood_contour_group.legend.show = False

        # assign line placement to the second contour group
        contour.line_group = plot.contour(1)
        contour.line_group.legend.show = False
        contour.line_group.variable = dataset.variable('Q')
        contour.line_group.default_num_levels = 4

        # add labels to the lines based on placement
        contour.line_group.labels.show = True
        contour.line_group.labels.font.size = 3.5
        contour.line_group.labels.font.bold = True

        # assign line coloring to the third contour group
        contour.line_color = plot.contour(2)
        contour.line_color.legend.show = False
        contour.line_color.variable = dataset.variable('R')

        # save image to PNG file
        tp.export.save_png('fieldmap_contour.png', 600, supersample=3)

    .. figure:: /_static/images/fieldmap_contour.png
        :width: 300px
        :figwidth: 300px
    """
    def __init__(self, fieldmap):
        super().__init__(fieldmap, sv.CONTOUR)

    @property
    def show(self):
        """Enable drawing the contours.

        :type: `bool`

        Example usage::

            >>> contour = plot.fieldmap(0).contour
            >>> contour.show = True
        """
        return self._get_style(bool, sv.SHOW)

    @show.setter
    def show(self, value):
        self._set_style(bool(value), sv.SHOW)

    @property
    def contour_type(self):
        """`ContourType` to plot.

        :type: `ContourType`

        Possible values are:

            `ContourType.Flood` (default)
                Filled color between the contour levels.
            `ContourType.Lines`
                Lines only.
            `ContourType.Overlay`
                Lines overlayed on flood.
            `ContourType.AverageCell`
                Filled color by the average value within cells.
            `ContourType.PrimaryValue`
                Filled color by the value at the primary corner of the cells.

        In this example, we enable both flooding and contour lines::

            >>> from tecplot.constant import ContourType
            >>> contour = plot.fieldmap(0).contour
            >>> contour.contour_type = ContourType.Overlay
        """
        return self._get_style(ContourType, sv.CONTOURTYPE)

    @contour_type.setter
    def contour_type(self, value):
        self._set_style(ContourType(value), sv.CONTOURTYPE)

    @property
    def flood_contour_group_index(self):
        """The `Index` of the `ContourGroup` to use for flooding.

        :type: `integer <int>` (zero-based index)

        This property sets and gets, by `Index`, the `ContourGroup` used for
        flooding. Changing style on this `ContourGroup` will affect all other
        fieldmaps on the same `Frame` that use it. Example usage::

            >>> contour = plot.fieldmap(0).contour
            >>> contour.flood_contour_group_index = 1
            >>> contour.flood_contour_group.variable = dataset.variable('P')
        """
        return self._get_style(Index, sv.FLOODCOLORING)

    @flood_contour_group_index.setter
    def flood_contour_group_index(self, index):
        self._set_style(Index(index), sv.FLOODCOLORING)

    @property
    def flood_contour_group(self):
        """The `ContourGroup` to use for flooding.

        :type: `ContourGroup`

        This property sets and gets the `ContourGroup` used for flooding.
        Changing style on this `ContourGroup` will affect all other fieldmaps
        on the same `Frame` that use it. Example usage::

            >>> cmap_name = 'Sequential - Yellow/Green/Blue'
            >>> contour = plot.fieldmap(0).contour
            >>> contour.flood_contour_group = plot.contour(1)
            >>> contour.flood_contour_group.variable = dataset.variable('P')
            >>> contour.flood_contour_group.colormap_name = cmap_name
        """
        return self.fieldmap.plot.contour(self.flood_contour_group_index)

    @flood_contour_group.setter
    def flood_contour_group(self, contour_group):
        self.flood_contour_group_index = contour_group.index

    @property
    def line_group_index(self):
        """The `Index` of the `ContourGroup` to use for contour lines.

        :type: `integer <int>` (zero-based index)

        This property sets and gets, by `Index`, the `ContourGroup` used for
        line placement and though all properties of the `ContourGroup` can be
        manipulated through this object, many of them such as color will not
        affect the lines unless the `FieldmapContour.line_color` is set to the
        same `ContourGroup`. Note that changing style on this `ContourGroup`
        will affect all other fieldmaps on the same `Frame` that use it.
        Example usage::

            >>> contour = plot.fieldmap(0).contour
            >>> contour.line_group_index = 2
            >>> contour.line_group.variable = dataset.variable('Z')
        """
        return self._get_style(Index, sv.LINECONTOURGROUP)

    @line_group_index.setter
    def line_group_index(self, index):
        self._set_style(Index(index), sv.LINECONTOURGROUP)

    @property
    def line_group(self):
        """The `ContourGroup` to use for line placement and style.

        :type: `ContourGroup`

        This property sets and gets the `ContourGroup` used for line placement
        and though all properties of the `ContourGroup` can be manipulated
        through this object, many of them such as color will not effect the
        lines unless the `FieldmapContour.line_color` is set to the same
        `ContourGroup`. Note that changing style on this `ContourGroup` will
        affect all other fieldmaps on the same `Frame` that use it. Example
        usage::

            >>> contour = plot.fieldmap(0).contour
            >>> contour.line_group = plot.contour(2)
            >>> contour.line_group.variable = dataset.variable('Z')
        """
        return self.fieldmap.plot.contour(self.line_group_index)

    @line_group.setter
    def line_group(self, contour_group):
        self.line_group_index = contour_group.index

    @property
    def line_color(self):
        """The `Color` or `ContourGroup` to use when coloring the lines.

        :type: `Color` or `ContourGroup`

        FieldmapContour lines can be a solid color or be colored by a
        `ContourGroup` as obtained through the ``plot.contour`` property. Note
        that changing style on this `ContourGroup` will affect all other
        fieldmaps on the same `Frame` that use it. Example usage::

            >>> from tecplot.constant import Color
            >>> contour = plot.fieldmap(1).contour
            >>> contour.line_color = Color.Blue

        Example of setting the color from a `ContourGroup`::

            >>> contour = plot.fieldmap(0).contour
            >>> contour.line_color = plot.contour(1)
            >>> contour.line_color.variable = dataset.variable('P')
        """
        return color_spec(self._get_style(Color, sv.COLOR), self.fieldmap.plot)

    @line_color.setter
    def line_color(self, value):
        self._set_style(color_spec(value), sv.COLOR)

    @property
    def line_pattern(self):
        """`LinePattern` type to use for contour lines.

        :type: `LinePattern`

        Possible values: `Solid <LinePattern.Solid>`, `Dashed`, `DashDot`,
        `Dotted`, `LongDash`, `DashDotDot`.

        Example usage::

            >>> from tecplot.constant import LinePattern
            >>> contour = plot.fieldmap(0).contour
            >>> contour.line_pattern = LinePattern.DashDotDot
        """
        return self._get_style(LinePattern, sv.LINEPATTERN)

    @line_pattern.setter
    def line_pattern(self, value):
        self._set_style(LinePattern(value), sv.LINEPATTERN)

    @property
    def line_thickness(self):
        """Thickness (`float`) of the drawn lines.

        :type: `float` in percentage of the `Frame`'s height.

        Example usage::

            >>> contour = plot.fieldmap(0).contour
            >>> contour.line_thickness = 0.7
        """
        return self._get_style(float, sv.LINETHICKNESS)

    @line_thickness.setter
    def line_thickness(self, value):
        self._set_style(float(value), sv.LINETHICKNESS)

    @property
    def pattern_length(self):
        """Length (`float`) of the pattern segment for non-solid lines.

        :type: `float` in percentage of the `Frame`'s height.

        Example usage::

            >>> contour = plot.fieldmap(0).contour
            >>> contour.pattern_length = 3.5
        """
        return self._get_style(float, sv.PATTERNLENGTH)

    @pattern_length.setter
    def pattern_length(self, value):
        self._set_style(float(value), sv.PATTERNLENGTH)

    @property
    def use_lighting_effect(self):
        """Enable lighting effect on this contour.

        :type: `bool`

        Example usage::

            >>> contour = plot.fieldmap(0).contour
            >>> contour.use_lighting_effect = False
        """
        return self._get_style(bool, sv.USELIGHTINGEFFECT)

    @use_lighting_effect.setter
    def use_lighting_effect(self, value):
        self._set_style(bool(value), sv.USELIGHTINGEFFECT)


class FieldmapEdge(FieldmapStyle):
    """Volume boundary lines.

    An edge plot layer displays the connections of the outer lines
    (``IJ``-ordered zones), finite element surface zones, or planes
    (``IJK``-ordered zones). The FieldmapEdge layer allows you to display the
    edges (creases and borders) of your data. Zone edges exist only for ordered
    zones or 2D finite element zones. Three-dimensional finite element zones do
    not have boundaries.

    .. code-block:: python
        :emphasize-lines: 15,25-28

        import os

        import tecplot as tp
        from tecplot.constant import Color, EdgeType, PlotType, SurfacesToPlot

        examples_dir = tp.session.tecplot_examples_directory()
        datafile = os.path.join(examples_dir, 'SimpleData', 'F18.plt')
        dataset = tp.data.load_tecplot(datafile)
        frame = dataset.frame

        # Enable 3D field plot, turn on contouring and translucency
        frame.plot_type = PlotType.Cartesian3D
        plot = frame.plot()
        plot.show_contour = True
        plot.show_edge = True

        plot.contour(0).colormap_name = 'Sequential - Blue'

        # adjust effects for every fieldmap in this dataset
        for zone in dataset.zones():
            fmap = plot.fieldmap(zone)
            fmap.contour.flood_contour_group.variable = dataset.variable('S')
            fmap.surfaces.surfaces_to_plot = SurfacesToPlot.BoundaryFaces

            edge = fmap.edge
            edge.edge_type = EdgeType.Creases
            edge.color = Color.RedOrange
            edge.line_thickness = 0.7

        # save image to file
        tp.export.save_png('fieldmap_edge.png', 600, supersample=3)

    .. figure:: /_static/images/fieldmap_edge.png
        :width: 300px
        :figwidth: 300px
    """
    def __init__(self, fieldmap):
        super().__init__(fieldmap, sv.EDGELAYER)

    @property
    def show(self):
        """Draw the mesh for this fieldmap.

        :type: `boolean <bool>`

        Example usage::

            >>> plot.show_edge = True
            >>> plot.fieldmap(0).edge.show = True
        """
        return self._get_style(bool, sv.SHOW)

    @show.setter
    def show(self, value):
        self._set_style(bool(value), sv.SHOW)

    @property
    def edge_type(self):
        """Where to draw edge lines.

        :type: `EdgeType`

        Possible values: `Borders`, `Creases`, `BordersAndCreases`.

        Example usage::

            >>> from tecplot.constant import EdgeType
            >>> plot.show_edge = True
            >>> plot.fieldmap(0).edge.edge_type = EdgeType.Creases
        """
        return self._get_style(EdgeType, sv.EDGETYPE)

    @edge_type.setter
    def edge_type(self, value):
        self._set_style(EdgeType(value), sv.EDGETYPE)

    @property
    def color(self):
        """Line `Color`.

        :type: `Color`
        """
        return self._get_style(Color, sv.COLOR)

    @color.setter
    def color(self, value):
        self._set_style(Color(value), sv.COLOR)

    @property
    def line_thickness(self):
        """Thickness of the edge lines drawn.

        :type: `float` in percentage of `Frame` height.

        Example usage::

            >>> plot.fieldmap(0).edge.line_thickness = 0.4
        """
        return self._get_style(float, sv.LINETHICKNESS)

    @line_thickness.setter
    def line_thickness(self, value):
        self._set_style(float(value), sv.LINETHICKNESS)

    @property
    def i_border(self):
        """Which border lines to draw in the ``I``-dimension.

        :type: `BorderLocation`

        Possible values: `None`, `Min <BorderLocation.Min>`, `Max
        <BorderLocation.Max>`, `Both <BorderLocation.Both>`.

        Example usage::

            >>> from tecplot.constant import BorderLocation
            >>> plot.show_edge = True
            >>> plot.fieldmap(0).edge.i_border = BorderLocation.Min
        """
        value = self._get_style(BorderLocation, sv.IBORDER)
        return None if value is BorderLocation.None_ else value

    @i_border.setter
    def i_border(self, value):
        if value is None:
            value = BorderLocation.None_
        self._set_style(BorderLocation(value), sv.IBORDER)

    @property
    def j_border(self):
        """Which border lines to draw in the ``J``-dimension.

        :type: `BorderLocation`

        Possible values: `None`, `Min <BorderLocation.Min>`, `Max
        <BorderLocation.Max>`, `Both <BorderLocation.Both>`.

        Example usage::

            >>> from tecplot.constant import BorderLocation
            >>> plot.show_edge = True
            >>> plot.fieldmap(0).edge.j_border = BorderLocation.Both
        """
        value = self._get_style(BorderLocation, sv.JBORDER)
        return None if value is BorderLocation.None_ else value

    @j_border.setter
    def j_border(self, value):
        if value is None:
            value = BorderLocation.None_
        self._set_style(BorderLocation(value), sv.JBORDER)

    @property
    def k_border(self):
        """Which border lines to draw in the ``K``-dimension.

        :type: `BorderLocation`

        Possible values: `None`, `Min <BorderLocation.Min>`, `Max
        <BorderLocation.Max>`, `Both <BorderLocation.Both>`.

        Example usage::

            >>> from tecplot.constant import BorderLocation
            >>> plot.show_edge = True
            >>> plot.fieldmap(0).edge.k_border = None
        """
        value = self._get_style(BorderLocation, sv.KBORDER)
        return None if value is BorderLocation.None_ else value

    @k_border.setter
    def k_border(self, value):
        if value is None:
            value = BorderLocation.None_
        self._set_style(BorderLocation(value), sv.KBORDER)


class FieldmapMesh(FieldmapStyle):
    """Lines connecting neighboring data points.

    The mesh plot layer displays the lines connecting neighboring data points
    within a `Zone <data_access>`. For ``I``-ordered data, the mesh is a single line
    connecting all of the points in order of increasing ``I``-index. For
    ``IJ``-ordered data, the mesh consists of two families of lines connecting
    adjacent data points of increasing ``I``-index and increasing ``J``-index.
    For ``IJK``-ordered data, the mesh consists of three families of lines, one
    connecting points of increasing ``I``-index, one connecting points of
    increasing ``J``-index, and one connecting points of increasing
    ``K``-index. For finite element zones, the mesh is a plot of every edge of
    all of the elements that are defined by the connectivity list for the node
    points.

    .. code-block:: python
        :emphasize-lines: 23-25

        from os import path
        import numpy as np
        import tecplot as tp
        from tecplot.constant import PlotType, MeshType

        examples_dir = tp.session.tecplot_examples_directory()
        infile = path.join(examples_dir, 'SimpleData', 'F18.plt')
        dataset = tp.data.load_tecplot(infile)

        # Enable 3D field plot and turn on contouring
        frame = tp.active_frame()
        frame.plot_type = PlotType.Cartesian3D
        plot = frame.plot()
        plot.show_mesh = True

        contour = plot.contour(0)
        contour.variable = dataset.variable('S')
        contour.colormap_name = 'Doppler'
        contour.levels.reset_levels(np.linspace(0.02,0.12,11))

        # set the mesh type and color for all zones
        for zone in dataset.zones():
            mesh = plot.fieldmap(zone).mesh
            mesh.mesh_type = MeshType.HiddenLine
            mesh.color = contour

        # save image to file
        tp.export.save_png('fieldmap_mesh.png', 600, supersample=3)

    .. figure:: /_static/images/fieldmap_mesh.png
        :width: 300px
        :figwidth: 300px
    """
    def __init__(self, fieldmap):
        super().__init__(fieldmap, sv.MESH)

    @property
    def show(self):
        """Draw the mesh for this fieldmap.

        :type: `boolean <bool>`

        Example usage::

            >>> from tecplot.constant import SurfacesToPlot
            >>> plot.show_mesh = True
            >>> surfaces = plot.fieldmap(0).surfaces
            >>> surfaces.surfaces_to_plot = SurfacesToPlot.IPlanes
            >>> plot.fieldmap(0).mesh.show = True
        """
        return self._get_style(bool, sv.SHOW)

    @show.setter
    def show(self, value):
        self._set_style(bool(value), sv.SHOW)

    @property
    def mesh_type(self):
        """`MeshType` to show.

        :type: `MeshType`

        Possible values:

        `Wireframe <MeshType.Wireframe>`
            Wire frame meshes are drawn below any other zone layers on the same
            zone. In 3D Cartesian plots, no hidden lines are removed. For 3D
            volume zones (finite element volume or IJK-ordered), the full 3D
            mesh (consisting of all the connecting lines between data points)
            is not generally drawn because the sheer number of lines would make
            it confusing. The mesh drawn will depend on `FieldmapSurfaces`
            which can be obtained through the parent fieldmap with
            ``mesh.fieldmap.surfaces``::

                from tecplot.constant import MeshType, SurfacesToPlot
                mesh = plot.fieldmap(0).mesh
                mesh.mesh_type = MeshType.Wireframe
                surfaces = mesh.fieldmap.surfaces
                surfaces.surfaces_to_plot = SurfacesToPlot.IPlanes

            By default, only the mesh on exposed cell faces is shown.

        `Overlay <MeshType.Overlay>`
            Similar to Wire Frame, mesh lines are drawn over all other zone
            layers except for vectors and scatter symbols. In 3D Cartesian
            plots, the area behind the cells of the plot is still visible
            (unless another plot type such as contour flooding prevents this).
            As with Wire Frame, the mesh drawn will depend on
            `FieldmapSurfaces` which can be obtained through the parent
            fieldmap with ``mesh.fieldmap.surfaces``.

        `HiddenLine <MeshType.HiddenLine>`
            Similar to Overlay, except hidden lines are removed from behind the
            mesh. In effect, the cells (elements) of the mesh are opaque.
            FieldmapSurfaces and lines that are hidden behind another surface
            are removed from the plot. For 3D volume zones, using this plot
            type obscures everything inside the zone. If you choose this option
            for 3D volume zones, then choosing to plot every surface with::

                from tecplot.constant import HiddenLine, SurfacesToPlot
                mesh = plot.fieldmap(0).mesh
                mesh.mesh_type = MeshType.HiddenLine
                surfaces = mesh.fieldmap.surfaces
                surfaces.surfaces_to_plot = SurfacesToPlot.All

            has the same effect as plotting only exposed cell faces with::

                surfaces.surfaces_to_plot = SurfacesToPlot.ExposedCellFaces

            but is much slower.
        """
        return self._get_style(MeshType, sv.MESHTYPE)

    @mesh_type.setter
    def mesh_type(self, value):
        self._set_style(MeshType(value), sv.MESHTYPE)

    @property
    def color(self):
        """The `Color` or `ContourGroup` to use when drawing the lines.

        :type: `Color` or `ContourGroup`

        FieldmapContour lines can be a solid color or be colored by a
        `ContourGroup` as obtained through the ``plot.contour`` property. Note
        that changing style on this `ContourGroup` will affect all other
        fieldmaps on the same `Frame` that use it. Example usage::

            >>> from tecplot.constant import Color
            >>> plot.fieldmap(1).mesh.color = Color.Blue

        Example of setting the color from a `ContourGroup`::

            >>> plot.fieldmap(1).mesh.color = plot.contour(1)
        """
        return color_spec(self._get_style(Color, sv.COLOR), self.fieldmap.plot)

    @color.setter
    def color(self, value):
        self._set_style(color_spec(value), sv.COLOR)

    @property
    def line_pattern(self):
        """`LinePattern` type to use for mesh lines.

        :type: `LinePattern`

        Possible values: `Solid <LinePattern.Solid>`, `Dashed`, `DashDot`,
        `Dotted`, `LongDash`, `DashDotDot`.

        Example usage::

            >>> from tecplot.constant import LinePattern
            >>> mesh = plot.fieldmap(0).mesh
            >>> mesh.line_pattern = LinePattern.Dashed
        """
        return self._get_style(LinePattern, sv.LINEPATTERN)

    @line_pattern.setter
    def line_pattern(self, value):
        self._set_style(LinePattern(value), sv.LINEPATTERN)

    @property
    def line_thickness(self):
        """Thickness (`float`) of the drawn lines.

        :type: `float` in percentage of the `Frame`'s height.

        Example usage::

            >>> plot.fieldmap(0).mesh.line_thickness = 0.7
        """
        return self._get_style(float, sv.LINETHICKNESS)

    @line_thickness.setter
    def line_thickness(self, value):
        self._set_style(float(value), sv.LINETHICKNESS)

    @property
    def pattern_length(self):
        """Length (`float`) of the pattern segment for non-solid lines.

        :type: `float` in percentage of the `Frame`'s height.

        Example usage::

            >>> plot.fieldmap(0).mesh.pattern_length = 3.5
        """
        return self._get_style(float, sv.PATTERNLENGTH)

    @pattern_length.setter
    def pattern_length(self, value):
        self._set_style(float(value), sv.PATTERNLENGTH)


class FieldmapPoints(FieldmapStyle):
    """Type and density of the points used for vector and scatter plots.

    This object controls the location of the points for `FieldmapVector` and
    `FieldmapScatter` plots relative to the cells.

    .. code-block:: python
        :emphasize-lines: 18-22

        from os import path
        import tecplot as tp
        from tecplot.constant import PlotType, PointsToPlot

        examples_dir = tp.session.tecplot_examples_directory()
        infile = path.join(examples_dir, 'SimpleData', 'HeatExchanger.plt')
        dataset = tp.data.load_tecplot(infile)

        # Enable 3D field plot and turn on contouring
        frame = tp.active_frame()
        frame.plot_type = PlotType.Cartesian2D
        plot = frame.plot()
        plot.vector.u_variable = dataset.variable('U(M/S)')
        plot.vector.v_variable = dataset.variable('V(M/S)')
        plot.show_vector = True

        for zone in dataset.zones():
            points = plot.fieldmap(zone).points
            points.points_to_plot = PointsToPlot.SurfaceCellCenters
            points.step = (2,2)

        # save image to file
        tp.export.save_png('fieldmap_points.png', 600, supersample=3)

    .. figure:: /_static/images/fieldmap_points.png
        :width: 300px
        :figwidth: 300px
    """
    def __init__(self, fieldmap):
        super().__init__(fieldmap, sv.POINTS)

    _IJKStep = namedtuple('IJKStep', ['i', 'j', 'k'])
    _IJKStep.__new__.__defaults__ = (None, None, None)

    @property
    def points_to_plot(self):
        """Location of the points to show.

        :type: `PointsToPlot`

        Possible values:

        `SurfaceNodes`
            Draws only the nodes that are on the surface of the `Zone <data_access>`.

        `AllNodes`
            Draws all nodes in the `Zone <data_access>`.

        `SurfaceCellCenters`
            Draws points at the cell centers which are on or near the surface
            of the `Zone <data_access>`.

        `AllCellCenters`
             Draws points at all cell centers in the `Zone <data_access>`.

        `AllConnected`
            Draws all the nodes that are connected by the node map. Nodes
            without any connectivity are not drawn.

        Example usage::

            >>> from tecplot.constant import PointsToPlot
            >>> pts = plot.fieldmap(0).points
            >>> sts.points_to_plot = PointsToPlot.SurfaceCellCenters
        """
        return self._get_style(PointsToPlot, sv.POINTSTOPLOT)

    @points_to_plot.setter
    def points_to_plot(self, points):
        self._set_style(PointsToPlot(points), sv.POINTSTOPLOT)

    @property
    def step(self):
        """Step along the dimensions (``I``, ``J``, ``K``).

        :type: `tuple` of `integers <int>`

        This property specifies the ``I``, ``J``, and ``K``-step intervals. For
        irregular and finite element data, only the first parameter or
        ``I``-Step has an effect. This steps through the nodes in the order
        they are listed in the data file. In this case, a single number can be
        given, but note that the return type is always a 3-`tuple` for both
        ordered and irregular data.

        Example for ``IJK`` ordered data::

            >>> plot.fieldmap(0).points.step = (10,10,None)
            >>> print(plot.fieldmap(0).points.step)
            (10, 10, 1)

        Example for irregular data::

            >>> plot.fieldmap(0).points.step = 10
            >>> print(plot.fieldmap(0).points.step)
            (10, 1, 1)
        """
        return tuple(FieldmapPoints._IJKStep(
                     self._get_style(int, sv.IJKSKIP, sv.I),
                     self._get_style(int, sv.IJKSKIP, sv.J),
                     self._get_style(int, sv.IJKSKIP, sv.K)))

    @step.setter
    def step(self, *values):
        ijkstep = FieldmapPoints._IJKStep(*flatten_args(*values))
        self._set_style(int(ijkstep.i or 1), sv.IJKSKIP, sv.I)
        self._set_style(int(ijkstep.j or 1), sv.IJKSKIP, sv.J)
        self._set_style(int(ijkstep.k or 1), sv.IJKSKIP, sv.K)


class FieldmapScatter(FieldmapStyle):
    """Plot of nodes using symbols.

    `FieldmapScatter` plots display symbols at the data points in a field. The
    symbols may be sized according to the values of a specified variable,
    colored by the values of the contour variable, or may be uniformly sized or
    colored. Unlike contour plots, scatter plots do not require any mesh
    structure connecting the points, allowing scatter plots of irregular data.

    .. code-block:: python
        :emphasize-lines: 12,14-17

        from os import path
        import tecplot as tp
        from tecplot.constant import PlotType, SymbolType, FillMode

        examples_dir = tp.session.tecplot_examples_directory()
        infile = path.join(examples_dir, 'SimpleData', 'HeatExchanger.plt')
        dataset = tp.data.load_tecplot(infile)

        frame = tp.active_frame()
        frame.plot_type = PlotType.Cartesian2D
        plot = frame.plot()
        plot.show_scatter = True

        for z in dataset.zones():
            scatter = plot.fieldmap(z).scatter
            scatter.symbol_type = SymbolType.Geometry
            scatter.fill_mode = FillMode.UseSpecificColor
            scatter.fill_color = plot.contour(0)
            scatter.size = 1

        tp.export.save_png('fieldmap_scatter.png', 600, supersample=3)

    .. figure:: /_static/images/fieldmap_scatter.png
        :width: 300px
        :figwidth: 300px
    """
    def __init__(self, fieldmap):
        super().__init__(fieldmap, sv.SCATTER)

    @property
    def show(self):
        """Show the scatter symbols.

        :type: `boolean <bool>`

        Example usage::

            >>> plot.show_scatter = True
            >>> plot.fieldmap(2).scatter.show = True
        """
        return self._get_style(bool, sv.SHOW)

    @show.setter
    def show(self, value):
        self._set_style(bool(value), sv.SHOW)

    @property
    def symbol_type(self):
        """The `SymbolType` to use for this scatter plot.

        :type: `SymbolType`

        Possible values are: `Geometry`, `Text <SymbolType.Text>`.

        Example usage::

            >>> from tecplot.constant import SymbolType
            >>> plot.fieldmap(0).scatter.symbol_type = SymbolType.Text
        """
        return Symbol(self)._symbol_type

    @symbol_type.setter
    def symbol_type(self, value):
        Symbol(self)._symbol_type = value

    def symbol(self, symbol_type=None):
        """Returns a scatter symbol style object.

        Parameters:
            symbol_type (`SymbolType`, optional): The type of symbol to return.
                By default, this will return the active symbol type which is
                obtained from `FieldmapScatter.symbol_type`.

        Returns: `TextScatterSymbol` or `GeometryScatterSymbol`

        Example usage::

            >>> from tecplot.constant import SymbolType
            >>> plot.fieldmap(0).scatter.symbol_type = SymbolType.Text
            >>> symbol = plot.fieldmap(0).scatter.symbol()
            >>> symbol.text = 'a'
        """
        _dispatch = {
            SymbolType.Text: TextScatterSymbol,
            SymbolType.Geometry: GeometryScatterSymbol}
        return _dispatch[symbol_type or self.symbol_type](self)

    @property
    def size(self):
        """Size of the symbols to draw.

        :type: `float`

        Example usage::

            >>> plot.fieldmap(0).scatter.size = 4
        """
        return self._get_style(float, sv.FRAMESIZE)

    @size.setter
    def size(self, value):
        self._set_style(float(value), sv.FRAMESIZE)

    @property
    def size_by_variable(self):
        """Use a variable to determine relative size of symbols.

        :type: `bool`

        Example usage::

            >>> plot.scatter.variable = dataset.variable('P')
            >>> plot.fieldmap(0).scatter.size_by_variable = True
        """
        return self._get_style(bool, sv.SIZEBYVARIABLE)

    @size_by_variable.setter
    def size_by_variable(self, value):
        try:
            self._set_style(bool(value), sv.SIZEBYVARIABLE)
        except TecplotSystemError as e:
            if str(e) == str(SetValueReturnCode.ContextError1):
                msg = dedent('''\
                A scatter variable must be set using the
                    plot.scatter.variable property.''')
                raise TecplotLogicError(msg)
            else:
                raise

    @property
    def line_thickness(self):
        """Width of the lines when drawing symbols.

        :type: `float`

        Example usage::

            >>> from tecplot.constant import SymbolType
            >>> scatter = plot.fieldmap(0).scatter
            >>> scatter.symbol_type = SymbolType.Geometry
            >>> scatter.line_thickness = 1
        """
        return self._get_style(float, sv.LINETHICKNESS)

    @line_thickness.setter
    def line_thickness(self, value):
        self._set_style(float(value), sv.LINETHICKNESS)

    @property
    def color(self):
        """Line `Color` or `ContourGroup` of the drawn symbols.

        :type: `Color` or `ContourGroup`

        This can be a solid color or  a `ContourGroup` as obtained through the
        ``plot.contour`` property. Note that changing style on the
        `ContourGroup` will affect all other fieldmaps in the same `Frame` that
        use it. Example usage::

            >>> from tecplot.constant import Color
            >>> plot.fieldmap(1).scatter.color = Color.Blue

        Example of setting the color from a `ContourGroup`::

            >>> plot.fieldmap(1).scatter.color = plot.contour(1)
        """
        return color_spec(self._get_style(Color, sv.COLOR),
                          self.fieldmap.plot)

    @color.setter
    def color(self, value):
        self._set_style(color_spec(value), sv.COLOR)

    @property
    def fill_mode(self):
        """Fill mode for the background color.

        :type: `FillMode.UseSpecificColor`, `FillMode.UseLineColor`,
            `FillMode.UseBackgroundColor` or `FillMode.None_`.

        Example usage::

            >>> from tecplot.constant import Color, SymbolType, FillMode
            >>> scatter = plot.fieldmap(0).scatter
            >>> scatter.symbol_type = SymbolType.Geometry
            >>> scatter.fill_mode = FillMode.UseSpecificColor
            >>> scatter.fill_color = Color.Red
        """
        return self._get_style(FillMode, sv.FILLMODE)

    @fill_mode.setter
    def fill_mode(self, value):
        self._set_style(FillMode(value), sv.FILLMODE)

    @property
    def fill_color(self):
        """Fill or background color.

        :type: `Color`, `ContourGroup`.

        The ``fill_mode`` attribute must be set accordingly::

            >>> from tecplot.constant import Color, SymbolType, FillMode
            >>> scatter = plot.fieldmap(0).scatter
            >>> scatter.symbol_type = SymbolType.Geometry
            >>> scatter.fill_mode = FillMode.UseSpecificColor
            >>> scatter.fill_color = Color.Red
        """
        return color_spec(self._get_style(Color, sv.FILLCOLOR),
                          self.fieldmap.plot)

    @fill_color.setter
    def fill_color(self, value):
        self._set_style(color_spec(value), sv.FILLCOLOR)


class FieldmapSurfaces(FieldmapStyle):
    """Plot surfaces from volume data.

    This class controls viewing volume data as surfaces, either via a boundary
    surface or one or more planes along the ``I``, ``J``, ``K`` dimensions for
    ordered data.

    .. code-block:: python
        :emphasize-lines: 33,39,42

        import numpy as np

        import tecplot as tp
        from tecplot.constant import *
        from tecplot.data.operate import execute_equation

        # Get the active frame, setup a grid (30x30x30)
        # where each dimension ranges from 0 to 30.
        # Add variable P to the dataset and give
        # values to the data.
        frame = tp.active_frame()
        dataset = frame.dataset
        for v in ['X','Y','Z','P']:
            dataset.add_variable(v)
        zone = dataset.add_ordered_zone('Zone', (30,30,30))
        xx = np.linspace(0,30,30)
        for v,arr in zip(['X','Y','Z'],np.meshgrid(xx,xx,xx)):
            zone.values(v)[:] = arr.ravel()
        execute_equation('{P} = -10*{X} + {Y}**2 + {Z}**2')

        # Enable 3D field plot and turn on contouring
        frame.plot_type = PlotType.Cartesian3D
        plot = frame.plot()
        plot.show_contour = True

        # get a handle of the fieldmap for this zone
        fmap = plot.fieldmap(dataset.zone('Zone'))

        # set the active contour group to flood by variable P
        fmap.contour.flood_contour_group.variable = dataset.variable('P')

        # show I and J-planes through the surface
        fmap.surfaces.surfaces_to_plot = SurfacesToPlot.IJPlanes

        # show only the first and last I-planes
        # min defaults to 0, max defaults to -1
        # we set step to -1 which is equivalent
        # to the I-dimensions's max
        fmap.surfaces.i_range = None,None,-1

        # show J-planes at indices: [5, 15, 25]
        fmap.surfaces.j_range = 5,25,10

        # save image to file
        tp.export.save_png('fieldmap_surfaces_ij.png', 600, supersample=3)

    .. figure:: /_static/images/fieldmap_surfaces_ij.png
        :width: 300px
        :figwidth: 300px
    """
    def __init__(self, fieldmap):
        super().__init__(fieldmap, sv.SURFACES)

    @property
    def surfaces_to_plot(self):
        """The surfaces to show.

        :type: `SurfacesToPlot`

        Possible values: `BoundaryFaces`, `ExposedCellFaces`, `IPlanes
        <SurfacesToPlot.IPlanes>`, `JPlanes <SurfacesToPlot.JPlanes>`, `KPlanes
        <SurfacesToPlot.KPlanes>`, `IJPlanes`, `JKPlanes`, `IKPlanes`,
        `IJKPlanes`, `All <SurfacesToPlot.All>`, the python built-in `None`.

        Options such as `IJKPlanes` show planes from multiple dimensions. For
        example, the `IJPlanes` value shows both the ``I``-planes and the
        ``J``-planes. The following example shows a 3D field plot using faces
        on the boundary::

            >>> from tecplot.constant import SurfacesToPlot
            >>> frame.plot_type = PlotType.Cartesian3D
            >>> srf = frame.plot().fieldmap(0).surfaces
            >>> srf.surfaces_to_plot = SurfacesToPlot.BoundaryFaces
        """
        value = self._get_style(SurfacesToPlot, sv.SURFACESTOPLOT)
        if value == SurfacesToPlot.None_:
            return None
        else:
            return value

    @surfaces_to_plot.setter
    def surfaces_to_plot(self, surfaces):
        if surfaces is None:
            surfaces = SurfacesToPlot.None_
        self._set_style(SurfacesToPlot(surfaces), sv.SURFACESTOPLOT)

    @property
    def i_range(self):
        """`IndexRange` for the *I* dimension of ordered data.

        :type: `tuple` of `integers <int>` (min, max, step)

        This example shows ``I``-planes at ``i = [0, 2, 4, 6, 8, 10]``::

            >>> from tecplot.constant import SurfacesToPlot
            >>> srf = frame.plot().fieldmap(0).surfaces
            >>> srf.surfaces_to_plot = SurfacesToPlot.IPlanes
            >>> srf.i_range = 0, 10, 2
        """
        return self._get_style(IndexRange, sv.IRANGE)

    @i_range.setter
    def i_range(self, values):
        self._set_style(IndexRange(*values), sv.IRANGE)

    @property
    def j_range(self):
        """`IndexRange` for the *J* dimension of ordered data.

        :type: `tuple` of `integers <int>` (min, max, step)

        This example shows all ``J``-planes starting with ``j = 10`` up to the
        maximum ``J``-plane of the associated `Zone <data_access>`::

            >>> from tecplot.constant import SurfacesToPlot
            >>> srf = frame.plot().fieldmap(0).surfaces
            >>> srf.surfaces_to_plot = SurfacesToPlot.JPlanes
            >>> srf.j_range = 10, None, 1
        """
        return self._get_style(IndexRange, sv.JRANGE)

    @j_range.setter
    def j_range(self, values):
        self._set_style(IndexRange(*values), sv.JRANGE)

    @property
    def k_range(self):
        """`IndexRange` for the *K* dimension of ordered data.

        :type: `tuple` of `integers <int>` (min, max, step)

        This example shows all ``K``-planes starting with the first up to 5
        from the last ``K``-plane of the associated `Zone <data_access>`::

            >>> from tecplot.constant import SurfacesToPlot
            >>> srf = frame.plot().fieldmap(0).surfaces
            >>> srf.surfaces_to_plot = SurfacesToPlot.KPlanes
            >>> srf.k_range = None, -5
        """
        return self._get_style(IndexRange, sv.KRANGE)

    @k_range.setter
    def k_range(self, values):
        self._set_style(IndexRange(*values), sv.KRANGE)


class FieldmapVector(FieldmapStyle):
    """Field plot of arrows.

    Before doing anything with vector plots, one must set the variables to be
    used for the ``(U, V, W)`` coordinates. This is done through the plot
    object. Once set, the vectors can be displayed and manipulated using this
    class:

    .. code-block:: python
        :emphasize-lines: 23-25,31-36

        import numpy as np
        import tecplot as tp
        from tecplot.data.operate import execute_equation
        from tecplot.constant import (PlotType, PointsToPlot, VectorType,
                                      ArrowheadStyle)

        frame = tp.active_frame()
        dataset = frame.dataset
        for v in ['X','Y','Z','P','Q','R']:
            dataset.add_variable(v)
        zone = dataset.add_ordered_zone('Zone', (30,30,30))
        xx = np.linspace(0,30,30)
        for v,arr in zip(['X','Y','Z'],np.meshgrid(xx,xx,xx)):
            zone.values(v)[:] = arr.ravel()
        execute_equation('{P} = -10 * {X}    +      {Y}**2 + {Z}**2')
        execute_equation('{Q} =       {X}    - 10 * {Y}    - {Z}**2')
        execute_equation('{R} =       {X}**2 +      {Y}**2 - {Z}   ')

        frame.plot_type = PlotType.Cartesian3D
        plot = frame.plot()
        plot.contour(0).variable = dataset.variable('P')
        plot.contour(0).colormap_name = 'Two Color'
        plot.vector.u_variable = dataset.variable('P')
        plot.vector.v_variable = dataset.variable('Q')
        plot.vector.w_variable = dataset.variable('R')
        plot.show_vector = True

        points = plot.fieldmap(0).points
        points.points_to_plot = PointsToPlot.AllNodes
        points.step = (5,3,2)

        vector = plot.fieldmap(0).vector
        vector.show = True
        vector.vector_type = VectorType.MidAtPoint
        vector.arrowhead_style = ArrowheadStyle.Filled
        vector.color = plot.contour(0)
        vector.line_thickness = 0.4

        # save image to file
        tp.export.save_png('fieldmap_vector.png', 600, supersample=3)

    .. figure:: /_static/images/fieldmap_vector.png
        :width: 300px
        :figwidth: 300px
    """
    def __init__(self, fieldmap):
        super().__init__(fieldmap, sv.VECTOR)

    @property
    def show(self):
        """Enable drawing vectors on the plot.

        :type: `bool`

        Example usage::

            >>> plot.show_vector = True
            >>> plot.fieldmap(0).vector.show = True
        """
        return self._get_style(bool, sv.SHOW)

    @show.setter
    def show(self, value):
        self._set_style(bool(value), sv.SHOW)

    @property
    def vector_type(self):
        """Anchor point of the drawn vectors.

        :type: `VectorType`

        Possible values: `TailAtPoint`, `HeadAtPoint`, `MidAtPoint`, `HeadOnly`.

        Example usage::

            >>> from tecplot.constant import VectorType
            >>> plot.fieldmap(0).vector.vector_type = VectorType.MidAtPoint
        """
        return self._get_style(VectorType, sv.VECTORTYPE)

    @vector_type.setter
    def vector_type(self, value):
        self._set_style(VectorType(value), sv.VECTORTYPE)

    @property
    def tangent_only(self):
        """Show only tangent vectors.

        Set to `True` to display **only** the tangent component of vectors.
        Tangent vectors are drawn on 3D surfaces only where it is possible to
        determine a vector normal to the surface. A plot where multiple
        surfaces intersect each other using common nodes is a case where
        tangent vectors are not drawn because there is more than one normal to
        choose from. An example of this would be a volume ``IJK``-ordered zone
        where both the ``I`` and ``J``-planes are shown. If tangent vectors
        cannot be drawn, then regular vectors are plotted instead.

        :type: `bool`

        Example usage::

            >>> plot.fieldmap(0).vector.tangent_only = True
        """
        return self._get_style(bool, sv.ISTANGENT)

    @tangent_only.setter
    def tangent_only(self, value):
        self._set_style(bool(value), sv.ISTANGENT)

    @property
    def color(self):
        """The `Color` or `ContourGroup` to use when drawing vectors.

        :type: `Color` or `ContourGroup`

        FieldmapVectors can be a solid color or be colored by a `ContourGroup`
        as obtained through the ``plot.contour`` property. Note that changing
        style on this `ContourGroup` will affect all other fieldmaps on the
        same `Frame` that use it. Example usage::

            >>> from tecplot.constant import Color
            >>> plot.fieldmap(1).vector.color = Color.Blue

        Example of setting the color from a `ContourGroup`::

            >>> plot.fieldmap(1).vector.color = plot.contour(1)
        """
        return color_spec(self._get_style(Color, sv.COLOR), self.fieldmap.plot)

    @color.setter
    def color(self, value):
        self._set_style(color_spec(value), sv.COLOR)

    @property
    def arrowhead_style(self):
        """The `ArrowheadStyle` drawn.

        :type: `ArrowheadStyle`

        Possible values: `Plain`, `Filled <ArrowheadStyle.Filled>`,
        `Hollow <ArrowheadStyle.Hollow>`.

        Example usage::

            >>> from tecplot.constant import ArrowheadStyle
            >>> plot.fieldmap(0).vector.arrowhead_style = ArrowheadStyle.Filled
        """
        return self._get_style(ArrowheadStyle, sv.ARROWHEADSTYLE)

    @arrowhead_style.setter
    def arrowhead_style(self, value):
        self._set_style(ArrowheadStyle(value), sv.ARROWHEADSTYLE)

    @property
    def line_pattern(self):
        """The `LinePattern` used to draw the arrow line.

        :type: `LinePattern`

        Possible values: `Solid <LinePattern.Solid>`, `Dashed`, `DashDot`,
        `Dotted`, `LongDash`, `DashDotDot`.

        Example usage::

            >>> from tecplot.constant import LinePattern
            >>> vector = plot.fieldmap(0).vector
            >>> vector.line_pattern = LinePattern.DashDot
        """
        return self._get_style(LinePattern, sv.LINEPATTERN)

    @line_pattern.setter
    def line_pattern(self, value):
        self._set_style(LinePattern(value), sv.LINEPATTERN)

    @property
    def line_thickness(self):
        """The width of the arrow line.

        :type: `float` (percentage of `Frame` height)

        Example usage::

            >>> from tecplot.constant import LinePattern
            >>> vector = plot.fieldmap(0).vector.line_thickness = 0.7
        """
        return self._get_style(float, sv.LINETHICKNESS)

    @line_thickness.setter
    def line_thickness(self, value):
        self._set_style(float(value), sv.LINETHICKNESS)

    @property
    def pattern_length(self):
        """Length of the pattern used when drawing vector lines.

        :type: `float` (percentage of `Frame` height)

        Example usage::

            >>> from tecplot.constant import LinePattern
            >>> vector = plot.fieldmap(0).vector
            >>> vector.line_pattern = LinePattern.Dashed
            >>> vector.pattern_length = 3.5
        """
        return self._get_style(float, sv.PATTERNLENGTH)

    @pattern_length.setter
    def pattern_length(self, value):
        self._set_style(float(value), sv.PATTERNLENGTH)


class Fieldmap(Style):
    """Style control for a specific `Zone <data_access>` attached to a specific `Frame`.

    The fieldmap connects the plotting style and various elements of the plot
    to a specific `Zone <data_access>` in the `Dataset` attached to a specific `Frame`. This
    object is obtained through the ``plot.fieldmap()`` method:

    .. code-block:: python
        :emphasize-lines: 16-17

        import os
        import numpy
        import tecplot

        examples_dir = tecplot.session.tecplot_examples_directory()
        infile = os.path.join(examples_dir, 'SimpleData', 'F18.lay')
        tecplot.load_layout(infile)
        frame = tecplot.active_frame()
        plot = frame.plot()
        dataset = frame.dataset

        plot.contour(0).colormap_name = 'GrayScale'
        plot.contour(0).legend.show = False

        for zone_name in ['left wing', 'right wing']:
            fmap = frame.plot().fieldmap(dataset.zone(zone_name))
            fmap.contour.flood_contour_group = plot.contour(1)

        plot.contour(1).colormap_name = 'Sequential - Yellow/Green/Blue'
        plot.contour(1).levels.reset_levels(numpy.linspace(-0.07, 0.07, 50))

        tecplot.export.save_png('F18_wings.png', 600, supersample=3)

    .. figure:: /_static/images/fieldmap.png
        :width: 300px
        :figwidth: 300px
    """
    def __init__(self, index, plot):
        self.index = Index(index)
        self.plot = plot
        super().__init__(sv.FIELDMAP, uniqueid=self.plot.frame.uid,
                         offset1=self.index, multiset=True)

    def __eq__(self, that):
        return (isinstance(that, type(self)) and
                self.plot == that.plot and
                self.index == that.index)

    def __ne__(self, that):
        return not (self == that)

    @property
    def show(self):
        """Display this fieldmap on the plot.

        :type: `bool`

        Example usage for turning on all fieldmaps::

            >>> for fmap in plot.fieldmaps():
            ...     fmap.show = True
        """
        return self.index in self.plot.active_fieldmap_indices

    @show.setter
    def show(self, show):
        assignment = AssignOp.PlusEquals if show else AssignOp.MinusEquals
        session.set_style({self.index}, sv.ACTIVEFIELDMAPS,
                          assignmodifier=assignment,
                          uniqueid=self.plot.frame.uid)

    @property
    def group(self):
        """Zero-based group number for this `Fieldmap`.

        :type: `integer <int>`

        This is a piece of auxiliary data and can be useful for identifying a
        subset of fieldmaps. For example, to loop over all fieldmaps that have
        group set to 4::

            >>> plot.fieldmap(0).group = 4
            >>> plot.fieldmap(3).group = 4
            >>> for fmap in filter(lambda f: f.group == 4, plot.fieldmaps()):
            ...     print(fmap.index)
            0
            3
        """
        return self._get_style(Index, sv.GROUP)

    @group.setter
    def group(self, value):
        self._set_style(Index(value), sv.GROUP)

    @property
    def zones(self):
        """List of zones used by this fieldmap.

        :type: generator of `Zones <data_access>`

        Example usage::

            >>> for zone in fieldmap.zones:
            ...     print(zone.name)
            Zone 1
            Zone 2
        """
        with self.plot.frame.activated():
            success, zones_ptr = _tecutil.FieldMapGetZones(self.index + 1)
            if not success:
                raise TecplotSystemError()
        zones_indexset = cast(zones_ptr, IndexSet)
        zone_indices = set(zones_indexset)
        zones_indexset.dealloc()
        for index in zone_indices:
            yield self.plot.frame.dataset.zone(index)

    @property
    def contour(self):
        """`FieldmapContour` style including flooding, lines and line coloring.

        :type: `FieldmapContour`
        """
        return FieldmapContour(self)

    @property
    def edge(self):
        """`FieldmapEdge` style control for boundary lines.

        :type: `FieldmapEdge`
        """
        return FieldmapEdge(self)

    @property
    def mesh(self):
        """`FieldmapMesh` style lines connecting neighboring data points.

        :type: `FieldmapMesh`
        """
        return FieldmapMesh(self)

    @property
    def scatter(self):
        """`FieldmapScatter` style for scatter plots.

        :type: `FieldmapScatter`
        """
        return FieldmapScatter(self)

    @property
    def surfaces(self):
        """`FieldmapSurfaces` object to control which surfaces to draw.

        :type: `FieldmapSurfaces`
        """
        return FieldmapSurfaces(self)

    @property
    def points(self):
        """`FieldmapPoints` object to control which points to draw.

        :type: `FieldmapPoints`
        """
        return FieldmapPoints(self)

    @property
    def vector(self):
        """`FieldmapVector` style for vector field plots using arrows.

        :type: `FieldmapVector`
        """
        return FieldmapVector(self)

    @property
    def show_iso_surfaces(self):
        """(`bool`) Enable drawing of Iso-surfaces.

        :type: `boolean <bool>`
        """
        return self._get_style(bool, sv.VOLUMEMODE, sv.VOLUMEOBJECTSTOPLOT,
                               sv.SHOWISOSURFACES)

    @show_iso_surfaces.setter
    def show_iso_surfaces(self, show):
        self._set_style(bool(show), sv.VOLUMEMODE, sv.VOLUMEOBJECTSTOPLOT,
                        sv.SHOWISOSURFACES)

    @property
    def show_slices(self):
        """(`bool`) Enable drawing of slice surfaces.

        :type: `boolean <bool>`
        """
        return self._get_style(bool, sv.VOLUMEMODE, sv.VOLUMEOBJECTSTOPLOT,
                               sv.SHOWSLICES)

    @show_slices.setter
    def show_slices(self, show):
        self._set_style(bool(show), sv.VOLUMEMODE, sv.VOLUMEOBJECTSTOPLOT,
                        sv.SHOWSLICES)

    @property
    def show_streamtraces(self):
        """(`bool`) Enable drawing of streamtraces.

        :type: `boolean <bool>`
        """
        return self._get_style(bool, sv.VOLUMEMODE, sv.VOLUMEOBJECTSTOPLOT,
                               sv.SHOWSTREAMTRACES)

    @show_streamtraces.setter
    def show_streamtraces(self, show):
        self._set_style(bool(show), sv.VOLUMEMODE, sv.VOLUMEOBJECTSTOPLOT,
                        sv.SHOWSTREAMTRACES)


class FieldmapEffects(FieldmapStyle):
    """Clipping and blanking style control.

    This object controls value blanking and clipping from plane slices for
    this fieldmap.
    """
    def __init__(self, fieldmap):
        super().__init__(fieldmap, sv.EFFECTS)

    @property
    def value_blanking(self):
        """Enable value blanking effect for this fieldmap.

        :type: `boolean <bool>`

        Example usage::

            >>> plot.fieldmap(0).effects.value_blanking = True
        """
        return self._get_style(bool, sv.USEVALUEBLANKING)

    @value_blanking.setter
    def value_blanking(self, value):
        self._set_style(bool(value), sv.USEVALUEBLANKING)

    @property
    def clip_planes(self):
        """Clip planes to use when drawing this fieldmap.

        :type: `list` of `integers <int>` [0-5] or `None`

        Example usage::

            >>> plot.fieldmap(0).effects.clip_planes = [0,1,2]
        """
        value = self._get_style(list, sv.USECLIPPLANES)
        return value if value else None

    @clip_planes.setter
    def clip_planes(self, value):
        if value is None:
            value = list()
        if not isinstance(value, Iterable):
            value = [value]
        self._set_style(list(value), sv.USECLIPPLANES,
                        **{sv.ASSIGNMODIFIER: AssignOp.Equals})


class FieldmapEffects3D(FieldmapEffects):
    """Lighting and translucency style control.

    .. code-block:: python
        :emphasize-lines: 23-25

        import os

        import tecplot as tp
        from tecplot.constant import LightingEffect, PlotType, SurfacesToPlot

        examples_dir = tp.session.tecplot_examples_directory()
        datafile = os.path.join(examples_dir, 'SimpleData', 'F18.plt')
        dataset = tp.data.load_tecplot(datafile)
        frame = dataset.frame

        # Enable 3D field plot, turn on contouring and translucency
        frame.plot_type = PlotType.Cartesian3D
        plot = frame.plot()
        plot.show_contour = True
        plot.use_translucency = True

        # adjust effects for every fieldmap in this dataset
        for zone in dataset.zones():
            fmap = plot.fieldmap(zone)
            fmap.contour.flood_contour_group.variable = dataset.variable('S')
            fmap.surfaces.surfaces_to_plot = SurfacesToPlot.BoundaryFaces

            eff = fmap.effects
            eff.lighting_effect = LightingEffect.Paneled
            eff.surface_translucency = 30

        # save image to file
        tp.export.save_png('fieldmap_effects3d.png', 600, supersample=3)

    .. figure:: /_static/images/fieldmap_effects3d.png
        :width: 300px
        :figwidth: 300px
    """

    @property
    def lighting_effect(self):
        """The type of lighting effect to render.

        :type: `LightingEffect`

        Possible values:

        `Paneled <LightingEffect.Paneled>`
            Within each cell, the color assigned to each area by shading or
            contour flooding is tinted by a shade constant across the cell.
            This shade is based on the orientation of the cell relative to your
            3D light source.

        `Gouraud <LightingEffect.Gouraud>`
            This plot type offers smoother, more continuous shading than
            `Paneled <LightingEffect.Paneled>` shading, but it results in
            slower plotting and larger vector images. `Gouraud
            <LightingEffect.Gouraud>` shading is not continuous across zone
            boundaries unless face neighbors are specified in the data and is
            not available for finite element volume zones when blanking is
            active in which case, the zone's lighting effect reverts to
            `Paneled <LightingEffect.Paneled>` shading in this case.

        If ``IJK``-ordered data with `FieldmapSurfaces.surfaces_to_plot` is set
        to `SurfacesToPlot.ExposedCellFaces`, faces exposed by blanking will
        revert to `Paneled <LightingEffect.Paneled>` shading.

        Example usage::

            >>> from tecplot.constant import LightingEffect
            >>> effects = plot.fieldmap(0).effects
            >>> effects.lighting_effect = LightingEffect.Paneled
        """
        return self._get_style(LightingEffect, sv.LIGHTINGEFFECT)

    @lighting_effect.setter
    def lighting_effect(self, value):
        self._set_style(LightingEffect(value), sv.LIGHTINGEFFECT)

    @property
    def use_translucency(self):
        """Enable translucency of all drawn surfaces for this fieldmap.

        :type: `boolean <bool>`

        This enables translucency controlled by the ``surface_translucency``
        attribute::

            >>> effects = plot.fieldmap(0).effects
            >>> effects.use_translucency = True
            >>> effects.surface_translucency = 50
        """
        return self._get_style(bool, sv.USETRANSLUCENCY)

    @use_translucency.setter
    def use_translucency(self, value):
        self._set_style(bool(value), sv.USETRANSLUCENCY)

    @property
    def surface_translucency(self):
        """Translucency of all drawn surfaces for this fieldmap.

        :type: `integer <int>` in percent

        The ``use_translucency`` attribute must be set to `True`::

            >>> effects = plot.fieldmap(0).effects
            >>> effects.use_translucency = True
            >>> effects.surface_translucency = 50
        """
        return self._get_style(int, sv.SURFACETRANSLUCENCY)

    @surface_translucency.setter
    def surface_translucency(self, value):
        self._set_style(int(value), sv.SURFACETRANSLUCENCY)


class FieldmapShade(FieldmapStyle):
    """Fill color for displayed surfaces on 2D field plots.

    Although most commonly used with 3D surfaces (see `FieldmapShade3D`), shade
    plots can be used to flood 2D plots with solid colors.

    .. code-block:: python
        :emphasize-lines: 20

        import os
        import random
        import tecplot
        from tecplot.constant import Color, PlotType

        random.seed(1)

        examples_dir = tecplot.session.tecplot_examples_directory()
        datafile = os.path.join(examples_dir, 'SimpleData', 'F18.plt')
        dataset = tecplot.data.load_tecplot(datafile)
        frame = dataset.frame
        frame.plot_type = PlotType.Cartesian2D
        plot = frame.plot()

        for zone in dataset.zones():
            color = Color(random.randint(0,63))
            while color == Color.White:
                color = Color(random.randint(0,63))
            fmap = plot.fieldmap(zone)
            fmap.shade.color = color

        tecplot.export.save_png('fieldmap_shade2d.png', 600, supersample=3)

    .. figure:: /_static/images/fieldmap_shade2d.png
        :width: 300px
        :figwidth: 300px
    """
    def __init__(self, fieldmap):
        super().__init__(fieldmap, sv.SHADE)

    @property
    def show(self):
        """FieldmapShade the drawn surfaces.

        :type: `bool`

        Example usage::

            >>> plot.fieldmap(0).shade.show = False
        """
        return self._get_style(bool, sv.SHOW)

    @show.setter
    def show(self, value):
        self._set_style(bool(value), sv.SHOW)

    @property
    def color(self):
        """Fill `Color` of the shade.

        :type: `Color`

        Example usage::

            >>> from tecplot.constant import Color
            >>> plot.fieldmap(0).shade.color = Color.Blue
        """
        return self._get_style(Color, sv.COLOR)

    @color.setter
    def color(self, value):
        self._set_style(Color(value), sv.COLOR)


class FieldmapShade3D(FieldmapShade):
    """Fill color for displayed surfaces on 3D field plots.

    This class inherits all functionality and purpose from `FieldmapShade` and
    adds the ability to turn on or off the lighting effect. In 3D plots,
    fieldmap effects (translucency and lighting) cause color variation
    (shading) throughout the zones. Shading can can be useful in discerning the
    shape of the data:

    .. code-block:: python
        :emphasize-lines: 21-22

        import os
        import random
        import tecplot
        from tecplot.constant import Color, PlotType, SurfacesToPlot

        random.seed(1)

        examples_dir = tecplot.session.tecplot_examples_directory()
        datafile = os.path.join(examples_dir, 'SimpleData', 'F18.plt')
        dataset = tecplot.data.load_tecplot(datafile)
        frame = dataset.frame
        frame.plot_type = PlotType.Cartesian3D
        plot = frame.plot()

        for zone in dataset.zones():
            color = Color(random.randint(0,63))
            while color == Color.White:
                color = Color(random.randint(0,63))
            fmap = plot.fieldmap(zone)
            fmap.surfaces.surfaces_to_plot = SurfacesToPlot.BoundaryFaces
            fmap.shade.color = color
            fmap.shade.use_lighting_effect = False

        tecplot.export.save_png('fieldmap_shade3d.png', 600, supersample=3)

    .. figure:: /_static/images/fieldmap_shade3d.png
        :width: 300px
        :figwidth: 300px
    """

    @property
    def use_lighting_effect(self):
        """Draw a lighting effect on the shaded surfaces.

        :type: `bool`

        Example usage::

            >>> plot.fieldmap(0).shade.use_lighting_effect = False
        """
        return self._get_style(bool, sv.USELIGHTINGEFFECT)

    @use_lighting_effect.setter
    def use_lighting_effect(self, value):
        self._set_style(bool(value), sv.USELIGHTINGEFFECT)


class Cartesian2DFieldmap(Fieldmap):
    @property
    def effects(self):
        """`FieldmapEffects` style control for clipping and blanking effects.

        :type: `FieldmapEffects`
        """
        return FieldmapEffects(self)

    @property
    def shade(self):
        """`FieldmapShade` style control for surface shading.

        :type: `FieldmapShade`
        """
        return FieldmapShade(self)


class Cartesian3DFieldmap(Fieldmap):
    @property
    def effects(self):
        """`FieldmapEffects3D` style control for blanking and lighting effects.

        :type: `FieldmapEffects3D`
        """
        return FieldmapEffects3D(self)

    @property
    def shade(self):
        """`FieldmapShade3D` style control for surface shading.

        :type: `FieldmapShade3D`
        """
        return FieldmapShade3D(self)
