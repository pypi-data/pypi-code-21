from builtins import int

import numbers
import six

from collections import Iterable

from ..constant import *
from ..exception import *
from .. import session, version
from ..tecutil import Index, sv, color_spec


class IsosurfaceGroupStyle(session.Style):
    def __init__(self, isosurface, *sv_args):
        self.isosurface = isosurface
        kw = dict(uniqueid=isosurface.plot.frame.uid,
                  offset1=isosurface.index)
        super().__init__(isosurface._sv, *sv_args, **kw)


class IsosurfaceMesh(IsosurfaceGroupStyle):
    """Mesh attributes of the isosurface group.

    .. code-block:: python
        :emphasize-lines: 20-22

        import os
        import tecplot as tp
        from tecplot.constant import *

        examples_dir = tp.session.tecplot_examples_directory()
        datafile = os.path.join(examples_dir, 'OneraM6wing', 'OneraM6_SU2_RANS.plt')
        dataset = tp.data.load_tecplot(datafile)

        plot = tp.active_frame().plot()
        plot.show_isosurfaces = True
        plot.contour(0).colormap_name = 'Magma'
        plot.contour(0).variable = dataset.variable('Mach')
        plot.contour(0).legend.show = False

        iso = plot.isosurface(0)
        iso.show = True
        iso.definition_contour_group = plot.contour(0)
        iso.isosurface_selection = IsoSurfaceSelection.OneSpecificValue
        iso.isosurface_values = 1
        iso.mesh.show = True
        iso.mesh.color = Color.Mahogany
        iso.mesh.line_thickness = 0.4

        view = plot.view
        view.psi = 65.777
        view.theta = 166.415
        view.alpha = -1.05394
        view.position = (-23.92541680486183, 101.8931504712126, 47.04269529295333)
        view.width = 1.3844

        tp.export.save_png('isosurface_mesh.png', 600, supersample=3)

    .. figure:: /_static/images/isosurface_mesh.png
        :width: 300px
        :figwidth: 300px
    """

    def __init__(self, mesh):
        super().__init__(mesh, sv.MESH)

    @property
    def show(self):
        """Display the mesh on isosurfaces.

        :type: `boolean <bool>`

        Example usage::

            >>> plot.isosurface(0).mesh.show = True
        """
        return self._get_style(bool, sv.SHOW)

    @show.setter
    def show(self, value):
        self._set_style(bool(value), sv.SHOW)

    @property
    def color(self):
        """Isosurface mesh color.

        :type: `Color` or `ContourGroup`

        Iso-surface mesh lines can be a solid color or be colored by a
        `ContourGroup` as obtained through the ``plot.contour`` property.

        Example usage::

            >>> plot.isosurface(0).mesh.show = True
            >>> plot.isosurface(0).mesh.color = Color.Blue
        """
        return color_spec(self._get_style(Color, sv.COLOR),
                          self.isosurface.plot)

    @color.setter
    def color(self, value):
        self._set_style(color_spec(value), sv.COLOR)

    @property
    def line_thickness(self):
        """Isosurface mesh line thickness.

        :type: `float`

        Suggested values are .002, .1, .4, .8, 1.5

        Example usage::

            >>> plot.isosurface(0).mesh.show = True
            >>> plot.isosurface(0).mesh.line_thickness = .4
        """
        return self._get_style(float, sv.LINETHICKNESS)

    @line_thickness.setter
    def line_thickness(self, value):
        self._set_style(float(value), sv.LINETHICKNESS)


class IsosurfaceContour(IsosurfaceGroupStyle):
    """Contour attributes of the isosurface group.

    .. code-block:: python
        :emphasize-lines: 22-25

        import os
        import tecplot as tp
        from tecplot.constant import *

        examples_dir = tp.session.tecplot_examples_directory()
        datafile = os.path.join(examples_dir, 'OneraM6wing', 'OneraM6_SU2_RANS.plt')
        dataset = tp.data.load_tecplot(datafile)

        plot = tp.active_frame().plot()
        plot.show_isosurfaces = True
        plot.contour(0).colormap_name = 'Magma'
        plot.contour(0).variable = dataset.variable('Mach')
        plot.contour(0).legend.show = False

        iso = plot.isosurface(0)
        iso.show = True
        iso.definition_contour_group = plot.contour(0)
        iso.isosurface_selection = IsoSurfaceSelection.OneSpecificValue
        iso.isosurface_values = 1


        plot.contour(1).variable = dataset.variable('Density')
        iso.contour.show = True
        iso.contour.contour_type = ContourType.PrimaryValue
        iso.contour.flood_contour_group = plot.contour(1)


        view = plot.view
        view.psi = 65.777
        view.theta = 166.415
        view.alpha = -1.05394
        view.position = (-23.92541680486183, 101.8931504712126, 47.04269529295333)
        view.width = 1.3844

        tp.export.save_png('isosurface_contour.png', 600, supersample=3)

    .. figure:: /_static/images/isosurface_contour.png
        :width: 300px
        :figwidth: 300px
    """

    def __init__(self, contour):
        self.plot = contour.plot
        super().__init__(contour, sv.CONTOUR)

    @property
    def use_lighting_effect(self):
        """Enable lighting effect.

        :type: `Boolean <bool>`

        When set to `True`, the lighting effect may be selected with the
        `IsosurfaceEffects.lighting_effect` attribute.

        Example usage::

            >>> plot.isosurface(0).contour.use_lighting_effect = True
            >>> plot.isosurface(0).effects.lighting_effect = LightingEffect.Paneled
        """
        return self._get_style(bool, sv.USELIGHTINGEFFECT)

    @use_lighting_effect.setter
    def use_lighting_effect(self, value):
        self._set_style(bool(value), sv.USELIGHTINGEFFECT)

    @property
    def show(self):
        """Show contours on isosurfaces.

        :type: `boolean <bool>`

        Example usage::

            >>> plot.isosurface(0).contour.show = True
        """
        return self._get_style(bool, sv.SHOW)

    @show.setter
    def show(self, value):
        self._set_style(bool(value), sv.SHOW)

    @property
    def contour_type(self):
        """Contour display type.

        :type: `ContourType`

        * `ContourType.Lines` - Draws lines of constant value of the
          specified contour variable.
        * `ContourType.Flood` - Floods regions between contour lines
          with colors from a color map.
          The distribution of colors used for contour flooding may be banded or
          continuous. When banded distribution is used for flooding,
          a solid color is used between contour levels.
          If continuous color distribution is used, the flood
          color will vary linearly in all directions.
        * `ContourType.Overlay` - Combines the above two options.
        * `ContourType.AverageCell` - Floods cells or finite elements with
          colors from a color map according to the average value of the contour
          variable over the data points bounding the cell.
          If the variables are located at the nodes, the values at the
          nodes are averaged. If the variables are cell-centered, the
          cell-centered values are averaged to the nodes and the nodes
          are then averaged.
        * `ContourType.PrimaryValue` - Floods cells or finite elements with
          colors from a color map according to the primary value of the contour
          variable for each cell. If the variable is cell centered, the
          primary value is the value assigned to the cell. If the variable
          is node located, the primary value comes from the lowest index
          node in the cell. If the variables are located at the nodes, the
          value of the lowest indexed node in the cell is used. When plotting
          IJK-ordered, FE-brick or FE-tetra cells, each face is considered
          independently of the other faces. You may get different colors on
          the different faces of the same cell.
          If the variables are cell-centered, the cell-centered value is
          used directly. When plotting I, J, or K-planes in 3D, the cell
          on the positive side of the plane supplies the value, except
          in the case of the last plane, where the cell on the negative
          side supplies the value.

        Example usage::

            >>> plot.isosurface(0).contour.show = True
            >>> plot.isosurface(0).contour.contour_type = ContourType.Flood
        """
        return self._get_style(ContourType, sv.CONTOURTYPE)

    @contour_type.setter
    def contour_type(self, value):
        self._set_style(ContourType(value), sv.CONTOURTYPE)

    @property
    def flood_contour_group_index(self):
        """The `Index` of the `ContourGroup` to use for flooding.

        :type: `Index` (zero-based index)

        This property sets and gets, by `Index`, the `ContourGroup` used for
        flooding. Changing style on this `ContourGroup` will affect all
        fieldmaps on the same `Frame` that use it.

        Example usage::

            >>> contour = plot.isosurface(0).contour
            >>> contour.flood_contour_group_index = 1
        """
        return self._get_style(Index, sv.FLOODCOLORING)

    @flood_contour_group_index.setter
    def flood_contour_group_index(self, index):
        self._set_style(Index(index), sv.FLOODCOLORING)

    @property
    def flood_contour_group(self):
        """Contour group to use for flooding.

        :type: `ContourGroup`

        Changing style on this `ContourGroup` will affect all
        fieldmaps on the same `Frame` that use it.

        Example usage::

            >>> group = plot.contour(1)
            >>> contour = plot.isosurface(1).contour
            >>> contour.flood_contour_group = group
        """
        return self.plot.contour(self.flood_contour_group_index)

    @flood_contour_group.setter
    def flood_contour_group(self, flood_contour_group):
        self.flood_contour_group_index = flood_contour_group.index

    @property
    def line_contour_group_index(self):
        """The `Index` of the `ContourGroup` to use for contour lines.

        :type: `integer <int>` (zero-based index)

        This property sets and gets, by `Index`, the `ContourGroup` used for
        line placement. Although all properties of the `ContourGroup` can be
        manipulated through this object, many of them (i.e., color) will not
        affect the lines unless the `FieldmapContour.line_color` is set to the
        same `ContourGroup`. Note that changing style on this `ContourGroup`
        will affect all other fieldmaps on the same `Frame` that use it.

        Example usage::

            >>> contour = plot.isosurface(0).contour
            >>> contour.line_contour_group_index = 2
        """
        return self._get_style(Index, sv.LINECONTOURGROUP)

    @line_contour_group_index.setter
    def line_contour_group_index(self, index):
        self._set_style(Index(index), sv.LINECONTOURGROUP)

    @property
    def line_contour_group(self):
        """The contour group to use for contour lines.

        :type: `ContourGroup`

        Note that changing style on this `ContourGroup`
        will affect all other fieldmaps on the same `Frame` that use it.

        Example usage::

            >>> contour = plot.isosurface(0).contour
            >>> group = plot.contour(1)
            >>> contour.line_contour_group = group
        """
        return self.plot.contour(self.line_contour_group_index)

    @line_contour_group.setter
    def line_contour_group(self, contour_group):
        self.line_contour_group_index = contour_group.index

    @property
    def line_color(self):
        """`Color` of contour lines.

        :type: `Color` or `ContourGroup`

        Contour lines can be a solid color or be colored by a
        `ContourGroup` as obtained through the ``plot.contour`` property.

        Example usage::

            >>> plot.show_isosurfaces = True
            >>> plot.isosurface(0).contour.line_color = Color.Blue
        """
        return color_spec(self._get_style(Color, sv.COLOR),
                          self.isosurface.plot)

    @line_color.setter
    def line_color(self, value):
        self._set_style(color_spec(value), sv.COLOR)

    @property
    def line_thickness(self):
        """Contour line thickness as a percentage of frame width.

        Suggested values are one of: **.02, .1, .4, .8, 1.5**

        :type: `float`

        Example usage::

            >>> plot.show_isosurfaces = True
            >>> plot.isosurface(0).contour.line_thickness = .4
        """
        return self._get_style(float, sv.LINETHICKNESS)

    @line_thickness.setter
    def line_thickness(self, value):
        self._set_style(float(value), sv.LINETHICKNESS)


class IsosurfaceEffects(IsosurfaceGroupStyle):
    """Effects of the isosurface group.

    .. code-block:: python
        :emphasize-lines: 21-23

        import os
        import tecplot as tp
        from tecplot.constant import *

        examples_dir = tp.session.tecplot_examples_directory()
        datafile = os.path.join(examples_dir, 'OneraM6wing', 'OneraM6_SU2_RANS.plt')
        dataset = tp.data.load_tecplot(datafile)

        plot = tp.active_frame().plot()
        plot.show_isosurfaces = True
        plot.contour(0).colormap_name = 'Magma'
        plot.contour(0).variable = dataset.variable('Mach')
        plot.contour(0).legend.show = False

        iso = plot.isosurface(0)
        iso.show = True
        iso.definition_contour_group = plot.contour(0)
        iso.isosurface_selection = IsoSurfaceSelection.ThreeSpecificValues
        iso.isosurface_values = [.95,1.0,1.1]

        iso.effects.lighting_effect = LightingEffect.Paneled
        iso.effects.use_translucency = True
        iso.effects.surface_translucency = 80


        view = plot.view
        view.psi = 65.777
        view.theta = 166.415
        view.alpha = -1.05394
        view.position = (-23.92541680486183, 101.8931504712126, 47.04269529295333)
        view.width = 1.3844

        tp.export.save_png('isosurface_effects.png', 600, supersample=3)

    .. figure:: /_static/images/isosurface_effects.png
        :width: 300px
        :figwidth: 300px
    """

    def __init__(self, contour):
        super().__init__(contour, sv.EFFECTS)

    @property
    def lighting_effect(self):
        """Lighting effect.

        :type: `LightingEffect`

        Isosurface lighting effects must be enabled by setting
        `IsosurfaceShade.use_lighting_effect` to `True` when setting this value.

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

            >>> plot.isosurface(0).shade.use_lighting_effect = True
            >>> plot.isosurface(0).effects.lighting_effect = LightingEffect.Paneled
        """
        return self._get_style(LightingEffect, sv.LIGHTINGEFFECT)

    @lighting_effect.setter
    def lighting_effect(self, value):
        self._set_style(LightingEffect(value), sv.LIGHTINGEFFECT)

    @property
    def surface_translucency(self):
        """Surface translucency of the isosurface group.

        :type: `integer <int>`

        Iso-surface surface translucency must be enabled by setting
        `IsosurfaceEffects.use_translucency` = `True` when setting this value.


        Valid translucency values range from one (opaque) to 99 (translucent).

        Example usage::

            >>> plot.isosurface(0).effects.use_translucency = True
            >>> plot.isosurface(0).effects.surface_translucency = 20
        """
        return self._get_style(int, sv.SURFACETRANSLUCENCY)

    @surface_translucency.setter
    def surface_translucency(self, value):
        self._set_style(int(value), sv.SURFACETRANSLUCENCY)

    @property
    def use_translucency(self):
        """Enable surface translucency for this isosurface group.

        :type: `boolean <bool>`

        The surface translucency value can be changed by setting
        `IsosurfaceEffects.surface_translucency`.

        Example usage::

            >>> plot.isosurface(0).effects.use_translucency = True
            >>> plot.isosurface(0).effects.surface_translucency = 20
        """
        return self._get_style(bool, sv.USETRANSLUCENCY)

    @use_translucency.setter
    def use_translucency(self, value):
        self._set_style(bool(value), sv.USETRANSLUCENCY)


class IsosurfaceShade(IsosurfaceGroupStyle):
    """Shade attributes of the isosurface group.

    .. code-block:: python
        :emphasize-lines: 17-19

        import tecplot as tp
        from os import path
        from tecplot.plot import IsosurfaceGroup
        from tecplot.constant import Color, LightingEffect

        examples_dir = tp.session.tecplot_examples_directory()
        datafile = path.join(examples_dir, 'SimpleData', 'DuctFlow.plt')
        dataset = tp.data.load_tecplot(datafile)

        plot = tp.active_frame().plot()
        plot.show_isosurfaces = True
        plot.contour(0).variable = dataset.variable('U(M/S)')
        iso = plot.isosurface(0)

        iso.contour.show = False  # Hiding the contour will reveal the shade.

        iso.shade.show = True
        iso.shade.color = Color.Red
        iso.shade.use_lighting_effect = True

        iso.effects.lighting_effect = LightingEffect.Paneled

        tp.export.save_png('isosurface_shade.png', 600, supersample=3)

    .. figure:: /_static/images/isosurface_shade.png
        :width: 300px
        :figwidth: 300px


    """

    def __init__(self, contour):
        super().__init__(contour, sv.SHADE)

    @property
    def show(self):
        """Show shade attributes.

        :type: `boolean <bool>`

        Example usage::

            >>> plot.isosurface(0).shade.show = True
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
        Use flooded contours for multi-color or RGB flooding

        Example usage::

            >>> plot.isosurface(0).shade.show = True
            >>> plot.isosurface(0).shade.color = Color.Blue
        """
        return self._get_style(Color, sv.COLOR)

    @color.setter
    def color(self, value):
        self._set_style(Color(value), sv.COLOR)

    @property
    def use_lighting_effect(self):
        """Enable lighting effect.

        :type: `Boolean <bool>`

        When set to `True`, the lighting effect may be selected with the
        `IsosurfaceEffects.lighting_effect` attribute.

        Example usage::

            >>> plot.isosurface(0).shade.use_lighting_effect = True
            >>> plot.isosurface(0).effects.lighting_effect = LightingEffect.Paneled
        """
        return self._get_style(bool, sv.USELIGHTINGEFFECT)

    @use_lighting_effect.setter
    def use_lighting_effect(self, value):
        self._set_style(bool(value), sv.USELIGHTINGEFFECT)


class _IsosurfaceValues(object):
    def __init__(self, isosurface_group):
        """@type isosurface_group: IsosurfaceGroup"""
        self.isosurface_group = isosurface_group

    def _set_values(self, values):
        try:
            if isinstance(values, numbers.Number):
                # Assign first value only.
                self.__setitem__(0, values)
            else:
                for index in range(3):
                    try:
                        self.__setitem__(index, values[index])
                    except IndexError:  # 1 or 2-tuple okay
                        break

        except (TypeError, ValueError):
            raise TypeError('isosurface_values must be a single value ' +
                            'or tuple of up to 3 values')

    def __iter__(self):
        yield self.isosurface_group._isosurface_value_1
        yield self.isosurface_group._isosurface_value_2
        yield self.isosurface_group._isosurface_value_3

    @staticmethod
    def _check_index(index):
        if not isinstance(index, six.integer_types):
            raise IndexError('Isosurface value index must '
                             'be an integer.')
        if not 0 <= index <= 2:
            raise IndexError('Isosurface value index must'
                             'be between >= 0 and <= 2.')

    def __getitem__(self, item):
        self._check_index(item)
        # We could do this more elegantly with a dictionary or some such,
        # but we want to avoid making 3 calls into the engine
        # when only one call is needed.
        if item == 0:
            return self.isosurface_group._isosurface_value_1
        elif item == 1:
            return self.isosurface_group._isosurface_value_2
        else:
            return self.isosurface_group._isosurface_value_3

    def __setitem__(self, key, value):
        self._check_index(key)

        # See note for __getitem__() above.
        if key == 0:
            self.isosurface_group._isosurface_value_1 = value
        elif key == 1:
            self.isosurface_group._isosurface_value_2 = value
        else:
            self.isosurface_group._isosurface_value_3 = value

    # We're essentially a 3-tuple
    def __str__(self):
        return tuple(self).__str__()

    def __repr__(self):
        return tuple(self).__repr__()

    def __len__(self):
        return 3


class IsosurfaceGroup(session.Style):
    """Isosurfaces style control.

    .. code-block:: python
        :emphasize-lines: 16-26

        import os
        import tecplot as tp
        from tecplot.constant import *

        examples_dir = tp.session.tecplot_examples_directory()
        datafile = os.path.join(examples_dir, 'OneraM6wing', 'OneraM6_SU2_RANS.plt')
        dataset = tp.data.load_tecplot(datafile)

        plot = tp.active_frame().plot()
        plot.show_isosurfaces = True
        plot.contour(0).colormap_name = 'Magma'
        plot.contour(0).variable = dataset.variable('Mach')
        plot.contour(0).levels.reset_levels( [.95,1.0,1.1,1.4])
        plot.contour(0).legend.show = False

        iso = plot.isosurface(0)
        iso.show = True
        iso.definition_contour_group = plot.contour(0)
        iso.isosurface_selection = IsoSurfaceSelection.ThreeSpecificValues
        iso.isosurface_values = [.95,1,1.1]

        iso.contour.show = True
        iso.contour.flood_contour_group = plot.contour(0)

        iso.effects.use_translucency = True
        iso.effects.surface_translucency = 80

        view = plot.view
        view.psi = 65.777
        view.theta = 166.415
        view.alpha = -1.05394
        view.position = (-23.92541680486183, 101.8931504712126, 47.04269529295333)
        view.width = 1.3844

        tp.export.save_png('isosurface_group.png', 600, supersample=3)

    .. figure:: /_static/images/isosurface_group.png
        :width: 600px
        :figwidth: 300px
    """

    def __init__(self, index, plot):
        assert 0 <= index < 8, 'Iso-surface index out of range (must be < 8)'
        self.index = Index(index)
        self.plot = plot
        super().__init__(sv.ISOSURFACEATTRIBUTES, uniqueid=self.plot.frame.uid,
                         offset1=self.index)

    def __eq__(self, other):
        return (self.index == other.index) and (self.plot == other.plot)

    def __ne__(self, other):
        return not self.__eq__(other)

    @property
    def mesh(self):
        """Mesh attributes for this isosurface group.

        :type: `IsosurfaceMesh`

        Example usage::

            >>> plot.isosurface(0).show = True
            >>> plot.isosurface(0).mesh.show = True
        """
        return IsosurfaceMesh(self)

    @property
    def contour(self):
        """Contour attributes for this isosurface group.

        :type: `IsosurfaceContour`

        Example usage::

            >>> plot.isosurface(0).show = True
            >>> plot.isosurface(0).contour.show = True
        """
        return IsosurfaceContour(self)

    @property
    def effects(self):
        """Settings for isosurface effects.

        :type: `IsosurfaceEffects`

        Example usage::

            >>> plot.isosurface(0).show = True
            >>> plot.isosurface(0).effects.use_translucency = True
        """
        return IsosurfaceEffects(self)

    @property
    def shade(self):
        """Shade attributes for this isosurface group.

        :type: `IsosurfaceShade`

        Example usage::

            >>> plot.isosurface(0).shade.show = True
        """
        return IsosurfaceShade(self)

    @property
    def show(self):
        """Show isosurfaces for this isosurface group.

        :type: `bool`

        Example usage::

            >>> plot.isosurface(1).show = True
        """
        return self._get_style(bool, sv.SHOWGROUP)

    @show.setter
    def show(self, value):
        self._set_style(bool(value), sv.SHOWGROUP)

    @property
    def isosurface_values(self):
        """Query/Assign up to 3 values at which to draw isosurfaces.

        :type: 1, 2, or 3-`tuple` of `floats <float>`, or scalar `float`

        To draw isosurfaces at up to 3 values:
            #. Set `isosurface_selection` to one of the
               following: `IsoSurfaceSelection.OneSpecificValue`
               `IsoSurfaceSelection.TwoSpecificValues`
               `IsoSurfaceSelection.ThreeSpecificValues`
            #. Set `isosurface_values` to a 1, 2, or 3 `tuple` or `list` of
               `floats <float>`, or set to a scalar `float` to assign the
               first value only.

        When queried, this property will always return
        a 3 tuple of `floats <float>`.

        See also `isosurface_selection`.

        Assign first isosurface value using a scalar `float`::

            >>> plot.isosurface(0).isosurface_selection = IsoSurfaceSelection.OneSpecificValue
            >>> plot.isosurface(0).isosurface_values = 0.5
            >>> plot.isosurface(0).isosurface_values[0]
            0.5

        Assign first isosurface value using a 1-`tuple`::

            >>> plot.isosurface(0).isosurface_selection = IsoSurfaceSelection.OneSpecificValue
            >>> plot.isosurface(0).isosurface_values = (.5,) # 1-tuple
            >>> plot.isosurface(0).isosurface_values
            0.5

        Assign all three isosurface values::

            >>> plot.isosurface(0).isosurface_selection = IsoSurfaceSelection.ThreeSpecificValues
            >>> plot.isosurface(0).isosurface_values = (.5, .7, 9)

        Assign the third isosurface values after assigning the first two::

            >>> plot.isosurface(0).isosurface_selection = IsoSurfaceSelection.ThreeSpecificValues
            >>> # Assign first and second isosurface value using a tuple
            >>> plot.isosurface(0).isosurface_values = (0.0, 0.1)
            >>> # Assign third isosurface value
            >>> plot.isosurface(0).isosurface_values[2] = .3
            >>> plot.isosurface(0).isosurface_values[2]
            .3
            >>> plot.isosurface(0).isosurface_values
            (0.0, 0.1, .3)

        Query the three isosurface values::

            >>> # isosurface_values always returns a
            >>> # list-like object of 3 floats with of current
            >>> # isosurface values, even if fewer than three have been set.
            >>> values = plot.isosurface(0).isosurface_values
            >>> values
            (0.1, 0.2, 0.3)
            >>> values[0]
            0.1
            >>> values[1]
            0.2
            >>> values[2]
            0.3
            >>> len(plot.isosurface(0).isosurface_values)
            3
        """

        # We have to return an object so that the values can be set
        # with square bracket notation.
        return _IsosurfaceValues(self)

    @isosurface_values.setter
    def isosurface_values(self, values):
        _IsosurfaceValues(self)._set_values(values)

    @property
    def isosurface_selection(self):
        """Select where to draw isosurfaces.

        :type: `IsoSurfaceSelection`

        Iso-surfaces may be drawn at:
            * Contour group levels
            * At specified value(s) - Specify up to three values of the
              contour variable at which to draw isosurfaces.

        To draw isosurfaces at contour group lines:
            #. Set `isosurface_selection` to `IsoSurfaceSelection.AllContourLevels`.
            #. Optional: Change `tecplot.plot.ContourLevels`

        To draw isosurfaces at up to 3 values:
            #. Set `isosurface_selection` to one
               of the following: `IsoSurfaceSelection.OneSpecificValue`
               `IsoSurfaceSelection.TwoSpecificValues`
               `IsoSurfaceSelection.ThreeSpecificValues`
            #. Set `isosurface_values` to a
               1, 2, or 3 `tuple` of `floats <float>`

        See also `isosurface_values`.

        Example usage::

            >>> plot.isosurface(0).show = True
            >>> plot.isosurface(0).isosurface_selection = IsoSurfaceSelection.TwoSpecificValues
            >>> plot.isosurface(0).isosurface_values = (.3, .8)
        """
        return self._get_style(IsoSurfaceSelection, sv.ISOSURFACESELECTION)

    @isosurface_selection.setter
    def isosurface_selection(self, value):
        self._set_style(IsoSurfaceSelection(value), sv.ISOSURFACESELECTION)

    # Private methods used to implement _IsosurfaceValues class
    @property
    def _isosurface_value_1(self):
        return self._get_style(float, sv.ISOVALUE1)

    @_isosurface_value_1.setter
    def _isosurface_value_1(self, value):
        self._set_style(float(value), sv.ISOVALUE1)

    @property
    def _isosurface_value_2(self):
        return self._get_style(float, sv.ISOVALUE2)

    @_isosurface_value_2.setter
    def _isosurface_value_2(self, value):
        self._set_style(float(value), sv.ISOVALUE2)

    @property
    def _isosurface_value_3(self):
        return self._get_style(float, sv.ISOVALUE3)

    @_isosurface_value_3.setter
    def _isosurface_value_3(self, value):
        self._set_style(float(value), sv.ISOVALUE3)

    @property
    def definition_contour_group_index(self):
        """Contour group index from which isosurfaces are based.

        :type: `Index`

        Contour group settings can be changed from `plot.ContourGroup`.


        Example usage::

            >>> plot.isosurface(0).show = True
            >>> plot.isosurface(0).definition_contour_group_index = 1
        """
        return self._get_style(Index, sv.DEFINITIONCONTOURGROUP)

    @definition_contour_group_index.setter
    def definition_contour_group_index(self, value):
        self._set_style(Index(value), sv.DEFINITIONCONTOURGROUP)

    @property
    def definition_contour_group(self):
        """Contour group from which isosurfaces are based.

        :type: `ContourGroup`

        Example usage::

            >>> group = plot.contour(1)
            >>> plot.isosurface(0).definition_contour_group = group
        """
        return self.plot.contour(self.definition_contour_group_index)

    @definition_contour_group.setter
    def definition_contour_group(self, contour_group):
        self.definition_contour_group_index = contour_group.index

    @property
    def obey_source_zone_blanking(self):
        """Obey source zone blanking.

        :type: `boolean <bool>`

         * When `True`, isosurfaces are generated for non-blanked regions only.
         * When `False`, isosurfaces are generated for blanked and unblanked.
           regions.

        Example usage::

            >>> plot.isosurface(0).show = True
            >>> plot.isosurface(0).obey_source_zone_blanking = True
        """
        return self._get_style(bool, sv.OBEYSOURCEZONEBLANKING)

    @obey_source_zone_blanking.setter
    def obey_source_zone_blanking(self, value):
        self._set_style(bool(value), sv.OBEYSOURCEZONEBLANKING)

    @property
    def surface_generation_method(self):
        """Determines how the surface is generated.

            :type: `SurfaceGenerationMethod`

            May be one of:

            * `SurfaceGenerationMethod.AllTriangles`:
                An advanced algorithm that can handle
                complex saddle issues and guarantees that there will
                be no holes in the final surface. As the surface is
                composed entirely of triangles, it can be delivered
                more efficiently to the graphics hardware.
            * `SurfaceGenerationMethod.AllowQuads`:
                Produces quads or triangles, and the
                resulting surface more closely resembles the shape of
                the volume cells from the source zone. Since the quads
                are not arbitrarily divided into triangles, no biases
                are introduced, and the resulting surface may appear
                smoother. Preferred when the source zone is FE-Brink
                or IJK-Ordered and the surface is aligned with the
                source cells.

            Example usage::

                >>> from tecplot.constant import SurfaceGenerationMethod
                >>> plot.isosurface(0).surface_generation_method = SurfaceGenerationMethod.AllowQuads
        """
        return self._get_style(SurfaceGenerationMethod,
                               sv.SURFACEGENERATIONMETHOD)

    @surface_generation_method.setter
    def surface_generation_method(self, value):
        if __debug__:
            if version.sdk_version_info < (2017, 2):
                msg = 'setting surface generation method requires' \
                      ' Tecplot 360 2017 R2 or later.'
                raise TecplotOutOfDateEngineError(msg)
        self._set_style(SurfaceGenerationMethod(value),
                        sv.SURFACEGENERATIONMETHOD)
