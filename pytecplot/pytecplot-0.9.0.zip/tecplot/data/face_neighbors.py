from builtins import super

import logging
import itertools as it

from collections import namedtuple
from contextlib import contextmanager
from ctypes import c_int32, c_int64, c_void_p, POINTER, addressof, cast
from textwrap import dedent

from ..tecutil import _tecutil
from ..constant import *
from ..exception import *
from .. import session
from ..tecutil import IndexSet, array_to_str, lock, lock_attributes

log = logging.getLogger(__name__)


@lock_attributes
class FaceNeighbors(c_void_p):
    r"""Face neighbor definition and control.

    Face neighbors are used when the face of an element overlaps with another
    face from another element. Specifying these two (or more) overlapping faces
    as "face neighbors" indicates element connections outside the implicit
    faces of the nodemap. By specifying face neighbors it ensures that plot
    elements like shading, creases and edges are treated continously even if
    there is a zone or cell boundry.

    The neighbors can be completely "local", within a single zone, or "global"
    conntecting two or more zones together. Furthermore, the connections made
    can be one-to-one meaning there any given face can only neighbor one other
    face, or one-to-many where a single face can neighbor several other faces.

    This example creates two triangles in two different zones. Global
    one-to-one face neighbors are then used to stitch the two triangles into a
    quad. The data created looks like this:

    .. code-block:: none

        Node positions (x,y,z):

                       (1,1,1)
                      *
                     / \
                    /   \
         (0,1,.5)  *-----*  (1,0,.5)
                    \   /
                     \ /
                      *
                       (0,0,0)

    The two triangles will have separate nodes at the shared locations:

    .. code-block:: none

        Nodes:
                           2
            Zone 1:       / \
                         /   \
                        1-----0
                        2-----1
                         \   /
            Zone 0:       \ /
                           0

    .. code-block:: python

        import tecplot as tp
        from tecplot.constant import *

        # Triangle 0
        nodes0 = (
            (0, 0, 0  ),
            (1, 0, 0.5),
            (0, 1, 0.5))
        scalar_data0 = (0, 1, 2)
        conn0 = ((0, 1, 2),)
        neighbors0 = ((None, 0, None),)
        neighbor_zones0 = ((None, 1, None),)

        # Triangle 1
        nodes1 = (
            (1, 0, 0.5),
            (0, 1, 0.5),
            (1, 1, 1  ))
        scalar_data1 = (1, 2, 3)
        conn1 = ((0, 1, 2),)
        neighbors1 = ((0, None, None),)
        neighbor_zones1 = ((0, None, None),)

        # Create the dataset and zones
        ds = tp.active_frame().create_dataset('Data', ['x','y','z','s'])
        z0 = ds.add_fe_zone(ZoneType.FETriangle,
                            name='FE Triangle Float (3,1) Nodal 0',
                            num_points=len(nodes0), num_elements=len(conn0),
                            face_neighbor_mode=FaceNeighborMode.GlobalOneToOne)
        z1 = ds.add_fe_zone(ZoneType.FETriangle,
                            name='FE Triangle Float (3,1) Nodal 1',
                            num_points=len(nodes1), num_elements=len(conn1),
                            face_neighbor_mode=FaceNeighborMode.GlobalOneToOne)

        # Fill in and connect first triangle
        z0.values('x')[:] = [n[0] for n in nodes0]
        z0.values('y')[:] = [n[1] for n in nodes0]
        z0.values('z')[:] = [n[2] for n in nodes0]
        z0.nodemap[:] = conn0
        z0.values('s')[:] = scalar_data0

        # Fill in and connect second triangle
        z1.values('x')[:] = [n[0] for n in nodes1]
        z1.values('y')[:] = [n[1] for n in nodes1]
        z1.values('z')[:] = [n[2] for n in nodes1]
        z1.nodemap[:] = conn1
        z1.values('s')[:] = scalar_data1

        # Set face neighbors
        z0.face_neighbors.set_neighbors(neighbors0, neighbor_zones0, obscures=True)
        z1.face_neighbors.set_neighbors(neighbors1, neighbor_zones1, obscures=True)


        ### Setup a view of the data
        plot = tp.active_frame().plot(PlotType.Cartesian3D)
        plot.activate()

        plot.contour(0).colormap_name = 'Sequential - Yellow/Green/Blue'
        plot.contour(0).colormap_filter.distribution = ColorMapDistribution.Continuous

        for ax in plot.axes:
            ax.show = True

        plot.show_mesh = False
        plot.show_contour = True
        plot.show_edge = True
        plot.use_translucency = True

        # View parameters obtained interactively from Tecplot 360
        plot.view.distance = 10
        plot.view.width = 2
        plot.view.psi = 80
        plot.view.theta = 30
        plot.view.alpha = 0
        plot.view.position = (-4.2, -8.0, 2.3)

        for fmap in plot.fieldmaps():
            fmap.surfaces.surfaces_to_plot = SurfacesToPlot.All
            fmap.effects.surface_translucency = 40

        # Turning on mesh, we can see all the individual triangles
        plot.show_mesh = True
        for fmap in plot.fieldmaps():
            fmap.mesh.line_pattern = LinePattern.Dashed
        tp.export.save_png('fe_triangles1.png', 600, supersample=3)

    ..  figure:: /_static/images/fe_triangles1.png
        :width: 300px
        :figwidth: 300px

        Two triangles in two separate zones, stitched together using global
        face neighbors, showing the edge and mesh.
    """
    def __init__(self, zone):
        self.zone = zone
        super().__init__(self._native_reference())

    @lock()
    def _native_reference(self):
        return _tecutil.DataFaceNbrGetReadableRef(self.zone.index + 1)

    def __eq__(self, other):
        self_addr  = addressof(cast(self , POINTER(c_int64)).contents)
        other_addr = addressof(cast(other, POINTER(c_int64)).contents)
        return self_addr == other_addr

    def __ne__(self, other):
        return not (self == other)

    @property
    def c_type(self):
        """Underlying storage type used by the Tecplot Engine.

        Possible values: `ctypes.c_int32`, ctypes.c_int64`.

        .. note:: This property is read-only.
        """
        _ctypes = {
            OffsetDataType.OffsetDataType_32Bit: c_int32,
            OffsetDataType.OffsetDataType_64Bit: c_int64}
        data_type = _tecutil.DataFaceNbrRawItemType(self)
        return _ctypes[data_type]

    @property
    def mode(self):
        """`FaceNeighborMode` of this zone.

        :type: `FaceNeighborMode`

        Possible values: `FaceNeighborMode.LocalOneToOne`,
            `FaceNeighborMode.LocalOneToMany`,
            `FaceNeighborMode.GlobalOneToOne`,
            `FaceNeighborMode.GlobalOneToMany`.

        .. note:: This property is read-only.

        Face neighbors are used when the face of an element overlaps with
        another face from another element. The neighbors can be completely
        "local", within a single zone, or "global" conntecting two or more
        zones together. Furthermore, the connections made can be one-to-one
        meaning there any given face can only neighbor one other face, or
        one-to-many where a single face can neighbor several other faces. The
        face neighbor mode is set on zone creation and can not be changed
        afterwards::

            >>> zone = dataset.add_fe_zone(ZoneType.FETriangle, 'Zone', 4, 2,
            ...    face_neighbor_mode=FaceNeighborMode.LocalOneToMany)
            >>> print(zone.face_neighbors.mode)
            FaceNeighborMode.LocalOneToMany
        """
        return _tecutil.DataFaceNbrGetModeByRef(self)

    def set_neighbors(self, neighbors, zones=None, obscures=False):
        """Clear and set face neighbors from the given array.

        Parameters:
            neighbors (array of `integers <int>`): Zero-based Element indices
                of the neighbors for each face in the zone. A value of
                :math:`-1` or `None` indicates no neighbor.
            zones (array of `Zones <data_access>`, optional): This parameter is
                only used when the face neighbor mode is global one-to-one or
                global one-to-many. (default: `None`)
            obscures (array of `booleans <bool>`, optional): Indicates that the
                neighbors completely obscure the face. (default: `False`)

        This method uses the `FaceNeighbors.assignment()` context internally to
        ensure the proper book keeping is done. See the example code for
        `FaceNeighbors` class object for details on how to use this method.
        """
        with self.assignment():
            for elem, faces in enumerate(neighbors):
                for face, face_neighbors in enumerate(faces):
                    if face_neighbors is None:
                        continue
                    elif face_neighbors == -1:
                        continue

                    if not hasattr(face_neighbors, '__iter__'):
                        face_neighbors = [face_neighbors]
                    if zones is None:
                        neighbor_zones = None
                    else:
                        z = zones[elem][face]
                        if not hasattr(z, '__iter__'):
                            z = [z]
                        neighbor_zones = z
                    if hasattr(obscures, '__iter__'):
                        if hasattr(obscures[elem], '__iter__'):
                            obscure = obscures[elem][face]
                        else:
                            obscure = obscures[elem]
                    else:
                        obscure = obscures
                    self.add_neighbors(elem, face, face_neighbors,
                                       neighbor_zones, obscure)

    def add_neighbors(self, element, face, neighbors, zones=None,
                      obscure=False):
        """Connect boundary of an element's face to a neighboring face.

        This sets the boundary connection face neighbors within an open face
        neighbor assignment sequence for the specified element and face.

        Parameters:
            element (`int`): The element number (zero-based).
            face (`int`): The face number on the element (zero-based).
            neighbors (`list` of `integers <int>` or `None`): List of
                zero-based indices of the neighboring faces.
            zones (`list` of zone objects, optional): List of zones for
                global neighbors. This must be the same length as
                ``neighbors``. Use `None` to indicate these are local
                neighbors. (default: `None`)
            obscure (`boolean <bool>`, optional): Indicates that the neighbors
                completely obscure the face. (default: `False`)

        This method must be called from within a `FaceNeighbors.assignment()`
        context which will clear any previously existing face neighbor data::

            >>> with zone.face_neighbors.assigment():
            ...     for elem, face, neighbors, zn in face_neighbor_data:
            ...         zone.face_neighbors.add_neighbors(elem, face,
            ...                                           neighbors, zn)

        See the example code for `FaceNeighbors` class object for more details
        on how to set up user-defined face neighbors.
        """
        if __debug__:
            if zones is not None:
                if len(neighbors) != len(zones):
                    msg = 'neighbors and zones must be the same length'
                    raise TecplotLogicError(msg)

        _dispatch = {
            c_int32: _tecutil.DataFaceNbrAssignByRef,
            c_int64: _tecutil.DataFaceNbrAssignByRef64}
        int_type = self.c_type

        def _add_one(arr):
            def _f(x):
                return x + 1 if x is not None else 0
            return list(map(_f, arr))

        def _add_one_index(arr):
            def _f(x):
                return getattr(x, 'index', x) + 1 if x is not None else 0
            return list(map(_f, arr))

        n = len(neighbors)
        neighbors = (int_type * n)(*_add_one(neighbors))
        if zones is not None:
            zones = (c_int32 * n)(*_add_one_index(zones))
        args = (element + 1, face + 1, obscure, n, neighbors, zones)

        if __debug__:
            if min(neighbors) < 1 or self.zone.num_faces < max(neighbors):
                raise TecplotIndexError
            if zones:
                if min(zones) < 1 or self.zone.dataset.num_zones < max(zones):
                    raise TecplotIndexError
            log.debug(dedent('''\
                Face Neighbor Assign:
                    elem: {},
                    face: {},
                    obs: {},
                    n: {},
                    nbrs: {},
                    zns: {}''').format(
                        element + 1, face + 1, obscure, n,
                        array_to_str(neighbors), array_to_str(zones)))

        if not _dispatch[int_type](self, *args):
            raise TecplotSystemError()

    def add_local_neighbors(self, neighbors, offset=0):
        """Assign all local one-to-one face neighbors at once.

        Parameters:
            neighbors (2D array of `integers <int>`): :math:`(E,F)` Array of
                the face neighbors where :math:`E` is the number of elements
                and :math:`F` is the number of faces per element.
            offset (`integer <int>`, optional): Offset in Tecplot's face
                neighbor array to begin assigning the supplied neighbor
                elements. (default: 0)

        This method must be called from within a `FaceNeighbors.assignment()`
        context which will clear any previously existing face neighbor data::

            >>> with zone.face_neighbors.assigment():
            ...     zone.face_neighbors.add_local_neighbors(neighbors)

        See the example code for `FaceNeighbors` class object for more details
        on how to set up user-defined face neighbors.
        """
        _dispatch = {
            c_int32: _tecutil.DataFaceNbrAssignArrayByRef,
            c_int64: _tecutil.DataFaceNbrAssignArrayByRef64}
        int_type = self.c_type

        def _flatten_add_one(arr):
            def _add_one(x):
                return x + 1 if x is not None else 0
            return list(map(_add_one, it.chain(*arr)))

        neighbors = _flatten_add_one(neighbors)
        n = len(neighbors)
        neighbors = (int_type * n)(*neighbors)

        if __debug__:
            if min(neighbors) < 0 or self.zone.num_faces < max(neighbors):
                raise TecplotIndexError
            log.debug(dedent('''\
                Face Neighbor Assign Array:
                    offset: {},
                    nbrs({}): {}''').format(offset + 1, n,
                                            array_to_str(neighbors)))

        _dispatch[int_type](self, offset + 1, n, neighbors)

    @contextmanager
    def assignment(self):
        """Context manager for assigning face neighbors.

        This context ensures the proper book keeping is done when setting face
        neighbors. After the face neighbors are specified, this context will
        valid the connections and make appropriate changes to the zone
        metadata. It must be used with the
        `FaceNeighbors.add_local_neighbors()` and/or
        `FaceNeighbors.add_neighbors()` methods. See the `FaceNeighbors`
        example code for more details on how to set up user-defined face
        neighbors.

        """
        with lock():
            if not _tecutil.DataFaceNbrBeginAssign(self.zone.index + 1):
                raise TecplotSystemError()
            try:
                yield
            finally:
                _tecutil.DataFaceNbrEndAssign()
        c_void_p.__init__(self, self._native_reference())

    _Neighbor = namedtuple('Neighbor', ['element', 'zone'])

    def neighbors(self, element, face):
        """Get the neighboring elements and zones of a specific face.

        Parameters:
            element (`integer <int>`): The zero-based index of the element.
            face (`integer <int>`): The zero-based index of the face on this
                element.

        Returns:
            `list` of `namedtuples <collections.namedtuple>`:
            ``(element, zone)``:
                ``element``:
                    The zero-based index of the neighboring element.
                ``zone``:
                    The zone holding the neighboring element. A value of `None`
                    indicates this is a local (intra-zone) neighbor connection.

        Example getting the neighboring faces of a zone's first element, second
        face::

            >>> neighbors = zone.face_neighbors.neighbors(element=0, face=1)
            >>> for neighbor in neighbors:
            ...     elem, zn = neighbor
            ...     print(elem, zn.index)
            21 2
        """
        element = element + 1
        face = face + 1
        n, user_spec = _tecutil.DataFaceNbrGetNumNByRef(self, element, face)
        neighbors = []
        for i in range(1, n + 1):
            res = _tecutil.DataFaceNbrGetNbrByRef(self, element, face, i)
            neighbor_elem, neighbor_zone = res
            neighbor_elem -= 1
            if neighbor_zone == 0:
                neighbor_zone = None
            else:
                neighbor_zone =  self.zone.dataset.zone(neighbor_zone - 1)
            neighbor = FaceNeighbors._Neighbor(neighbor_elem, neighbor_zone)
            neighbors.append(neighbor)
        return neighbors

    def is_obscured(self, element, face, active_zones=None):
        """Obscuration of the specified face.

        Parameters:
            element (`integer <int>`): The zero-based index of the element.
            face (`integer <int>`): The zero-based index of the face on the
                element.
            active_zones (`list` of `Zones <data_access>`): List of zones to
                consider when global face neighbors are present. If `None`,
                the active zones of the dataset's parent frame will be used.

        Returns:
            `boolean <bool>`

        .. note::

            Because datasets can be shared between frames, the default frame
            used to identify the active zones may not be the one you want. In
            this case, you can use the `Frame.active_zones()` method to provide
            the active zones for a specific frame. Furthermore, the plot type
            of the frame must have the concept of active zones - i.e. it must
            not be in "sketch" mode.

        Example usage::

            >>> zone.face_neighbors.is_obscured(element=0, face=1)
            True
        """
        if active_zones is None:
            frame = self.zone.dataset.frame
            active_zones = frame.active_zones()
        with IndexSet(*active_zones) as active_zones:
            return _tecutil.DataFaceNbrFaceIsObscured(self, element + 1,
                                                      face + 1, active_zones)
