"""
Zones describe the size, shape, element (cell) geometry, connectivity and
solution time of arrays in a dataset. Zones created as "ordered," "classic
finite-element," or "polytopal finite-element" along with the number of nodes
and elements which can not be changed (without creating a new zone). Ordered
zones are always considered to be logically-rectangular grids of one, two or
three dimensions depending on the shape. Classic finite-element zones must use
a fixed-type element throughout. This means that each element has the same
number of faces and nodes. Polytopal zones can have a varying number of faces
and nodes for each element. The connectivity is implied in ordered zones and
explicitly provided by the user for finite-element zones.

In PyTecplot, there are three zone class objects: `OrderedZone`,
`ClassicFEZone` and `PolyFEZone`. The `OrderedZone` and `ClassicFEZone` classes
use the `FaceNeighbors` class to handle "global" face-neighbor connections from
one zone to another. The connectivity for the `ClassicFEZone` objects are
accessed through the `Nodemap` class. The `PolyFEZone` objects provide element
definition and connectivity access through the `Facemap` class.
"""
from builtins import int

import logging

from functools import reduce
from six import string_types
from textwrap import dedent

from ..tecutil import _tecutil, _tecutil_connector
from ..constant import *
from ..exception import *
from .. import session, layout, version
from ..tecutil import Index, inherited_property, lock, lock_attributes
from .array import Array
from .face_neighbors import FaceNeighbors
from .facemap import Facemap
from .nodemap import Nodemap

log = logging.getLogger(__name__)


@lock_attributes
class Zone(object):
    def __init__(self, uid, dataset):
        self.uid = uid
        self.dataset = dataset

    def __str__(self):
        """Brief string representation.

        Returns:
            `string <str>`: Brief representation of this `Zone <data_access>`,
            showing a list of associated `Variables <Variable>`.

        Example::

            >>> rect_zone = dataset.zone('Rectangular zone')
            >>> print(rect_zone)
            Zone: 'Rectangular zone'
              Type: Ordered
              Shape: (10, 10, 10)
        """
        fmt = dedent('''\
            Zone: '{}'
              Type: {}
              Shape: {}''')
        return fmt.format(self.name, self.zone_type.name, self._shape)

    def __repr__(self):
        """Executable string representation.

        Returns:
            `string <str>`: Internal representation of this `Zone
            <data_access>`.

        The string returned can be executed to generate a clone of this
        `Zone <data_access>` object::

            >>> rectzone = dataset.zone('Rectangular zone')
            >>> print(repr(rectzone))
            Zone(uid=31, Dataset(uid=21, frame=Frame(uid=11, page=Page(uid=1)))
            >>> exec('rectzone_clone = '+repr(rectzone))
            >>> rectzone_clone
            Zone(uid=31, Dataset(uid=21, frame=Frame(uid=11, page=Page(uid=1)))
            >>> rectzone == rectzone_clone
            True
        """
        return 'Zone(uid={uid}, dataset={dataset})'.format(
            uid=self.uid, dataset=repr(self.dataset))

    def __eq__(self, other):
        """Checks for equality in the |Tecplot Engine|.

        Returns:
            `bool`: `True` if the unique ID numbers are the same for both
            `Zones <data_access>`.
        """
        return self.uid == other.uid

    def __ne__(self, other):
        return not (self == other)

    @property
    def aux_data(self):
        """Auxiliary data for this zone.

        Returns:
            `AuxData`

        This is the auxiliary data attached to the zone. Such data is
        written to the layout file by default and can be retrieved later.
        Example usage::

            >>> frame = tp.active_frame()
            >>> aux = frame.dataset.zone('My Zone').aux_data
            >>> aux['X_weighted_avg'] = '3.14159'
            >>> print(aux['X_weighted_avg'])
            3.14159
        """
        return session.AuxData(self.dataset.frame, AuxDataObjectType.Zone,
                               self.index)

    @property
    def index(self):
        """Zero-based position within the parent `Dataset`.

        :type: `Index`

        This is the value used to obtain a specific zone if you have
        duplicately named zones in the dataset::

            >>> tp.new_layout()
            >>> frame = tp.active_frame()
            >>> dataset = frame.create_dataset('Dataset', ['x', 'y'])
            >>> dataset.add_ordered_zone('Zone', (10,10,10))
            >>> dataset.add_ordered_zone('Zone', (3,3,3))
            >>> # getting zone by name always returns first match
            >>> print(dataset.zone('Zone').index)
            0
            >>> # use index to get specific zone
            >>> print(dataset.zone(1).dimensions)
            (3, 3, 3)
        """
        return Index(_tecutil.ZoneGetNumByUniqueID(self.uid) - 1)

    @property
    def strand(self):
        """The strand ID number.

        :type: `integer <int>`

        Example usage::

            >>> dataset.zone('My Zone').strand = 2

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
        if version.sdk_version_info < (2017, 3):
            log.info(MESSAGES.PERFORMANCE_IMPROVEMENTS)
            with self.dataset.frame.activated():
                return _tecutil.ZoneGetStrandID(self.index + 1)
        else:
            return _tecutil.ZoneGetStrandIDByDataSetID(self.dataset.uid,
                                                       self.index + 1)

    @strand.setter
    @lock()
    def strand(self, value):
        if __debug__:
            if not isinstance(value, int):
                raise TecplotTypeError('strand must be an integer.')
        if version.sdk_version_info < (2017, 3):
            log.info(MESSAGES.PERFORMANCE_IMPROVEMENTS)
            with self.dataset.frame.activated():
                _tecutil.ZoneSetStrandID(self.index + 1, int(value))
        else:
            _tecutil.ZoneSetStrandIDByDataSetID(self.dataset.uid,
                                                self.index + 1, int(value))

    @property
    def solution_time(self):
        """The solution time for this zone.

        :type: `float`

        Example usage::

            >>> dataset.zone('My Zone').solution_time = 3.14

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
        return _tecutil.ZoneGetSolutionTime(self.index + 1)

    @solution_time.setter
    @lock()
    def solution_time(self, value):
        with self.dataset.frame.activated():
            _tecutil.ZoneSetSolutionTime(self.index + 1, float(value))

    @property
    def zone_type(self):
        if version.sdk_version_info < (2017, 3):
            log.info(MESSAGES.PERFORMANCE_IMPROVEMENTS)
            with self.dataset.frame.activated():
                return _tecutil.ZoneGetType(self.index + 1)
        else:
            return _tecutil.ZoneGetTypeByDataSetID(self.dataset.uid,
                                                   self.index + 1)

    @property
    def name(self):
        """The name of the zone.

        :type: `string <str>`

        Example usage::

            >>> dataset.zone(0).name = 'Zone 0'
        """
        res, zname = _tecutil.ZoneGetNameByDataSetID(self.dataset.uid,
                                                     self.index + 1)
        if not res:
            raise TecplotSystemError()
        return zname

    @name.setter
    @lock()
    def name(self, name):
        _tecutil.ZoneRenameByDataSetID(self.dataset.uid, self.index + 1, name)

    @property
    def num_variables(self):
        """Number of `Variables <Variable>` in the parent `Dataset`.

        :type: `integer <int>`

        Example usage, iterating over all variables by index::

            >>> for i in range(dataset.num_variables):
            ...     variable = dataset.variable(i)
        """
        return self.dataset.num_variables

    def values(self, pattern):
        """Returns an `Array` by index or string pattern.

        Parameters:
            pattern (`integer <int>` or `string <str>`): Zero-based index,
                `glob-style pattern <fnmatch.fnmatch>` in which case, the first
                match is returned, or a `Variable` object.

        The `Variable.name` attribute is used to match the *pattern* to the
        desired `Array` though this is not necessarily unique::

            >>> ds = frame.dataset
            >>> print(ds)
            Dataset:
              Zones: ['Rectangular zone']
              Variables: ['x', 'y', 'z']
            >>> zone = ds.zone('Rectangular zone')
            >>> x = zone.values('x')
            >>> x == zone.values(0)
            True
        """
        if isinstance(pattern, (string_types, int)):
            variable_id = pattern
        else:
            variable_id = pattern.index
        return Array(self, self.dataset.variable(variable_id))

    def copy(self, share_variables=False):
        """Duplicate this `Zone <data_access>` in the parent `Dataset`.

        The name is also copied but can be changed after duplication.

        Parameters:
            share_variables (`bool` or `list` of `Variables <Variable>`):
                Variables to be shared between original and generated zones.
                If variables are not shared they will be created as passive
                variables.
                Default: `False`.

        Returns:
            `Zone <data_access>`: The newly created zone.

        Example::

            >>> new_zone = dataset.zone('My Zone').copy()
            >>> print(new_zone.name)
            My Zone
            >>> new_zone.name = 'My Zone Copy'
            >>> print(new_zone.name)
            My Zone Copy
        """
        return self.dataset.copy_zones(self, share_variables=share_variables)[0]

    @property
    def _shape(self):
        return _tecutil.ZoneGetIJKByUniqueID(self.dataset.uid, self.index + 1)

    @property
    def num_faces(self):
        """Number of faces in this zone.

        :type: `integer <int>`

        This is the same as the number of elements times the number of faces
        per element. Example usage::

            >>> print(dataset.zone('My Zone').num_faces)
            1048576
        """
        return self.num_elements * self.num_faces_per_element


class OrderedZone(Zone):
    """An ordered ``(i, j, k)`` zone within a `Dataset`.

    Ordered zones contain nodal or cell-centered arrays where the connectivity
    is implied by the dimensions and ordering of the data.

    `Zones <data_access>` can be identified (uniquely) by the index with their
    parent `Dataset` or (non-uniquely) by name. In general, a `Variable` must
    be selected to access the underlying data array. This object is used by
    fieldmaps and linemaps to apply style to specific zones. Here we obtain the
    fieldmap associated with the zone named 'My Zone'::

        >>> fmap = plot.fieldmap(dataset.zone('My Zone'))
    """

    @property
    def dimensions(self):
        """Nodal dimensions along ``(i, j, k)``.

        Returns:
            `tuple` of `integers <int>`: ``(i, j, k)`` for ordered data.

        Example usage::

            >>> print(zone.dimensions)
            (128, 128, 128)
        """
        return self._shape

    @property
    def rank(self):
        """Number of dimensions of the data array.

        :type: `integer <int>`

        This will return the number of dimensions which contain more than one
        value::

            >>> zone = dataset.zone('My Zone')
            >>> print(zone.dimensions)
            (10, 10, 1)
            >>> print(zone.rank)
            2
        """
        return sum(s > 1 for s in self.dimensions)

    @property
    def num_points(self):
        """Total number of nodes within this zone.

        :type: `integer <int>`

        This is number of nodes within the zone and is equivalent to the
        product of the values in `OrderedZone.dimensions`. Example usage::

            >>> zone = dataset.zone('My Zone')
            >>> print(zone.dimensions)
            (128, 128, 128)
            >>> print(zone.num_points)
            2097152
        """
        return reduce(lambda x, y: x * y, self.dimensions, 1)

    @property
    def num_elements(self):
        """Number of cells in this zone.

        :type: `integer <int>`

        Example usage::

            >>> zone = dataset.zone('My Zone')
            >>> print(zone.dimensions)
            (128, 128, 128)
            >>> print(zone.num_elements)
            2048383
        """
        reduced_shape = list(filter(lambda x: x > 1, self.dimensions))
        return reduce(lambda x, y: x * (y - 1), reduced_shape or [1], 1)

    @property
    def num_points_per_element(self):
        """Points per cell for ordered zones.

        :type: `integer <int>`

        For ordered zones, this is :math:`2^{d}` where :math:`d` is the number
        of dimensions greater than one:

            ==== =================
            Rank Faces Per Element
            ==== =================
            0    0
            1    2
            2    4
            3    8
            ==== =================

        Example usage::

            >>> zone = dataset.zone('My Zone')
            >>> print(zone.dimensions)
            (10, 10, 1)
            >>> print(zone.rank)
            2
            >>> print(zone.num_points_per_element)
            4
        """
        ndim = self.rank
        return 2**ndim if ndim > 0 else 0

    @property
    def num_faces_per_element(self):
        """Number of faces per element in this ordered zone.

        :type: `integer <int>`

        This is determined by the rank of the zone:

            ==== =================
            Rank Faces Per Element
            ==== =================
            0    0
            1    1
            2    4
            3    6
            ==== =================

        Example usage::

            >>> zone = dataset.zone('My Zone')
            >>> print(zone.dimensions)
            (1, 10, 10)
            >>> print(zone.rank)
            2
            >>> print(zone.num_faces_per_element)
            4
        """
        _fpe = {0: 0, 1: 1, 2: 4, 3: 6}
        return _fpe[self.rank]

    @inherited_property(Zone)
    def zone_type(self):
        """The `ZoneType` indicating structure of the data contained.

        :type: `ZoneType`

        The specific type of zone this object represents::

            >>> print(dataset.zone(0).zone_type)
            ZoneType.Ordered
        """

    @property
    def face_neighbors(self):
        """The face neighbor list for this ordered zone.

        :type: `FaceNeighbors`

        Example usage::

            >>> zone = dataset.zone(0)
            >>> print(zone.face_neighbors.mode)
            FaceNeighborMode.LocalOneToOne
        """
        return FaceNeighbors(self)


class FEZone(Zone):
    @property
    def num_points(self):
        """Total number of nodes within this zone.

        :type: `integer <int>`

        This is the total number of nodes in the zone. Example usage::

            >>> print(dataset.zone('My Zone').num_points)
            2048
        """
        return self._shape[0]

    @property
    def num_elements(self):
        """Number of cells in this finite-element zone.

        :type: `integer <int>`

        Example usage::

            >>> print(dataset.zone('My Zone').num_elements)
            1048576
        """
        return self._shape[1]

    @property
    def shared_connectivity(self):
        """`list` of `Zones <data_access>` sharing connectivity.

        :type: `list` of `Zones <data_access>`

        Example usage::

            >>> dataset.zone('My Zone').copy()
            >>> for zone in dataset.zone('My Zone').shared_connectivity:
            ...     print(zone.index)
            0
            1
        """
        indices = _tecutil.ConnectGetShareZoneSet(self.index + 1)
        ret = [self.dataset.zone(i) for i in indices]
        indices.dealloc()
        return ret


class ClassicFEZone(FEZone):
    """A classic finite-element zone within a `Dataset`.

    Classic finite-element zones are arrays of nodes that are connected
    explicitly into pre-defined geometric shapes called "elements." The
    geometry is consistent across the whole zone so that the number of nodes
    per element is constant.

    `Zones <data_access>` can be identified (uniquely) by the index with their
    parent `Dataset` or (non-uniquely) by name. In general, a `Variable` must
    be selected to access the underlying data array. This object is used by
    fieldmaps and linemaps to apply style to specific zones. Here we obtain the
    fieldmap associated with the zone named 'My Zone'::

        >>> fmap = plot.fieldmap(dataset.zone('My Zone'))
    """

    @property
    def num_points_per_element(self):
        """Points per element for classic finite-element zones.

        :type: `integer <int>`

        The number of points (also known as nodes) per finite-element is
        determined from the ``zone_type`` parameter. The follow table shows the
        number of points per element for the available zone types along with
        the resulting shape of the nodemap based on the number of points
        specified (:math:`N`):

            ============== ============== ========================
            Zone Type      Points/Element Nodemap Shape
            ============== ============== ========================
            ``FELineSeg``  2              (:math:`N`, :math:`2 N`)
            ``FETriangle`` 3              (:math:`N`, :math:`3 N`)
            ``FEQuad``     4              (:math:`N`, :math:`4 N`)
            ``FETetra``    4              (:math:`N`, :math:`4 N`)
            ``FEBrick``    8              (:math:`N`, :math:`8 N`)
            ============== ============== ========================

        Example usage::

            >>> zone = dataset.zone('My Zone')
            >>> print(zone.zone_type)
            ZoneType.FETriangle
            >>> print(zone.num_points_per_element)
            3
        """
        return self.nodemap.num_points_per_element

    @property
    def nodemap(self):
        """The connectivity `Nodemap` for this classic finite-element zone.

        :type: `Nodemap`

        Example usage::

            >>> zone = dataset.zone(0)
            >>> print(zone.nodemap.num_points_per_element)
            4
        """
        return Nodemap(self)

    @property
    def face_neighbors(self):
        """The face neighbor list for this finite-element zone.

        :type: `FaceNeighbors`

        Example usage::

            >>> zone = dataset.zone(0)
            >>> print(zone.face_neighbors.mode)
            FaceNeighborMode.LocalOneToMany
        """
        return FaceNeighbors(self)

    @inherited_property(Zone)
    def zone_type(self):
        """The `ZoneType` indicating structure of the data contained.

        :type: `ZoneType`

        The specific type of zone this object represents::

            >>> print(dataset.zone(0).zone_type)
            ZoneType.FEBrick
        """

    @property
    def rank(self):
        """Number of dimensions of the data array.

        :type: `integer <int>`

        This indicates the dimensionality of the data and is dependent on the
        type of element this zone contains:

            ============== ====
            Zone Type      Rank
            ============== ====
            ``FELineSeg``  1
            ``FETriangle`` 2
            ``FEQuad``     2
            ``FETetra``    3
            ``FEBrick``    3
            ============== ====

        Example usage::

            >>> zone = dataset.zone('My Zone')
            >>> print(zone.zone_type)
            ZoneType.FEBrick
            >>> print(zone.rank)
            3
        """
        _rank = {ZoneType.FELineSeg: 1,
                 ZoneType.FETriangle: 2,
                 ZoneType.FEQuad: 2,
                 ZoneType.FETetra: 3,
                 ZoneType.FEBrick: 3}
        return _rank[self.zone_type]

    @property
    def num_faces_per_element(self):
        """Number of faces per element.

        :type: `integer <int>`

        This is dependent on the type of element this zone contains:

            ============== =================
            Zone Type      Faces Per Element
            ============== =================
            ``FELineSeg``  1
            ``FETriangle`` 3
            ``FEQuad``     4
            ``FETetra``    4
            ``FEBrick``    6
            ============== =================

        Example usage::

            >>> print(dataset.zone('My Zone').num_faces_per_element)
            4
        """
        _fpe = {ZoneType.FELineSeg: 1,
                ZoneType.FETriangle: 3,
                ZoneType.FEQuad: 4,
                ZoneType.FETetra: 4,
                ZoneType.FEBrick: 6}
        return _fpe[self.zone_type]


class PolyFEZone(FEZone):
    """A polygonal finite-element zone within a `Dataset`.

    A polygonal zone consists of arrays of nodes which are connected explicitly
    into arbitrary and varying geometric elements. These elements are 2D or 3D
    in nature and have a number of faces (connections between nodes) which hold
    the concept of a left and right neighbor.

    `Zones <data_access>` can be identified (uniquely) by the index with their
    parent `Dataset` or (non-uniquely) by name. In general, a `Variable` must
    be selected to access the underlying data array. This object is used by
    fieldmaps and linemaps to apply style to specific zones. Here we obtain the
    fieldmap associated with the zone named 'My Zone'::

        >>> fmap = plot.fieldmap(dataset.zone('My Zone'))
    """

    @property
    def num_faces(self):
        """Number of faces in this finite-element zone.

        :type: `integer <int>`

        The number of faces may be ``0`` if unknown or facemap creation is
        deferred. Example usage::

            >>> print(dataset.zone('My Zone').num_faces)
            1048576
        """
        return self._shape[2]

    @property
    def rank(self):
        """Number of dimensions of the data array.

        :type: `integer <int>`

        This indicates the dimensionality of the data and is dependent on the
        type of element this zone contains:

            ================ ====
            Zone Type        Rank
            ================ ====
            ``FEPolygon``    2
            ``FEPolyhedron`` 3
            ================ ====

        Example usage::

            >>> zone = dataset.zone('My Zone')
            >>> print(zone.zone_type)
            ZoneType.FEPolygon
            >>> print(zone.rank)
            2
        """
        _rank = {ZoneType.FEPolygon: 2,
                 ZoneType.FEPolyhedron: 3}
        return _rank[self.zone_type]

    @property
    def facemap(self):
        """The connectivity `Facemap` for this polygonal finite-element zone.

        :type: `Facemap`

        Example usage::

            >>> zone = dataset.zone(0)
            >>> print(zone.facemap.num_faces)
            4500
        """
        return Facemap(self)

    @inherited_property(Zone)
    def zone_type(self):
        """The `ZoneType` indicating structure of the data contained.

        :type: `ZoneType`

        The specific type of zone this object represents::

            >>> print(dataset.zone(0).zone_type)
            ZoneType.FEPolygon
        """
