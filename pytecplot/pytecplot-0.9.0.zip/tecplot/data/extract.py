from ..tecutil import _tecutil
from .. import layout
from ..constant import *
from ..exception import TecplotSystemError, TecplotLogicError
from ..tecutil import ArgList, IndexSet, lock, sv


@lock()
def extract_slice(origin=(0, 0, 0), normal=(0, 0, 1), source=None,
                  multiple_zones=None, copy_cell_centers=None,
                  assign_strand_ids=None, frame=None, dataset=None):
    """Create new zone slices from the zones in a dataset.

    Parameters:
        origin (array of three `floats <float>`): Point in space,
            :math:`(x, y, z)`, that lies on the slice plane.
        normal (array of three `floats <float>`): Vector direction,
            :math:`(x, y, z)`, indicating the normal of the slice plane.
        source (`SliceSource`): Source zone types to consider when extracting
            the slice. Possible values: `SliceSource.LinearZones`,
            `SliceSource.SurfaceZones`, `SliceSource.SurfacesOfVolumeZones`,
            `SliceSource.VolumeZones` (default).
        multiple_zones (`boolean <bool>`): If `True`, this allows the
            extracted slice to consist of one zone per contiguous region. By
            default, only a single zone is created.  (default: `False`)
        copy_cell_centers (`boolean <bool>`): If `True`, cell-center
            values will be copied when possible to the extracted slice plane.
            Cell-centers are copied when a variable is cell-centered for all
            the source zones through which the slice passes. Otherwise,
            extracted planes use node-centered data, which is calculated by
            interpolation. (default: `False`)
        assign_strand_ids (`boolean <bool>`): automatically assign strand IDs
            to the data extracted from transient sources. This is only
            available if *multiple_zones* is `False`. (default: `True`)

    Returns:
        One or a `list` of `Zones <data_access>` representing a planar slice.

    .. warning::

        Slicing is only available when the plot type is set to 3D::

            >>> from tecplot.constant import PlotType
            >>> frame.plot_type = PlotType.Cartesian3D

    .. note::

        This function returns a list of zones if *multiple_zones* is set to
        `True`. Otherwise, a single zone is returned.

    This example shows extracting a slice zone from the surface a wing:

    .. code-block:: python
        :emphasize-lines: 16-20

        import os
        import tecplot as tp
        from tecplot.constant import PlotType, SliceSource

        examples_dir = tp.session.tecplot_examples_directory()
        datafile = os.path.join(examples_dir, 'OneraM6wing',
                                'OneraM6_SU2_RANS.plt')
        dataset = tp.data.load_tecplot(datafile)

        frame = tp.active_frame()
        frame.plot_type = PlotType.Cartesian3D

        # set active plot to 3D and extract
        # an arbitrary slice from the surface
        # data on the wing
        extracted_slice = tp.data.extract.extract_slice(
            origin=(0, 0.25, 0),
            normal=(0, 1, 0),
            source=SliceSource.SurfaceZones,
            dataset=dataset)

        # switch plot type in current frame, clear plot
        plot = frame.plot(PlotType.XYLine)
        plot.activate()
        plot.delete_linemaps()

        # create line plot from extracted zone data
        cp_linemap = plot.add_linemap(
            name='Quarter-chord C_p',
            zone=extracted_slice,
            x=dataset.variable('x'),
            y=dataset.variable('Pressure_Coefficient'))

        # set style of linemap plot and
        # update axes limits to show data
        cp_linemap.line.color = tp.constant.Color.Blue
        cp_linemap.line.line_thickness = 0.8
        cp_linemap.y_axis.reverse = True
        plot.view.fit()

        # export image of pressure coefficient as a function of x
        tp.export.save_png('wing_slice_pressure_coeff.png', 600, supersample=3)

    .. figure:: /_static/images/wing_slice_pressure_coeff.png
        :width: 300px
        :figwidth: 300px
    """


    if dataset is None:
        if frame is None:
            frame = layout.active_frame()
        dataset = frame.dataset
    elif frame is None:
        frame = dataset.frame

    if __debug__:
        if frame.dataset != dataset:
            raise TecplotLogicError('Dataset is not attached to frame.')
        if frame.plot_type is not PlotType.Cartesian3D:
            msg = 'Plot Type must be Cartesian3D to create a slice.'
            raise TecplotLogicError(msg)

    with frame.activated():
        new_zone_index = dataset.num_zones
        with ArgList() as arglist:
            arglist[sv.ORIGINX] = float(origin[0])
            arglist[sv.ORIGINY] = float(origin[1])
            arglist[sv.ORIGINZ] = float(origin[2])
            arglist[sv.NORMALX] = float(normal[0])
            arglist[sv.NORMALY] = float(normal[1])
            arglist[sv.NORMALZ] = float(normal[2])
            if source is not None:
                arglist[sv.SLICESOURCE] = SliceSource(source)
            if multiple_zones is not None:
                sigle_zone = not bool(multiple_zones)
                arglist[sv.FORCEEXTRACTIONTOSINGLEZONE] = sigle_zone
            arglist[sv.COPYCELLCENTEREDVALUES] = copy_cell_centers
            if assign_strand_ids is not None:
                arglist[sv.AUTOSTRANDTRANSIENTDATA] = bool(assign_strand_ids)
            if not _tecutil.CreateSliceZoneFromPlneX(arglist):
                raise TecplotSystemError()
            if dataset.num_zones == new_zone_index:
                raise TecplotLogicError('No zones found when extracting slice')
            if multiple_zones:
                zone_indices = range(new_zone_index, dataset.num_zones)
                return [dataset.zone(i) for i in zone_indices]
            else:
                return dataset.zone(new_zone_index)

@lock()
def extract_zones_from_connected_regions(zones):
    with IndexSet(zones) as zone_set:
        if not _tecutil.ExtractZonesFromConnectedRegions(zone_set):
            raise TecplotSystemError()
