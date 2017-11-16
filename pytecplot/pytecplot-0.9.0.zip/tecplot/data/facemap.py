import itertools as it
import logging

from collections import deque, namedtuple
from contextlib import contextmanager
from ctypes import c_int32, c_int64, c_void_p, POINTER, addressof, cast
from textwrap import dedent

from ..tecutil import _tecutil
from ..constant import *
from ..exception import *
from .. import version
from ..tecutil import array_to_str, lock, lock_attributes

log = logging.getLogger(__name__)


@lock_attributes
class Elementmap(c_void_p):
    """Facemap reverse look-up."""
    def __init__(self, zone):
        self.zone = zone
        super().__init__(self._native_reference())

    @lock()
    def _native_reference(self):
        with self.zone.dataset.frame.activated():
            return _tecutil.DataElemGetReadableRef(self.zone.index + 1)

    def num_faces(self, element):
        return _tecutil.DataElemGetNumFaces(self, element + 1)

    def face(self, element, offset):
        return _tecutil.DataElemGetFace(self, element + 1, offset + 1) - 1

    def faces(self, element):
        return [self.face(element, f) for f in range(self.num_faces(element))]


@lock_attributes
class Facemap(c_void_p):
    r"""Connectivity list definition and control.

    A facemap holds the connectivity for a polytopal finite-element zone. This
    includes node-to-element and element-to-element connections. The following
    script creates a quad of two triangles from scratch using the PyTecplot
    low-level data creation interface. The data created looks like this:

    .. code-block:: none

        Node positions (x,y,z):

                       (1,1,1)
                      3
                     / \
                    /   \
         (0,1,.5)  2-----1  (1,0,.5)
                    \   /
                     \ /
                      0
                       (0,0,0)

    Element indices are used when identifying the left and right of each face,
    where :math:`-1` is used to indicate no element:

    .. code-block:: none

                      *
                  -1 / \ -1
                    / 1 \
                   *-----*
                    \ 0 /
                  -1 \ / -1
                      *

    .. code-block:: python

        import tecplot as tp
        from tecplot.constant import *

        nodes = ((0, 0, 0  ),
                 (1, 0, 0.5),
                 (0, 1, 0.5),
                 (1, 1, 1  ))
        faces = ((0, 1),
                 (1, 2),
                 (2, 0),
                 (1, 3),
                 (3, 2))
        elements = (( 0, 0,  0,  1,  1),  # elements to the left of each face
                    (-1, 1, -1, -1, -1))  # elements to the right of each face
        num_elements = 2
        scalar_data = (0, 1, 2, 3)

        ds = tp.active_frame().create_dataset('Data', ['x','y','z','s'])
        z = ds.add_poly_zone(ZoneType.FEPolygon,
                             name='FE Polygon Float (4,2,5) Nodal',
                             num_points=len(nodes),
                             num_elements=num_elements,
                             num_faces=len(faces))

        z.values('x')[:] = [n[0] for n in nodes]
        z.values('y')[:] = [n[1] for n in nodes]
        z.values('z')[:] = [n[2] for n in nodes]
        z.facemap.set_mapping(faces, elements)
        z.values('s')[:] = scalar_data

        ### setup a view of the data
        plot = tp.active_frame().plot(PlotType.Cartesian3D)
        plot.activate()

        cont = plot.contour(0)
        cont.colormap_name = 'Sequential - Yellow/Green/Blue'
        cont.colormap_filter.distribution = ColorMapDistribution.Continuous

        for ax in plot.axes:
            ax.show = True

        plot.show_mesh = False
        plot.show_contour = True
        plot.show_edge = True
        plot.use_translucency = True

        fmap = plot.fieldmap(z)
        fmap.surfaces.surfaces_to_plot = SurfacesToPlot.All
        fmap.effects.surface_translucency = 40

        # View parameters obtained interactively from Tecplot 360
        plot.view.distance = 10
        plot.view.width = 2
        plot.view.psi = 80
        plot.view.theta = 30
        plot.view.alpha = 0
        plot.view.position = (-4.2, -8.0, 2.3)

        # Turning on mesh, we can see all the individual triangles
        plot.show_mesh = True
        plot.fieldmap(z).mesh.line_pattern = LinePattern.Dashed
        tp.export.save_png('polygons1.png', 600, supersample=3)

    ..  figure:: /_static/images/polygons1.png
        :width: 300px
        :figwidth: 300px

        Two triangle polygons showing edge and mesh lines.
    """
    def __init__(self, zone):
        if __debug__:
            sdk_required = (2017, 2, 0)
            if (
                version.sdk_version_info < sdk_required and
                zone.num_faces == 0
            ):
                msg = 'Deferred allocation of facemap not supported.'
                raise TecplotOutOfDateEngineError(sdk_required, msg)
        self.zone = zone
        if self.zone.num_faces > 0:
            try:
                ref = self._native_reference()
            except:
                ref = None
        else:
            ref = None
        super().__init__(ref)

    @property
    def _has_data_backing(self):
        return bool(self)

    @lock()
    def _native_reference(self, writable=False):
        try:
            _dispatch = {
                True: _tecutil.DataFaceMapGetWritableRef,
                False: _tecutil.DataFaceMapGetReadableRef}
            with self.zone.dataset.frame.activated():
                return _dispatch[writable](self.zone.index + 1)
        except TecplotLogicError:
            raise TecplotLogicError(
                'A facemap must first be created with Facemap.alloc()')

    @lock()
    def alloc(self, face_nodes, boundary_faces=0, boundary_connections=0):
        """Allocate space for the facemap.

        Parameters:
            face_nodes (`int`):  Total number of nodes for all faces. This is
                not the number of unique nodes but the total number. For
                example if a facemap defines two triangle polygons that share a
                common face, ``faces`` would be 5 and ``face_nodes`` would be
                6, not 4.
            boundary_faces (`int`, optional): Total number of boundary faces.
                (default: 0)
            boundary_connections (`int`, optional): Total number of boundary
                face elements or boundary face element/zone pairs. (default: 0)

        Returns:
            `Facemap`

        This is called when using the `Facemap.set_mapping()` method which is
        the preferred method for filling the connectivity of polytope zones. If
        the zone does not already have space allocated for a facemap and if you
        wish to use the `Facemap.set_nodes()` and `Facemap.set_elements()`
        methods to fill in the connectivity, then this must be called first::

            >>> facemap = zone.facemap.alloc(400, 25, 50)

        .. note:: Tecplot version 2017.2 or later.

            Setting the boundary faces and boundary connections using PyTecplot
            requires Tecplot version 2017.2 or later.
        """
        if __debug__:
            sdk_version_required = (2017, 2, 0)
            if (
                version.sdk_version_info < sdk_version_required and
                boundary_faces
            ):
                msg = 'Creation of facemap boundary elements not supported.'
                raise TecplotOutOfDateEngineError(sdk_version_required, msg)
        if not _tecutil.DataFaceMapAlloc(self.zone.index + 1,
                                         self.zone.num_faces, face_nodes,
                                         boundary_faces, boundary_connections):
            raise TecplotSystemError()
        c_void_p.__init__(self, self._native_reference())

    def __eq__(self, other):
        if not (self._has_data_backing and other._has_data_backing):
            return False
        self_addr = addressof(cast(self, POINTER(c_int64)).contents)
        other_addr = addressof(cast(other, POINTER(c_int64)).contents)
        return self_addr == other_addr

    def __ne__(self, other):
        return not (self == other)

    def __len__(self):
        return self.num_faces()

    def num_faces(self, element=None):
        """The number of faces of an element in this `Facemap`.

        Parameters:
            element (`integer <int>`, optional): Zero-based index of an
                element. If no element is given, the total number of faces
                in the map are returned.

        Returns:
            `integer <int>`

        Example usage::

            >>> print(zone.facemap.num_faces())
            1048576
        """
        if element is None:
            if not self._has_data_backing:
                return self.zone.num_faces
            return _tecutil.DataFaceMapGetNFaces(self)
        else:
            return Elementmap(self.zone).num_faces(element)

    @property
    def num_unique_nodes(self):
        """The number of unique nodes in this `Facemap`.

        :type: `integer <int>`

        .. note:: This property is read-only.

        Example usage::

            >>> print(zone.facemap.num_unique_nodes)
            4194304
        """
        if not self._has_data_backing:
            return self.zone.num_points
        return _tecutil.DataFaceMapGetNumNodes(self)

    def num_nodes(self, face=None, element=None):
        """The number nodes for a given face in this `Facemap`.

        Parameters:
            face (`integer <int>`, required if no *element* is given): The
                zero-based index of the face either within the given *element*
                or globally. If no face is given, the number of nodes on the
                given *element* are returned.
            element (`integer <int>`, required if no face is given): The
                zero-based index of an element. If no element is given, then
                *face* is globally indexed from zero over the whole zone.

        Returns:
            `integer <int>` The number of nodes.

        Example usage::

            >>> print(zone.facemap.num_nodes(face=1))
            4
        """
        if element is None:
            if face is None:
                raise TecplotNotImplementedError
                # While the following sum() is technically correct, it is
                # extremely slow as currently, there is no way to query
                # the total number of nodes in the connectivity list directly.
                #
                # return sum(self.num_nodes(i) for i in range(self.num_faces()))
            else:
                if self.zone.zone_type == ZoneType.FEPolygon:
                    return 2
                else:
                    return _tecutil.DataFaceMapGetNFaceNodes(self, face + 1)
        else:
            emap = Elementmap(self.zone)
            if face is None:
                return sum(self.num_nodes(f) for f in emap.faces(element))
            else:
                return self.num_nodes(emap.face(element, face))

    def num_boundary_connections(self, face=None, element=None):
        """The number of boundary connections for a given face.

        Parameters:
            face (`integer <int>`, required if no element is given): The
                zero-based index of the face.
            element (`integer <int>`, optional): Zero-based index of an
                element. If given, *face* will be locally indexed within this
                element, otherwise *face* is globally indexed over the whole
                zone.

        Returns:
            `integer <int>` The number of boundary connections.

        Example usage::

            >>> print(zone.facemap.num_boundary_connections(1))
            1
        """
        if face is None:
            if element is None:
                raise TecplotNotImplementedError
                # While the following sum() is technically correct using
                # the face indices here, it is extremely slow as currently,
                # there is no way to query the total number of boundary
                # connections directly.
                #
                # faces = range(self.num_faces())
            else:
                emap = Elementmap(self.zone)
                faces = emap.faces(element)
            return sum(self.num_boundary_connections(f) for f in faces)
        elif element is not None:
            face = self.face(element, face)
        return _tecutil.DataFaceMapGetNBndryConns(self, face + 1)

    _BoundaryConnection = namedtuple('BoundaryConnection', ['element', 'zone'])

    def boundary_connection(self, face, offset, element=None):
        """The connected element and zone along a boundary face.

        Parameters:
            face (`integer <int>`): The zero-based index of the face.
            offset (`integer <int>`): The zero-based index of the node being
                requested.
            element (`integer <int>`, optional): Zero-based index of an
                element. If given, *face* will be locally indexed within this
                element, otherwise *face* is globally indexed over the whole
                zone.

        Returns:
            `namedtuple <collections.namedtuple>`: ``(element, zone)``:
                ``element``
                    The zero-based index of the neighboring element.
                ``zone``
                    The zone holding the neighboring element.

        Example usage::

            >>> bconn = zone.facemap.boundary_connection(0, 2)
            >>> print(bconn.element)
            128
            >>> print(bconn.zone.index)
            2
        """
        if element is not None:
            face = self.face(element, face)
        elem, zone = _tecutil.DataFaceMapGetBndryConn(self, face + 1,
                                                      offset + 1)
        return Facemap._BoundaryConnection(elem - 1,
                                           self.zone.dataset.zone(zone - 1))

    def node(self, face, offset, element=None):
        """The node index along a specific face.

        Parameters:
            face (`integer <int>`): The zero-based index of the face.
            offset (`integer <int>`): The zero-based index of the node being
                requested.
            element (`integer <int>`, optional): Zero-based index of an
                element. If given, *face* will be locally indexed within this
                element, otherwise *face* is globally indexed over the whole
                zone.

        Returns:
            `integer <int>` The node at the specified location.

        Example usage::

            >>> print(zone.facemap.face_node(0, 2))
            128
        """
        if element is not None:
            face = self.face(element, face)
        return _tecutil.DataFaceMapGetFaceNode(self, face + 1, offset + 1) - 1

    def left_element(self, face, element=None):
        """The element to the left of a specific face.

        Parameters:
            face (`integer <int>`): The zero-based index of the face.
            element (`integer <int>`, optional): Zero-based index of an
                element. If given, *face* will be locally indexed within this
                element, otherwise *face* is globally indexed over the whole
                zone.

        Returns:
            `integer <int>`

        A negative number indicates there is no element to the left of this
        face. Example usage::

            >>> print(zone.facemap.left_element(0))
            128
        """
        if element is not None:
            face = self.face(element, face)
        return _tecutil.DataFaceMapGetLeftElem(self, face + 1) - 1

    def right_element(self, face, element=None):
        """The element to the right of a specific face.

        Parameters:
            face (`integer <int>`): The zero-based index of the face.
            element (`integer <int>`, optional): Zero-based index of an
                element. If given, *face* will be locally indexed within this
                element, otherwise *face* is globally indexed over the whole
                zone.

        Returns:
            `integer <int>`

        A negative number indicates there is no element to the right of this
        face. Example usage::

            >>> print(zone.facemap.right_element(0))
            -1
        """
        if element is not None:
            face = self.face(element, face)
        return _tecutil.DataFaceMapGetRightElem(self, face + 1) - 1

    def face(self, element, offset):
        """Face index on a specific element.

        Parameters:
            element (`integer <int>`): The zero-based index of the element.
            offset (`integer <int>`): The zero-based index of the face being
                requested.

        Returns:
            `integer <int>` Zero-based index of the face at the specified
            location.

        Example usage::

            >>> print(zone.facemap.face(0, 2))
            128
        """
        return Elementmap(self.zone).face(element, offset)

    @property
    def node_c_type(self):
        """The data type of the node indices.

        Possible values: `ctypes.c_int32`, `ctypes.c_int64`

        .. note:: This property is read-only.
        """
        _ctypes = {
            OffsetDataType.OffsetDataType_32Bit: c_int32,
            OffsetDataType.OffsetDataType_64Bit: c_int64}
        if self._has_data_backing:
            data_type = _tecutil.DataFaceMapGetNodeRawItemType(self)
            return _ctypes[data_type]

    @property
    def element_c_type(self):
        """The data type of the element indices.

        Possible values: `ctypes.c_int32`, `ctypes.c_int64`

        .. note:: This property is read-only.
        """
        _ctypes = {
            OffsetDataType.OffsetDataType_32Bit: c_int32,
            OffsetDataType.OffsetDataType_64Bit: c_int64}
        if self._has_data_backing:
            ref = self._native_reference(writable=True)
            data_type = _tecutil.DataFaceMapGetElementRawItemType(ref)
            return _ctypes[data_type]

    def set_nodes(self, facemap):
        """Sets the polytope node-connectivity.

        Parameters:
            facemap (2D array of zero-based `integers <int>`): The `list` of
                `lists <list>` which need not all be the same length, defining
                the individual elements by their nodes.

        The facemap must first be allocated with `Facemap.alloc()` and must be
        called from within a `Facemap.assignment()` context and should be
        followed by a call to `Facemap.set_elements()` to complete the
        connectivity map information needed for rendering. It is recomended to
        use the `Facemap.set_mapping()` which does all the required
        book keeping.
        """
        _dispatch = {
            c_int32: _tecutil.DataFaceMapAssignNodes,
            c_int64: _tecutil.DataFaceMapAssignNodes64}
        data_type = self.node_c_type
        nfaces = len(facemap)
        nnodes = [len(n) for n in facemap]
        nfacenodes = sum(nnodes)
        if self.zone.zone_type is ZoneType.FEPolygon:
            faces = None
        else:
            faces = (c_int32 * nfaces)(*nnodes)
        nodes = (data_type * nfacenodes)(*[n + 1 for n in it.chain(*facemap)])

        if __debug__:
            if min(nodes) < 1 or self.num_unique_nodes < max(nodes):
                raise TecplotIndexError
            log.debug(dedent('''\
                Facemap set nodes:
                    faces({}): {}
                    nodes: {}''').format(nfaces, array_to_str(faces),
                                         array_to_str(nodes)))

        ref = self._native_reference(writable=True)
        _dispatch[data_type](ref, nfaces, faces, nodes)

    def set_elements(self, left_elements, right_elements):
        """Sets the polytope node-connectivity.

        Parameters:
            left_elements (array of zero-based `integers <int>`): This is an
                array of the elements to the left of each face in the facemap
                and must be the same length as the number of faces.
            right_elements (array of zero-based `integers <int>`): Same as
                *left_elements* for the right side of each face.

        The facemap must first be allocated with `Facemap.alloc()` and must be
        called from within a `Facemap.assignment()` context and should follow a
        call to `Facemap.set_nodes()` to complete the connectivity map
        information needed for rendering. Using `Facemap.set_mapping()` is
        recommended, which does all the required book keeping.

        """
        _dispatch = {
            c_int32: _tecutil.DataFaceMapAssignElems,
            c_int64: _tecutil.DataFaceMapAssignElems64}
        data_type = self.element_c_type
        nelements = len(left_elements)
        left = (data_type * nelements)(*[e + 1 for e in left_elements])
        right = (data_type * nelements)(*[e + 1 for e in right_elements])

        if __debug__:
            if self.zone.num_elements < max(left):
                raise TecplotIndexError
            if self.zone.num_elements < max(right):
                raise TecplotIndexError
            log.debug(dedent('''\
                Facemap set elements:
                    left({}): {}
                    right({}): {}''').format(len(left), array_to_str(left),
                                             len(right), array_to_str(right)))

        ref = self._native_reference(writable=True)
        _dispatch[data_type](ref, nelements, left, right)

    def set_boundary_connections(self, elements, zones):
        """Set the boundary connections.

        Parameters:
            elements (2D array of `integers <int>`): Zero-based indices of the
                connected elements. This is a "ragged" array of dimension
                :math:`(N,E_i)` where :math:`N` is the number of boundary faces
                and :math:`E_i` is the number of boundary connected elements
                for the :math:`i^{th}` face.
            zones (2D array of `integers <int>`): Zero-based indices of the
                zones for each entry given in *elements*. This must be the same
                shape as *elements*.

        The facemap must first be allocated with `Facemap.alloc()` and must be
        called from within a `Facemap.assignment()` context, and should follow
        calls to `Facemap.set_nodes()` and `Facemap.set_elements()` to complete
        the connectivity map information needed for rendering. Using
        `Facemap.set_mapping()` is recommended, which does all the required
        book keeping.

        """
        _dispatch = {
            c_int32: _tecutil.DataFaceMapAssignBConns,
            c_int64: _tecutil.DataFaceMapAssignBConns64}
        data_type = self.node_c_type
        nbfaces = len(elements)
        nbconns = (c_int32 * nbfaces)(*[len(n) for n in elements])
        nbelems = sum(nbconns)

        def _flatten_add_one(arr):
            def _f(x):
                return x + 1 if x is not None else 0
            return list(map(_f, it.chain(*arr)))

        def _flatten_add_one_index(arr):
            def _f(x):
                return getattr(x, 'index', x) + 1 if x is not None else 0
            return list(map(_f, it.chain(*arr)))

        belems = (data_type * nbelems)(*_flatten_add_one(elements))
        bzones = (c_int32 * nbelems)(*_flatten_add_one_index(zones))

        if __debug__:
            if min(belems) < 1 or self.zone.num_elements < max(belems):
                raise TecplotIndexError
            if min(bzones) < 1 or self.zone.dataset.num_zones < max(bzones):
                raise TecplotIndexError
            log.debug(dedent('''\
                Facemap set boundary connections:
                    num boundary faces: {}
                    num boundary conns: {}
                    boundary elems: {}
                    boundary zones: {}'''.format(nbfaces,
                                                 array_to_str(nbconns),
                                                 array_to_str(belems),
                                                 array_to_str(bzones))))

        ref = self._native_reference(writable=True)
        _dispatch[data_type](ref, nbfaces, nbconns, belems, bzones)

    def set_mapping(self, facemap, elements, boundary_elements=None,
                    boundary_zones=None):
        """Set the node and element connectivity for this polytope zone.

        Parameters:
            facemap (2D array of zero-based `integers <int>`): The `list` of
                `lists <list>` which need not all be the same length, defining
                the individual elements by their nodes.
            elements (2D array of zero-based `integers <int>`): This is a
                :math:`(2,N)` array where :math:`N` is the number of faces and
                the items are a list of the elements to the left and right of
                the face respectively.
            boundary_elements (2D array of `integers <int>`, optional):
                Zero-based indices of the connected elements. This is a
                "ragged" array of dimension :math:`(N, E_i)` where :math:`N` is
                the number of boundary faces and :math:`E_i` is the number of
                boundary connected elements for the :math:`i^{th}` face.
            boundary_zones (2D array of `integers <int>`, optional): Zero-based
                indices of the zones for each entry given in *elements*. This
                must be the same shape as *elements*.

        See the code example for the `Facemap` class object for details.
        """
        nfacenodes = sum(len(n) for n in facemap)
        if boundary_elements is not None:
            nbfaces = len(boundary_elements)
            nbelems = sum(len(n) for n in boundary_elements)
        else:
            nbfaces = 0
            nbelems = 0

        if __debug__:
            log.debug(dedent('''\
                Facemap alloc:
                    num face nodes: {}
                    num boundary faces: {}
                    num boundary elements: {}'''.format(nfacenodes, nbfaces,
                                                        nbelems)))

        self.alloc(nfacenodes, nbfaces, nbelems)
        with self.assignment():
            self.set_nodes(facemap)
            self.set_elements(*elements)
            if boundary_elements is not None:
                self.set_boundary_connections(boundary_elements, boundary_zones)

    @contextmanager
    def assignment(self):
        """Context manager for assigning facemap connections.

        This context ensures the proper book keeping is done when setting the
        connectivity list and must be used with `Facemap.set_nodes()`,
        `Facemap.set_elements()` and `Facemap.set_boundary_connections()`,
        which are used to define the connectivity of the zone.
        """
        with lock():
            ref = self._native_reference(writable=True)
            _tecutil.DataFaceMapBeginAssign(ref)
            try:
                yield
            finally:
                if not _tecutil.DataFaceMapEndAssign(ref):
                    raise TecplotSystemError()

    def set_elementmap(self, elementmap):
        """Define connectivity per element.

        Parameters:
            elementmap (`integers <int>`): Zero-based indices of the nodes that
                make up each face of each element. For polygons, the map is a
                list of elements, each made of up a list of nodes. For
                polyhedrons, this is a list of elements, made up a list of
                faces, each made up of a list of nodes.

        .. warning::

            This method is mutually exclusive with the `Facemap.set_mapping()`
            and `Facemap.assignment()`, `Facemap.set_nodes()`,
            `Facemap.set_elements()` and `Facemap.set_boundary_connections()`
            family of methods. The size of the underlying arrays are calculated
            based on the elementmap given and a call to `Facemap.alloc()` is
            made which will override any previous allocation.

        This may be a more convenient way to describe the connectivity of a
        polytope zone, however it does not support boundary face connections to
        other zones (see `Facemap.set_mapping()`).

        Here is an example of an elementmap for two triangles (polygons)::

            nodes = ((0, 0, 0  ),
                     (1, 0, 0.5),
                     (0, 1, 0.5),
                     (1, 1, 1  ))
            elementmap = ((0, 1, 2),  # polygon 0, 3 faces
                          (1, 3, 2))  # polygon 1, 3 faces

        This is an example of an elementmap for two tetrahedrons
        (polyhedrons)::

            nodes = ((0, 0, 0),
                     (1, 1, 0),
                     (1, 0, 1),
                     (0, 1, 1),
                     (0, 0, 1))
            elementmap = (((0, 1, 2),  # polyhedron 0, 4 faces
                           (0, 1, 3),
                           (1, 3, 2),
                           (0, 2, 3)),
                          ((0, 2, 3),  # polyhedron 1, 4 faces
                           (2, 3, 4),
                           (0, 2, 4),
                           (0, 4, 3)))

        """
        nelems = len(elementmap)

        faces = [len(e) for e in elementmap]
        faces = (c_int32 * len(faces))(*faces)

        if self.zone.zone_type == ZoneType.FEPolygon:
            nodes = None
            elemmap = [n + 1 for face in elementmap for n in face]
        else:  # if self.zone.zone_type == ZoneType.FEPolyhedron:
            nodes = [len(face) for elem in elementmap for face in elem]
            nodes = (c_int32 * len(nodes))(*nodes)
            elemmap = [n + 1 for elem in elementmap
                       for face in elem
                       for n in face]

        elemmap = (c_int32 * len(elemmap))(*elemmap)

        if __debug__:
            if len(elemmap):
                if min(elemmap) < 1 or self.num_unique_nodes < max(elemmap):
                    raise TecplotIndexError
            log.debug(dedent('''\
                FaceMapAssign:
                    nelems: {}
                    faces: {}
                    nodes: {}
                    elemmap: {}''').format(nelems, array_to_str(faces),
                                           array_to_str(nodes),
                                           array_to_str(elemmap)))

        # reset facemap before we fill it with the nodemap
        if self.zone.zone_type == ZoneType.FEPolygon:
            self.alloc(int(self.zone.num_faces * self.num_nodes(0)))
        else:
            self.alloc(0)

        with lock():
            ref = self._native_reference(writable=True)
            if not _tecutil.DataFaceMapAssignElemToNodeMap(ref, nelems, faces,
                                                           nodes, elemmap):
                raise TecplotSystemError()
