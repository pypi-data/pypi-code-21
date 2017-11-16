from builtins import int

from collections import Iterable, namedtuple
from contextlib import contextmanager

from six import string_types

from ..tecutil import _tecutil
from .. import layout
from ..constant import *
from ..exception import *
from ..tecutil import (ArgList, IndexSet, Index, flatten_args, sv, lock,
                       optional)

Range = namedtuple('Range', 'min max step')
"""Limit the data altered by the `execute_equation` function.

The Range specification of I,J,K range indices for `execute_equation`
follow these rules:

    * All indices start with 0 and go to some maximum index *m*.
    * Negative values represent the indexes starting with the maximum at -1
      and continuing back to the beginning of the range.
    * A step of None, 0 and 1 are all equivalent and mean that no elements
      are skipped.
    * A negative step indicates a skip less than the maximum.

Example:

    Add one to variable 'X' for a zone 'Rectangular' for data points
    in I Range 1 to max, skipping every three points::

        >>> execute_equation('{X} = {X}+1', i_range=Range(1, None, 3),
        ...                  zone_set='Rectangular')
"""
Range.__new__.__defaults__ = (None, None, None)


@lock()
def execute_equation(equation, zones=None, i_range=None, j_range=None,
                     k_range=None, value_location=None, variable_data_type=None,
                     ignore_divide_by_zero=None):
    """The execute_equation function operates on a data set within the
    |Tecplot Engine| using FORTRAN-like equations.

    Parameters:
        equation (`string <str>`): String containing the equation.
            Multiple equations can be processed by separating each equation
            with a newline. See Section 20 - 1 "Data Alteration through
            Equations" in the Tecplot User's Manual for more information on
            using equations. Iterable container of `Zone <data_access>` objects
            to operate on. May be a list, set, tuple, or any iterable
            container. If `None`, the equation will be applied to all zones.

            .. note:: In the equation string, variable names should be enclosed
                in curly braces. For example, '{X} = {X} + 1'

        zones: (Iterable container of `Zone <data_access>` objects, optional):
            Iterable container of `Zone <data_access>` objects to operate on.
            May be a list, set, tuple, or any iterable container. If `None`,
            the equation will be applied to all zones.
        i_range (`Range`, optional):
            Tuple of integers for I:  (min, max, step). If `None`, then the
            equation will operate on the entire range.
            Not used for finite element nodal data.
        j_range (`Range`, optional):
            Tuple of integers for J:  (min, max, step). If `None`, then the
            equation will operate on the entire range.
            Not used for finite element nodal data.
        k_range (`Range`, optional):
            Tuple of integers for K:  (min, max, step). If `None`, then the
            equation will operate on the entire range.
            Not used for finite element nodal data.
        value_location (`ValueLocation`, optional):
            Variable `ValueLocation` for the variable on the left hand side.
            This is used only if this variable is being created for the first
            time.
            If `None`, |Tecplot Engine| will choose the location for you.
        variable_data_type (`FieldDataType`, optional):
            Data type for the variable on the left hand side.
            This is used only if this variable is being created for the first
            time.
            If `None`, |Tecplot Engine| will choose the type for you.
        ignore_divide_by_zero (`bool`, optional):
            `bool` value which instructs |Tecplot Engine| to ignore
            divide by zero errors. The result is clamped
            such that 0/0 is clamped to zero and (+/-N)/0
            where N != 0 clamps to +/-maximum value for the given type.

    Raises:
        `TecplotSystemError`

    .. warning:: Zero-based Indexing

        It is important to know that all indexing in |PyTecplot| scripts are
        zero-based. This is a departure from the macro language which is
        one-based. This is to keep with the expectations when working in the
        python language. However, |PyTecplot| does not modify strings that are
        passed to the |Tecplot Engine|. This means that one-based indexing
        should be used when running macro commands from python or when using
        `execute_equation() <tecplot.data.operate.execute_equation>`.

    Add one to variable 'X' for zones 'Rectangular' and 'Circular' for every
    data point:
    >>> import tecplot
    >>> dataset = tecplot.active_frame().dataset
    >>> execute_equation('{X} = {X} + 1', zones=[dataset.zone('Rectangular'),
    >>>                  dataset.zone('Circular')])

    Create a new, double precision variable called DIST:

    >>> execute_equation('{DIST} = SQRT({X}**2 + {Y}**2)',
    ...                  variable_data_type=FieldDataType.Double)

    Set a variable called **P** to zero along the boundary of an IJ-ordered
    zone:

    >>> execute_equation('{P} = 0', i_range=Range(step=-1))
    >>> execute_equation('{P} = 0', j_range=Range(step=-1))
    """
    if __debug__:
        if not isinstance(equation, string_types):
            raise TecplotTypeError('Equation must be a string')
        elif len(equation) == 0:
            raise TecplotValueError('Equation can not be empty')
        if not isinstance(value_location, (ValueLocation, type(None))):
            msg = 'value_location must be a ValueLocation'
            raise TecplotTypeError(msg)
        if not isinstance(variable_data_type, (FieldDataType, type(None))):
            msg = 'variable_data_type must be a FieldDataType'
            raise TecplotTypeError(msg)
        if not isinstance(ignore_divide_by_zero, (bool, type(None))):
            raise TecplotTypeError('ignore_divide_by_zero must be a bool')

        # Check that all zones belong to the active dataset
        # (which is currently the only dataset option available)
        if zones:
            try:
                current_dataset = layout.active_frame().dataset
                parent_ids = {U.dataset.uid for U in zones} if isinstance(
                    zones, Iterable) else {zones.dataset.uid}

                if {current_dataset.uid} != parent_ids:
                    raise TecplotValueError(
                        'All zones must have the same parent dataset')
            except AttributeError:
                pass  # integer indices do not care or know about parent dataset

    with ArgList() as arglist:
        arglist[sv.EQUATION] = equation
        with optional(IndexSet, zones) as zoneset:
            arglist[sv.ZONESET] = zoneset

            for dim, rng in zip(['I', 'J', 'K'], [i_range, j_range, k_range]):
                if rng is not None:
                    if not isinstance(rng, Range):
                        rng = Range(*rng)
                    if rng.min is not None:
                        arglist[dim + 'MIN'] = Index(rng.min)
                    if rng.max is not None:
                        arglist[dim + 'MAX'] = Index(rng.max)
                    if rng.step is not None:
                        step = int(rng.step)
                        if step != 0:
                            arglist[dim + 'SKIP'] = rng.step

            arglist[sv.VALUELOCATION] = value_location
            arglist[sv.VARDATATYPE] = variable_data_type
            arglist[sv.IGNOREDIVIDEBYZERO] = ignore_divide_by_zero

            if not _tecutil.DataAlterX(arglist):
                raise TecplotSystemError()


@contextmanager
def _interpolate_process_args(dest_zone, src_zones, variables, plot):
    if plot is None:
        plot = layout.active_frame().plot()
    if isinstance(dest_zone, int):
        dest_zone = plot.frame.dataset.zone(dest_zone)
    if not isinstance(src_zones, (Iterable, type(None))):
        src_zones = [src_zones]
    if not isinstance(variables, (Iterable, type(None))):
        variables = [variables]

    if __debug__:
        if plot.frame.dataset != dest_zone.dataset:
            msg = 'Plot and destination zone do not share the same dataset.'
            raise TecplotLogicError(msg)
        if src_zones is not None:
            def is_invalid_zone(z):
                if isinstance(z, int):
                    return z >= plot.frame.dataset.num_zones
                else:
                    return plot.frame.dataset != z.dataset
            if any(map(is_invalid_zone, src_zones)):
                msg = 'Source zones are not part of the same dataset.'
                raise TecplotLogicError(msg)
        if variables is not None:
            def is_invalid_variable(v):
                if isinstance(v, int):
                    return v >= plot.frame.dataset.num_variables
                else:
                    return plot.frame.dataset != v.dataset
            if any(map(is_invalid_variable, variables)):
                msg = 'Variables are not part of the same dataset.'
                raise TecplotLogicError(msg)

    with plot.activated():
        with optional(IndexSet, src_zones) as src:
            with optional(IndexSet, variables) as varset:
                dest = dest_zone.index + 1
                yield src, dest, varset


@lock()
def interpolate_linear(destination_zone, source_zones=None, variables=None,
                       fill_value=None, plot=None):
    """Linear interpolation onto a destination zone.

    Parameters:
        destination_zone (`zone <data_access>` or `integer <int>`): The
            destination zone (or zone index) for interpolation.
        source_zones (`zones <data_access>` or `integers <int>`, optional):
            Zones (or zone indices) used to obtain the field values for
            interpolation. By default, all zones except the *destination_zone*
            will be used. All source zones must be FE-Tetra, FE-Brick or be
            IJK-ordered when doing linear interpolation in 3D.
        variables (`variables <Variable>` or `integers <int>`, optional):
            Variables (or variable indices) to interpolate. By default, all
            variables except those assigned to the axes will be used and is in
            general dependent on the active plot type of the frame.
        fill_value (`float`, optional): Constant value to which all points
            outside the data field are set. By default, the values outside
            the field are preserved.
        plot (:ref:`plot`, optional): The plot to use when interpolating which
            determines the dimensionality and spatial variables. By default,
            the active plot on the active frame will be used.

    .. note:: Cartesian 2D and 3D plots only.

        This interpolation method relies on the coordinates, :math:`(x, y)` for
        2D or :math:`(x, y, z)` for 3D, set for the active (or given) plot
        which must be either Cartesian2D or Cartesian3D.

    The following example loads a 2D dataset and uses interpolation to merge information from two independent zones:

    .. code-block:: python

        import os
        import numpy as np
        import tecplot as tp
        from tecplot.constant import *

        # Use interpolation to merge information from two independent zones
        examples_dir = tp.session.tecplot_examples_directory()
        datafile = os.path.join(examples_dir, 'SimpleData', 'RainierElevation.plt')
        dataset = tp.data.load_tecplot(datafile)
        # Get list of source zones to use later
        srczones = list(dataset.zones())

        fr = tp.active_frame()
        plot = fr.plot(PlotType.Cartesian2D)
        plot.activate()
        plot.show_contour = True
        plot.show_edge = True

        # Show two section of the plot independently
        plot.contour(0).legend.show = False
        plot.contour(1).legend.show = False
        plot.contour(1).colormap_name = 'Diverging - Blue/Red'
        for scrzone in srczones:
            plot.fieldmap(scrzone).edge.line_thickness = 0.4
        plot.fieldmap(0).contour.flood_contour_group = plot.contour(1)

        # export image of original data
        tp.export.save_png('interpolate_2d_source.png', 600, supersample=3)

        # use the first zone as the source, and get the range of (x, y)
        xvar = plot.axes.x_axis.variable
        yvar = plot.axes.y_axis.variable
        ymin, xmin = 99999,99999
        ymax, xmax = -99999,-99999
        for scrzone in srczones:
            curxmin, curxmax = scrzone.values(xvar.index).minmax()
            curymin, curymax = scrzone.values(yvar.index).minmax()
            ymin = min(curymin,ymin)
            ymax = max(curymax,ymax)
            xmin = min(curxmin,xmin)
            xmax = max(curxmax,xmax)

        # create new zone with a coarse grid
        # onto which we will interpolate from the source zone
        xpoints = 40
        ypoints = 40
        newzone = dataset.add_ordered_zone('Interpolated', (xpoints, ypoints))

        # setup the (x, y) positions of the new grid
        xx = np.linspace(xmin, xmax, xpoints)
        yy = np.linspace(ymin, ymax, ypoints)
        YY, XX = np.meshgrid(yy, xx, indexing='ij')
        newzone.values(xvar.index)[:] = XX.ravel()
        newzone.values(yvar.index)[:] = YY.ravel()

        # perform linear interpolation from the source to the new zone
        tp.data.operate.interpolate_linear(newzone, source_zones=srczones)

        # show the new zone's data, hide the source
        plot.fieldmap(newzone).show = True
        plot.fieldmap(newzone).contour.show = True
        plot.fieldmap(newzone).contour.flood_contour_group = plot.contour(0)
        plot.fieldmap(newzone).edge.show = True
        plot.fieldmap(newzone).edge.line_thickness = .4
        plot.fieldmap(newzone).edge.color = Color.Orange

        for scrzone in srczones:
            plot.fieldmap(scrzone).show = False

        # export image of interpolated data
        tp.export.save_png('interpolate_linear_2d_dest.png', 600, supersample=3)

    .. figure:: /_static/images/interpolate_2d_source.png
        :width: 300px
        :figwidth: 300px

        Source data.

    .. figure:: /_static/images/interpolate_linear_2d_dest.png
        :width: 300px
        :figwidth: 300px

        Interpolated data.

    """
    with _interpolate_process_args(destination_zone, source_zones, variables,
                                   plot) as (src, dest, varset):
        if fill_value is None:
            interp_const = 0.0
            interp_mode = LinearInterpMode.DontChange
        else:
            interp_const = float(fill_value)
            interp_mode = LinearInterpMode.SetToConst
        if not _tecutil.LinearInterpolate(src, dest, varset, interp_const,
                                          interp_mode.value):
            raise TecplotSystemError()


@lock()
def interpolate_kriging(destination_zone, source_zones=None, variables=None,
                        krig_range=0.3, zero_value=0.0, drift=Drift.Linear,
                        point_selection=PtSelection.OctantN, num_points=8,
                        plot=None):
    """Kriging interpolation onto a destination zone.

    Parameters:
        destination_zone (`zone <data_access>` or `integer <int>`): The
            destination zone (or zone index) for interpolation.
        source_zones (`zones <data_access>` or `integers <int>`, optional):
            Zones (or zone indices) used to obtain the field values for
            interpolation. By default, all zones except the *destination_zone*
            will be used. All source zones must be FE-Tetra, FE-Brick or be
            IJK-ordered when doing linear interpolation in 3D.
        variables (`variables <Variable>` or `integers <int>`, optional):
            Variables (or variable indices) to interpolate. By default, all
            variables except those assigned to the axes will be used and is in
            general dependent on the active plot type of the frame.
        krig_range (`float`, optional): Distance beyond which source points
            become insignificant. Must be between zero and one, inclusive.
            (default: 0.3)
        zero_value (`float`, optional): Semi-variance at each source data point
            on a normalized scale from zero to one. (default: 0.0)
        drift (`Drift`, optional): Overall trend for the data. Possible values:
            `Drift.None_` no trend, `Drift.Linear` (default) linear trend,
            `Drift.Quad` quadratic trend.
        point_selection (`PtSelection`, optional): Method for determining which
            source points to consider for each destination data point. Possible
            values: `PtSelection.OctantN` (default) closest *num_points*
            selected by coordinate-system octants, `PtSelection.NearestN`
            closest *num_points* to the destination point, `PtSelection.All`
            all points in the source zone.
        num_points (`integer <int>`, optional): Number of source points to
            consider for each destination data point if *point_selection* is
            `PtSelection.OctantN` or `PtSelection.NearestN`. (default: 8)
        plot (:ref:`plot`, optional): The plot to use when interpolating which
            determines the dimensionality and spatial variables. By default,
            the active plot on the active frame will be used.

    .. note:: Cartesian 2D and 3D plots only.

        This interpolation method relies on the coordinates, :math:`(x, y)` for
        2D or :math:`(x, y, z)` for 3D, set for the active (or given) plot
        which must be either Cartesian2D or Cartesian3D.

    The following example loads a 2D dataset and interpolates the first zone to
    a new one with a larger grid spacing:

    .. code-block:: python

        import os
        import numpy as np
        import tecplot as tp
        from tecplot.constant import *

        # Use interpolation to merge information from two independent zones
        examples_dir = tp.session.tecplot_examples_directory()
        datafile = os.path.join(examples_dir, 'SimpleData', 'RainierElevation.plt')
        dataset = tp.data.load_tecplot(datafile)
        # Get list of source zones to use later
        srczones = list(dataset.zones())

        fr = tp.active_frame()
        plot = fr.plot(PlotType.Cartesian2D)
        plot.activate()
        plot.show_contour = True
        plot.show_edge = True

        # Show two section of the plot independently
        plot.contour(0).legend.show = False
        plot.contour(1).legend.show = False
        plot.contour(1).colormap_name = 'Diverging - Blue/Red'
        for scrzone in srczones:
            plot.fieldmap(scrzone).edge.line_thickness = 0.4
        plot.fieldmap(0).contour.flood_contour_group = plot.contour(1)

        # export image of original data
        tp.export.save_png('interpolate_2d_source.png', 600, supersample=3)

        # use the first zone as the source, and get the range of (x, y)
        xvar = plot.axes.x_axis.variable
        yvar = plot.axes.y_axis.variable
        ymin, xmin = 99999,99999
        ymax, xmax = -99999,-99999
        for scrzone in srczones:
            curxmin, curxmax = scrzone.values(xvar.index).minmax()
            curymin, curymax = scrzone.values(yvar.index).minmax()
            ymin = min(curymin,ymin)
            ymax = max(curymax,ymax)
            xmin = min(curxmin,xmin)
            xmax = max(curxmax,xmax)

        # create new zone with a coarse grid
        # onto which we will interpolate from the source zone
        xpoints = 40
        ypoints = 40
        newzone = dataset.add_ordered_zone('Interpolated', (xpoints, ypoints))

        # setup the (x, y) positions of the new grid
        xx = np.linspace(xmin, xmax, xpoints)
        yy = np.linspace(ymin, ymax, ypoints)
        YY, XX = np.meshgrid(yy, xx, indexing='ij')
        newzone.values(xvar.index)[:] = XX.ravel()
        newzone.values(yvar.index)[:] = YY.ravel()

        # perform linear interpolation from the source to the new zone
        tp.data.operate.interpolate_kriging(newzone, source_zones=srczones)

        # show the new zone's data, hide the source
        plot.fieldmap(newzone).show = True
        plot.fieldmap(newzone).contour.show = True
        plot.fieldmap(newzone).contour.flood_contour_group = plot.contour(0)
        plot.fieldmap(newzone).edge.show = True
        plot.fieldmap(newzone).edge.line_thickness = .4
        plot.fieldmap(newzone).edge.color = Color.Orange

        for scrzone in srczones:
            plot.fieldmap(scrzone).show = False

        # export image of interpolated data
        tp.export.save_png('interpolate_krig_2d_dest.png', 600, supersample=3)

    .. figure:: /_static/images/interpolate_2d_source.png
        :width: 300px
        :figwidth: 300px

        Source data.

    .. figure:: /_static/images/interpolate_krig_2d_dest.png
        :width: 300px
        :figwidth: 300px

        Interpolated data.
    """
    with _interpolate_process_args(destination_zone, source_zones, variables,
                                   plot) as (src, dest, varset):
        if not _tecutil.Krig(
            src, dest, varset, krig_range, zero_value, Drift(drift).value,
                PtSelection(point_selection).value, num_points):
            raise TecplotSystemError()


@lock()
def interpolate_inverse_distance(destination_zone, source_zones=None,
                                 variables=None, exponent=3.5, min_radius=0.0,
                                 point_selection=PtSelection.OctantN,
                                 num_points=8, plot=None):
    """Inverse-Distance interpolation onto a destination zone.

    Parameters:
        destination_zone (`zone <data_access>` or `integer <int>`): The
            destination zone (or zone index) for interpolation.
        source_zones (`zones <data_access>` or `integers <int>`, optional):
            Zones (or zone indices) used to obtain the field values for
            interpolation. By default, all zones except the *destination_zone*
            will be used. All source zones must be FE-Tetra, FE-Brick or be
            IJK-ordered when doing linear interpolation in 3D.
        variables (`variables <Variable>` or `integers <int>`, optional):
            Variables (or variable indices) to interpolate. By default, all
            variables except those assigned to the axes will be used and is in
            general dependent on the active plot type of the frame.
        exponent (`float`, optional): Exponent for the inverse-distance
            weighting. (default: 3.5)
        num_radius (`float`, optional): Minimum distance used for the
            inverse-distance weighting. (default: 0.0)
        point_selection (`PtSelection`, optional): Method for determining which
            source points to consider for each destination data point. Possible
            values: `PtSelection.OctantN` (default) closest *num_points*
            selected by coordinate-system octants, `PtSelection.NearestN`
            closest *num_points* to the destination point, `PtSelection.All`
            all points in the source zone.
        num_points (`integer <int>`, optional): Number of source points to
            consider for each destination data point if *point_selection* is
            `PtSelection.OctantN` or `PtSelection.NearestN`. (default: 8)
        plot (:ref:`plot`, optional): The plot to use when interpolating which
            determines the dimensionality and spatial variables. By default,
            the active plot on the active frame will be used.

    .. note:: Cartesian 2D and 3D plots only.

        This interpolation method relies on the coordinates, :math:`(x, y)` for
        2D or :math:`(x, y, z)` for 3D, set for the active (or given) plot
        which must be either Cartesian2D or Cartesian3D.

    The following example loads a 2D dataset and interpolates the first zone to
    a new one with a larger grid spacing:

    .. code-block:: python

        import os
        import numpy as np
        import tecplot as tp
        from tecplot.constant import *

        # Use interpolation to merge information from two independent zones
        examples_dir = tp.session.tecplot_examples_directory()
        datafile = os.path.join(examples_dir, 'SimpleData', 'RainierElevation.plt')
        dataset = tp.data.load_tecplot(datafile)
        # Get list of source zones to use later
        srczones = list(dataset.zones())

        fr = tp.active_frame()
        plot = fr.plot(PlotType.Cartesian2D)
        plot.activate()
        plot.show_contour = True
        plot.show_edge = True

        # Show two section of the plot independently
        plot.contour(0).legend.show = False
        plot.contour(1).legend.show = False
        plot.contour(1).colormap_name = 'Diverging - Blue/Red'
        for scrzone in srczones:
            plot.fieldmap(scrzone).edge.line_thickness = 0.4
        plot.fieldmap(0).contour.flood_contour_group = plot.contour(1)

        # export image of original data
        tp.export.save_png('interpolate_2d_source.png', 600, supersample=3)

        # use the first zone as the source, and get the range of (x, y)
        xvar = plot.axes.x_axis.variable
        yvar = plot.axes.y_axis.variable
        ymin, xmin = 99999,99999
        ymax, xmax = -99999,-99999
        for scrzone in srczones:
            curxmin, curxmax = scrzone.values(xvar.index).minmax()
            curymin, curymax = scrzone.values(yvar.index).minmax()
            ymin = min(curymin,ymin)
            ymax = max(curymax,ymax)
            xmin = min(curxmin,xmin)
            xmax = max(curxmax,xmax)

        # create new zone with a coarse grid
        # onto which we will interpolate from the source zone
        xpoints = 40
        ypoints = 40
        newzone = dataset.add_ordered_zone('Interpolated', (xpoints, ypoints))

        # setup the (x, y) positions of the new grid
        xx = np.linspace(xmin, xmax, xpoints)
        yy = np.linspace(ymin, ymax, ypoints)
        YY, XX = np.meshgrid(yy, xx, indexing='ij')
        newzone.values(xvar.index)[:] = XX.ravel()
        newzone.values(yvar.index)[:] = YY.ravel()

        # perform linear interpolation from the source to the new zone
        tp.data.operate.interpolate_inverse_distance(newzone, source_zones=srczones)

        # show the new zone's data, hide the source
        plot.fieldmap(newzone).show = True
        plot.fieldmap(newzone).contour.show = True
        plot.fieldmap(newzone).contour.flood_contour_group = plot.contour(0)
        plot.fieldmap(newzone).edge.show = True
        plot.fieldmap(newzone).edge.line_thickness = .4
        plot.fieldmap(newzone).edge.color = Color.Orange

        for scrzone in srczones:
            plot.fieldmap(scrzone).show = False

        # export image of interpolated data
        tp.export.save_png('interpolate_invdst_2d_dest.png', 600, supersample=3)

    .. figure:: /_static/images/interpolate_2d_source.png
        :width: 300px
        :figwidth: 300px

        Source data.

    .. figure:: /_static/images/interpolate_invdst_2d_dest.png
        :width: 300px
        :figwidth: 300px

        Interpolated data.
    """
    with _interpolate_process_args(destination_zone, source_zones, variables,
                                   plot) as (src, dest, varset):
        if not _tecutil.InverseDistInterpolation(
            src, dest, varset, exponent, min_radius,
                PtSelection(point_selection).value, num_points):
            raise TecplotSystemError()
