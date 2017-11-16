from builtins import super

import ctypes
import itertools as it
import logging
import re

from collections import namedtuple, Iterable
from fnmatch import fnmatch
from functools import reduce
from keyword import iskeyword
from six import string_types
from textwrap import dedent, TextWrapper

from ..tecutil import _tecutil, _tecutil_connector
from ..constant import *
from ..exception import *
from .. import layout, session, version
from ..tecutil import (ArgList, Index, IndexRange, IndexSet, ListWrapper,
                       StringList, flatten_args, lock, lock_attributes, sv)
from .variable import Variable
from .zone import ClassicFEZone, OrderedZone, PolyFEZone, Zone

log = logging.getLogger(__name__)


@lock_attributes
class Dataset(object):
    """Table of `Arrays <Array>` identified by `Zone <data_access>` and `Variable`.

    This is the primary data container within the Tecplot Engine. A `Dataset`
    can be shared among several `Frames <Frame>`, though any particular
    `Dataset` object will have a handle to at least one of them. Any
    modification of a shared `Dataset` will be reflected in all `Frames
    <Frame>` that use it.

    Though a `Dataset` is usually attached to a `Frame` and the plot style
    associated with that, it can be thought of as independent from any style or
    plotting representation. Each `Dataset` consists of a list of `Variables
    <Variable>` which are used by one or more of a list of `Zones
    <data_access>`. The `Variable` determines the data type, while the `Zone
    <data_access>` determines the layout such as shape and ordered vs
    unordered.

    The actual data are found at the intersection of a `Zone <data_access>` and
    `Variable` and the resulting object is an `Array`. The data array can be
    obtained using either path::

        >>> # These two lines obtain the same object "x"
        >>> x = dataset.zone('My Zone').values('X')
        >>> x = dataset.variable('X').values('My Zone')

    A `Dataset` is the object returned by most data-loading operations in
    |PyTecplot|::

        >>> dataset = tecplot.data.load_tecplot('my_data.plt')

    Under `Dataset`, there are a number methods to create and delete `Zones
    <data_access>` and `variables <Variable>`.
    """
    def __init__(self, uid, frame):
        self.uid = uid
        self.frame = frame

    def __repr__(self):
        """Executable string representation.

        Returns:
            `string <str>`: Internal representation of this `Dataset`.

        The string returned can be executed to generate a
        clone of this `Dataset` object::

            >>> dataset = frame.dataset
            >>> print(repr(dataset))
            Dataset(uid=21, frame=Frame(uid=11, page=Page(uid=1)))
            >>> exec('dataset_clone = '+repr(dataset))
            >>> dataset_clone
            Dataset(uid=21, frame=Frame(uid=11, page=Page(uid=1)))
            >>> dataset == dataset_clone
            True
        """
        return 'Dataset(uid={uid}, frame={frame})'.format(
            uid=self.uid, frame=repr(self.frame))

    def __str__(self):
        """Brief string representation.

        Returns:
            `string <str>`: Brief representation of this `Dataset`, showing
            `Zones <data_access>` and `Variables <Variable>`.

        Example::

            >>> dataset = frame.dataset
            >>> print(dataset)
            Dataset: 'My Dataset'
              Zones: 'Rectangular zone'
              Variables: 'x', 'y', 'z'
        """
        fmt = dedent('''\
            Dataset: '{}'
              Zones: {}
              Variables: {}''')
        maxwidth = 79
        wrapper = ListWrapper(initial_width=maxwidth - len('  Zones: '),
                              subsequent_indent='    ',
                              subsequent_width=maxwidth)
        zones = wrapper.fill(z.name for z in self.zones())
        wrapper.initial_width = maxwidth - len('  Variables: ')
        variables = wrapper.fill(v.name for v  in self.variables())
        return fmt.format(self.title, zones, variables)

    def __eq__(self, other):
        """Checks for equality in the |Tecplot Engine|.

        Returns:
            `bool`: `True` if the unique ID numbers are the same for both
            `Datasets <Dataset>`.

        This can be useful for determining if two `Frames <Frame>`
        are holding on to the same `Dataset`::

            >>> frame1.dataset == frame2.dataset
            True
        """
        return self.uid == other.uid

    def __ne__(self, other):
        return not self.__eq__(other)

    def __contains__(self, obj):
        if obj.dataset == self:
            if isinstance(obj, Variable) and obj == self.variable(obj.index):
                return True
            elif isinstance(obj, Zone) and obj == self.zone(obj.index):
                return True
        return False

    @property
    def aux_data(self):
        """Auxiliary data for this dataset.

        Returns:
            `AuxData`

        This is the auxiliary data attached to the dataset. Such data is
        written to the layout file by default and can be retrieved later.
        Example usage::

            >>> frame = tp.active_frame()
            >>> aux = frame.dataset.aux_data
            >>> aux['Result'] = '3.14159'
            >>> print(aux['Result'])
            3.14159
        """
        return session.AuxData(self.frame, AuxDataObjectType.Dataset)

    @property
    def title(self):
        """Title of this `Dataset`.

        :type: `string <str>`

        Example usage::

            >>> dataset.title = 'My Data'

        .. versionchanged:: 2017.3 of Tecplot 360
            The dataset title property requires Tecplot 360 2017 R3 or later.
        """
        if __debug__:
            sdk_required = (2017, 3)
            if version.sdk_version_info < sdk_required:
                raise TecplotOutOfDateEngineError(sdk_required)
        success, title, _, _ = _tecutil.DataSetGetInfoByUniqueID(self.uid)
        if not success:
            raise TecplotSystemError()
        return title

    @title.setter
    @lock()
    def title(self, title):
        if __debug__:
            sdk_required = (2017, 3)
            if version.sdk_version_info < sdk_required:
                raise TecplotOutOfDateEngineError(sdk_required)
        if not _tecutil.DataSetSetTitleByUniqueID(self.uid, title):
            raise TecplotSystemError()

    @property
    def num_zones(self):
        """Number of `Zones <data_access>` in this `Dataset`.

        :type: `integer <int>`

        This count includes disabled zones which were skipped when loading the
        data. Example usage::

            >>> for i in range(dataset.num_zones):
            ...     zone = dataset.zone(i)
        """
        return _tecutil.DataSetGetNumZonesByUniqueID(self.uid)

    def zone(self, pattern):
        """Returns `Zone <data_access>` by index or string pattern.

        Parameters:
            pattern (`integer <int>` or `string <str>`):  Zero-based index or
                `glob-style pattern <fnmatch.fnmatch>` in which case, the
                first match is returned.

        Returns:
            `OrderedZone`, `ClassicFEZone` or `PolyFEZone` depending on the
            zone type.

        Raises:
            `TecplotIndexError`

        The `Zone.name <OrderedZone.name>` attribute is used to match the
        *pattern* to the desired `Zone <data_access>` though this is not
        necessarily unique::

            >>> ds = frame.dataset
            >>> print(ds)
            Dataset:
              Zones: ['Rectangular zone']
              Variables: ['x', 'y', 'z']
            >>> rectzone = ds.zone('Rectangular zone')
            >>> rectzone == ds.zone(0)
            True
        """
        _dispatch = {
            ZoneType.Ordered: OrderedZone,
            ZoneType.FELineSeg: ClassicFEZone,
            ZoneType.FETriangle: ClassicFEZone,
            ZoneType.FEQuad: ClassicFEZone,
            ZoneType.FETetra: ClassicFEZone,
            ZoneType.FEBrick: ClassicFEZone,
            ZoneType.FEPolygon: PolyFEZone,
            ZoneType.FEPolyhedron: PolyFEZone}
        if isinstance(pattern, string_types):
            try:
                return next(self.zones(pattern))
            except StopIteration:
                raise TecplotPatternMatchError(
                    pattern,
                    'no zone found with name: "{}"'.format(pattern),
                    'glob')
        else:
            if pattern < 0:
                pattern += self.num_zones
            if 0 <= pattern < self.num_zones:
                if version.sdk_version_info < (2017, 3):
                    log.info(MESSAGES.PERFORMANCE_IMPROVEMENTS)
                    with self.frame.activated():
                        if not _tecutil.ZoneIsEnabled(pattern + 1):
                            msg = 'zone {} is not enabled'.format(pattern)
                            raise TecplotIndexError(msg)
                else:
                    if not _tecutil.ZoneIsEnabledByDataSetID(self.uid, pattern + 1):
                        msg = 'zone {} is not enabled'.format(pattern)
                        raise TecplotIndexError(msg)
                uid = _tecutil.ZoneGetUniqueIDByDataSetID(self.uid,
                    pattern + 1)
                ztype = Zone(uid, self).zone_type
                return _dispatch[ztype](uid, self)
        raise TecplotIndexError

    def zones(self, pattern=None):
        """Yields all `Zones <data_access>` matching a *pattern*.

        Parameters:
            pattern (`string <str>` pattern, optional): `glob-style pattern
                <fnmatch.fnmatch>` used to match zone names or `None` which
                will return all zones. (default: `None`)

        Returns:
            `OrderedZone`, `ClassicFEZone` or `PolyFEZone` depending on the
            zone type.

        Example usage::

            >>> for zone in dataset.zones('A*'):
            ...     x_array = zone.variable('X')

        Use list comprehension to construct a list of all zones with 'Wing'
        in the zone name::

            >>> wing_zones = [Z for Z in dataset.zones() if 'Wing' in Z.name]
        """
        if pattern is None:
            for i in range(self.num_zones):
                try:
                    yield self.zone(i)
                except TecplotIndexError:
                    # zone not enabled
                    continue
        elif version.sdk_version_info < (2017, 3):
            log.info(MESSAGES.PERFORMANCE_IMPROVEMENTS)
            for i in range(self.num_zones):
                try:
                    zone = self.zone(i)
                    if fnmatch(zone.name, pattern):
                        yield zone
                except TecplotIndexError:
                    # zone not enabled
                    continue
        else:
            success, ptr = _tecutil.ZoneGetEnabledByDataSetID(self.uid)
            if not success:
                raise TecplotSystemError()
            indices = ctypes.cast(ptr, IndexSet)

            success, ptr = _tecutil.ZoneGetEnabledNamesByDataSetID(self.uid)
            if not success:
                indices.dealloc()
                raise TecplotSystemError()
            names = ctypes.cast(ptr, StringList)

            try:

                for index, name in zip(indices, names):
                    if fnmatch(name, pattern):
                        yield self.zone(index)
            finally:
                indices.dealloc()
                names.dealloc()

    @property
    def num_variables(self):
        """Number of `Variables <Variable>` in this `Dataset`.

        :type: `integer <int>`

        This count includes disabled variables which were skipped when the data
        was loaded. Example usage::

            >>> for i in range(dataset.num_variables):
            ...     variable = dataset.variable(i)
        """
        return _tecutil.DataSetGetNumVarsByUniqueID(self.uid)

    def variable(self, pattern):
        """Returns the `Variable` by index or string pattern.

        Parameters:
            pattern (`integer <int>` or `string <str>`):  Zero-based index or
                `glob-style pattern <fnmatch.fnmatch>` in which case, the
                first match is returned.

        Raises:
            `TecplotIndexError`

        The `Variable.name` attribute is used to match the *pattern* to the
        desired `Variable` though this is not necessarily unique::

            >>> ds = frame.dataset
            >>> print(ds)
            Dataset:
              Zones: ['Rectangular zone']
              Variables: ['x', 'y', 'z']
            >>> x = ds.variable('x')
            >>> x == ds.variable(0)
            True
        """
        if isinstance(pattern, string_types):
            try:
                return next(self.variables(pattern))
            except StopIteration:
                raise TecplotPatternMatchError(
                    pattern,
                    'no variable found with name: "{}".'.format(pattern),
                    'glob')
        else:
            if pattern < 0:
                pattern += self.num_variables
            if 0 <= pattern < self.num_variables:
                if not _tecutil.VarIsEnabledByDataSetID(self.uid, pattern + 1):
                    msg = 'variable {} is not enabled'.format(pattern)
                    raise TecplotIndexError(msg)
                return Variable(_tecutil.VarGetUniqueIDByDataSetID(
                                self.uid, pattern + 1), self)
        raise TecplotIndexError

    def variables(self, pattern=None):
        """Yields all `Variables <Variable>` matching a *pattern*.

        Parameters:
            pattern (`string <str>` pattern, optional): `glob-style pattern
                <fnmatch.fnmatch>` used to match variable names or `None` which
                will return all variables. (default: `None`)

        Example usage::

            >>> for variable in dataset.variables('A*'):
            ...     array = variable.values('My Zone')
        """
        if pattern is None:
            for i in range(self.num_variables):
                try:
                    yield self.variable(i)
                except TecplotIndexError:
                    # variable not enabled
                    continue
        elif version.sdk_version_info < (2017, 3):
            log.info(MESSAGES.PERFORMANCE_IMPROVEMENTS)
            for i in range(self.num_variables):
                try:
                    variable = self.variable(i)
                    if fnmatch(variable.name, pattern):
                        yield variable
                except TecplotIndexError:
                    # variable not enabled
                    continue
        else:
            success, ptr = _tecutil.VarGetEnabledByDataSetID(self.uid)
            if not success:
                raise TecplotSystemError()
            indices = ctypes.cast(ptr, IndexSet)

            success, ptr = _tecutil.VarGetEnabledNamesByDataSetID(self.uid)
            if not success:
                indices.dealloc()
                raise TecplotSystemError()
            names = ctypes.cast(ptr, StringList)

            try:
                for index, name in zip(indices, names):
                    if fnmatch(name, pattern):
                        yield self.variable(index)
            finally:
                indices.dealloc()
                names.dealloc()

    @property
    def VariablesNamedTuple(self):
        r"""A `collections.namedtuple` object using variable names.

        The variable names are transformed to be unique, valid identifiers
        suitable for use as the key-list for a `collections.namedtuple`.
        This means that all invalid characters such as spaces and dashes
        are converted to underscores, Python keywords are appended by an
        underscore, leading numbers or empty names are prepended with a "v"
        and duplicate variable names are indexed starting with zero, padded
        left with zeros variable names duplicated more than nine times. The
        following table gives some specific examples:

            ==================== ===========================
            Variable names       Resulting namedtuple fields
            ==================== ===========================
            ``'x', 'y'``         ``'x', 'y'``
            ``'x', 'x'``         ``'x0', 'x1'``
            ``'X', 'Y=f(X)'``    ``'X', 'Y_f_X_'``
            ``'x 2', '_', '_'``  ``'x_2', 'v0', 'v1'``
            ``'def', 'if'``      ``'def_', 'if_'``
            ``'1', '2', '3'``    ``'v1', 'v2', 'v3'``
            ==================== ===========================

        This example shows how one can use this n-tuple type with the
        result from a call to `tecplot.data.query.probe_at_position`::

            >>> from os import path
            >>> import tecplot as tp
            >>> examples_dir = tp.session.tecplot_examples_directory()
            >>> datafile = path.join(examples_dir,'SimpleData','DownDraft.plt')
            >>> dataset = tp.data.load_tecplot(datafile)
            >>> result = tp.data.query.probe_at_position(0,0.1,0.3)
            >>> data = dataset.VariablesNamedTuple(*result.data)
            >>> msg = '(RHO, E) = ({:.2f}, {:.2f})'
            >>> print(msg.format(data.RHO, data.E))
            (RHO, E) = (1.17, 252930.37)
        """
        # First we clean up variable names
        # and keep a count of each name used
        names = []
        count = {}
        for v in self.variables():
            # sub invalid characters with underscores
            name = re.sub(r'\W|^(?=\d)', r'_', v.name)
            # remove leading underscores
            name = re.sub(r'^_+', r'', name)
            # prepend leading number with 'v'
            name = re.sub(r'^(\d)', r'v\1', name)
            # append keywords with underscore
            if iskeyword(name):
                name = name + '_'
            # force non-empty variable names using 'v'
            if name == '':
                name = 'v'
            # add name to list
            names.append(name)
            # keep track of names to identify duplicates
            if name not in count:
                count[name] = 0
            count[name] += 1

        # append index, with padded zeros
        numbered = count.copy()
        for i,name in enumerate(names):
            if count[name] > 1:
                names[i] = '{0}{1:0{2}d}'.format(name,
                    count[name] - numbered[name], len(str(count[name] - 1)))
                numbered[name] -= 1

        return namedtuple('DatasetVariables', names)

    @lock()
    def copy_zones(self, *zones, **kwargs):
        """Copies `Zones <data_access>` within this `Dataset`.

        Parameters:
            *zones (`Zone <data_access>`, optional): Specific `Zones
                <data_access>` to copy. All zones will be copied if none are
                supplied.
            shared_variables (`bool` or `list` of `Variables <Variable>`):
                Variables to be shared between original and generated zones.
                (default: `False`)

        Returns:
            `list` of the newly created `Zones <data_access>`.

        Example usage::

            >>> new_zones = dataset.copy_zones()
        """
        share_variables = kwargs.pop('share_variables', False)

        if not share_variables:
            branch_variables = list(self.variables())
        elif isinstance(share_variables, Iterable):
            for idx, var in enumerate(share_variables):
                if not isinstance(var,Variable):
                    share_variables[idx]= self.variable(var)

            branch_variables = [v for v in self.variables()
                                if v not in share_variables]
        else:
            branch_variables = []

        num_zones = self.num_zones
        with IndexSet(*zones) as zoneset:
            with ArgList(SOURCEZONES=zoneset) as arglist:
                if __debug__:
                    log.debug('Zone copy:\n' + str(arglist))
                _tecutil.ZoneCopyX(arglist)

        new_zones = [self.zone(i) for i in range(num_zones, self.num_zones)]

        for zone in new_zones:
            for var in branch_variables:
                self.branch_variables(zone, var, True)

        return new_zones

    @lock()
    def add_variable(self, name, dtypes=None, locations=None):
        """Add a single `Variable` to the active `Dataset`.

        Parameters:
            name (`string <str>`): The name of the new `Variable`. This does not
                have to be unique.
            dtypes (`FieldDataType` or `list` of `FieldDataType`, optional):
                Data types of this `Variable` for each `Zone <data_access>` in
                the currently active `Dataset`. Options are:
                `FieldDataType.Float`, `Double <FieldDataType.Double>`,
                `Int32`, `Int16`, `Byte` and `Bit`. If a single value, this
                will be duplicated for all `Zones <data_access>`. (default:
                `None`)
            locations (`ValueLocation` or `list` of `ValueLocation`, optional):
                Point locations of this `Variable` for each
                `Zone <data_access>` in the currently active `Dataset`. Options
                are: `Nodal` and `CellCentered`. If a single value, this will
                be duplicated for all `Zones <data_access>`. (default: `None`)

        Returns:
            `Variable`

        The added `Variable` will be available for use in each `Zone
        <data_access>` of the dataset. This method should be used in
        conjunction with other data creation methods such as
        `Dataset.add_zone`:

        .. code-block:: python
            :emphasize-lines: 7-8

            import math
            import tecplot as tp
            from tecplot.constant import PlotType

            # Setup Tecplot dataset
            dataset = tp.active_frame().create_dataset('Data')
            dataset.add_variable('x')
            dataset.add_variable('s')
            zone = dataset.add_ordered_zone('Zone', 100)

            # Fill the dataset
            x = [0.1 * i for i in range(100)]
            zone.values('x')[:] = x
            zone.values('s')[:] = [math.sin(i) for i in x]

            # Set plot type to XYLine
            tp.active_frame().plot(PlotType.XYLine).activate()

            tp.export.save_png('add_variables.png', 600, supersample=3)

        ..  figure:: /_static/images/add_variables.png
            :width: 300px
            :figwidth: 300px
        """
        assert len(name) <= 128, 'Variable names are limited to 128 characters'
        with self.frame.activated():
            dataset = self.frame.dataset
            new_variable_index = dataset.num_variables
            with ArgList(NAME=name) as arglist:
                if dtypes is not None:
                    if not hasattr(dtypes, '__iter__'):
                        dtypes = [dtypes] * dataset.num_zones
                    arglist['VARDATATYPE'] = dtypes
                if locations is not None:
                    if not hasattr(locations, '__iter__'):
                        locations = [locations] * dataset.num_zones
                    arglist['VALUELOCATION'] = locations

                if __debug__:
                    msg = 'new variable: ' + name
                    for k, v in arglist.items():
                        msg += '\n  {} = {}'.format(k, v)
                    log.debug(msg)
                if not _tecutil.DataSetAddVarX(arglist):
                    raise TecplotSystemError()
            return dataset.variable(new_variable_index)

    @lock()
    def add_zone(self, zone_type, name, shape, dtypes=None, locations=None,
                 face_neighbor_mode=None, parent_zone=None, solution_time=None,
                 strand_id=None, index=None):
        """Add a single `Zone <data_access>` to this `Dataset`.

        Parameters:
            zone_type (`ZoneType`): The type of `Zone <data_access>` to be
                created. Possible values are: `Ordered`, `FETriangle`,
                `FEQuad`, `FETetra`, `FEBrick`, `FELineSeg`, `FEPolyhedron` and
                `FEPolygon`.
            name (`string <str>`): Name of the new `Zone <data_access>`. This
                does not have to be unique.
            shape (`integer <int>` or `list` of `integers <int>`): Specifies
                the length and dimension (up to three) of the new `Zone
                <data_access>`. A 1D `Zone <data_access>` is assumed if a
                single `int` is given. This is **(i, j, k)** for ordered `Zones
                <data_access>`, **(num_points, num_elements)** for
                finite-element `Zones <data_access>` and **(num_points,
                num_elements, num_faces)** for polytope `Zones <data_access>`
                where the number of faces is known.
            dtypes (`FieldDataType`, `list` of `FieldDataType`, optional): Data
                types of this `Zone <data_access>` for each `Variable` in the
                currently active `Dataset`. Options are: `Float
                <FieldDataType.Float>`, `Double <FieldDataType.Double>`,
                `Int32`, `Int16`, `Byte` and `Bit`. If a single value, this
                will be duplicated for all `Variables <Variable>`. If `None`
                then the type of the first `Variable`, defaulting to
                `FieldDataType.Float`, is used for all. (default: `None`)
            locations (`ValueLocation`, `list` of `ValueLocation`, optional):
                Point locations of this `Zone <data_access>` for each
                `Variable` in the currently active `Dataset`. Options are:
                `Nodal` and `CellCentered`. If a single value, this will be
                duplicated for all `Variables <Variable>`.  If `None` then the
                type of the first `Variable`, defaulting to `Nodal`, is used
                for all. (default: `None`)
            face_neighbor_mode (`FaceNeighborMode`, optional): Specifies the
                face-neighbor mode for this zone.  Options are:
                `FaceNeighborMode.LocalOneToOne` (default),
                `FaceNeighborMode.LocalOneToMany`,
                `FaceNeighborMode.GlobalOneToOne` or
                `FaceNeighborMode.GlobalOneToMany`.
            parent_zone (`Zone <data_access>`, optional): A parent `Zone
                <data_access>` to be used when generating surface-restricted
                streamtraces.
            solution_time (`float`, optional): Solution time for this zone.
                (default: 0)
            strand_id (`integer <int>`, optional): Associate this new `Zone
                <data_access>` with a particular strand.
            index (`integer <int>`, optional): Number of the zone to add or
                replace. If omitted or set to `None`, the new zone will be
                appended to the dataset. This value can be set to the number of
                a zone that already exists thereby replacing the existing zone.
                (default: `None`)

        Returns:
            `Zone <data_access>`

        The added `Zone <data_access>` will be able to use all `Variables
        <Variable>` defined in the  dataset. This method should be used in
        conjunction with other data creation methods such as
        `Frame.create_dataset`. Example usage::

            >>> from tecplot.constant import ZoneType
            >>> zone = dataset.add_zone(ZoneType.Ordered, 'Zone', (10, 10, 10))

        .. note::

            The relationship and meaning of this method's parameters change
            depending on the type of zone being created. Therefore, it is
            recommended to use the more specific zone creation methods:

                * `Dataset.add_ordered_zone`
                * `Dataset.add_fe_zone`
                * `Dataset.add_poly_zone`
        """
        if __debug__:
            if self.num_variables == 0:
                errmsg = dedent('''\
                Can not create a zone on a dataset with no variables.
                    Add at least one variable to this dataset before
                    creating any zones.''')
                raise TecplotLogicError(errmsg)

        with self.frame.activated():
            dataset = self.frame.dataset
            new_zone_index = dataset.num_zones if index is None else index
            with ArgList(ZONETYPE=zone_type, NAME=name) as arglist:
                # convert shape to (imax, jmax, kmax)
                if not hasattr(shape, '__iter__'):
                    shape = [shape]
                for k, v in zip([sv.IMAX, sv.JMAX, sv.KMAX], shape):
                    arglist[k] = v

                # expand data types and locations to length of num_variables
                for key, val in zip([sv.VARDATATYPE, sv.VALUELOCATION],
                                    [dtypes, locations]):
                    if val is not None:
                        if not hasattr(val, '__iter__'):
                            val = [val] * dataset.num_variables
                        arglist[key] = val

                if solution_time is not None:
                    arglist[sv.SOLUTIONTIME] = float(solution_time)

                if parent_zone is not None:
                    arglist[sv.PARENTZONE] = parent_zone.index + 1

                if face_neighbor_mode is not None:
                    arglist[sv.FACENEIGHBORMODE] = FaceNeighborMode(
                        face_neighbor_mode)

                if index is not None:
                    arglist[sv.ZONE] = index + 1

                if __debug__:
                    shp = '({})'.format(','.join(str(s) for s in shape))
                    msg = 'new dataset shape: ' + shp
                    for k, v in arglist.items():
                        msg += '\n  {} = {}'.format(k, v)
                    log.debug(msg)

                if not _tecutil.DataSetAddZoneX(arglist):
                    raise TecplotSystemError()

            new_zone = dataset.zone(new_zone_index)
            session.state_changed(StateChange.ZonesAdded, dataset=self)
            return new_zone

    def add_ordered_zone(self, name, shape, **kwargs):
        """Add a single ordered `Zone <data_access>` to this `Dataset`.

        Parameters:
            name (`string <str>`): Name of the new `Zone <data_access>`. This
                does not have to be unique.
            shape (`integer <int>` or `list` of `integers <int>`): Specifies
                the length and dimension **(i, j, k)** of the new
                `Zone <data_access>`. A 1D `Zone <data_access>` is assumed if a
                single `int` is given.
            **kwargs: These arguments are passed to `Dataset.add_zone`.

        .. seealso:: `Dataset.add_zone`

            Keyword arguments are passed to the parent zone creation method
            `Dataset.add_zone`.

        This example creates a 10x10x10 ordered zone of double-precision
        floating-point numbers::

            >>> from tecplot.constant import FieldDataType
            >>> my_zone = dataset.add_zone('My Zone', (10, 10, 10),
            ...                            dtype=FieldDataType.Double)

        Here is a full example:

        .. code-block:: python
            :emphasize-lines: 12,17,22

            import numpy as np
            import tecplot as tp
            from tecplot.constant import PlotType, Color

            # Generate data
            x = np.linspace(-4, 4, 100)

            # Setup Tecplot dataset
            dataset = tp.active_frame().create_dataset('Data', ['x', 'y'])

            # Create a zone
            zone = dataset.add_ordered_zone('sin(x)', len(x))
            zone.values('x')[:] = x
            zone.values('y')[:] = np.sin(x)

            # Create another zone
            zone = dataset.add_ordered_zone('cos(x)', len(x))
            zone.values('x')[:] = x
            zone.values('y')[:] = np.cos(x)

            # And one more zone
            zone = dataset.add_ordered_zone('tan(x)', len(x))
            zone.values('x')[:] = x
            zone.values('y')[:] = np.tan(x)

            # Set plot type to XYLine
            plot = tp.active_frame().plot(PlotType.XYLine)
            plot.activate()

            # Show all linemaps and make the lines a bit thicker
            for lmap in plot.linemaps():
                lmap.show = True
                lmap.line.line_thickness = 0.6

            plot.legend.show = True

            tp.export.save_png('add_ordered_zones.png', 600, supersample=3)

        ..  figure:: /_static/images/add_ordered_zones.png
            :width: 300px
            :figwidth: 300px
        """
        return self.add_zone(ZoneType.Ordered, name, shape, **kwargs)

    def add_fe_zone(self, zone_type, name, num_points, num_elements, **kwargs):
        r"""Add a single finite-element `Zone <data_access>` to this `Dataset`.

        Parameters:
            zone_type (`ZoneType`): The type of `Zone <data_access>` to be
                created. Possible values are: `FETriangle`, `FEQuad`,
                `FETetra`, `FEBrick` and `FELineSeg`.
            name (`string <str>`): Name of the new `Zone <data_access>`. This
                does not have to be unique.
            num_points (`integer <int>`): Number of points (nodes) in this
                zone.
            num_elements (`integer <int>`): Number of elements in this zone.
                The nodemap will have the shape (num_points, num_elements).
            **kwargs: These arguments are passed to `Dataset.add_zone`.

        .. seealso:: `Dataset.add_zone`

            Keyword arguments are passed to the parent zone creation method
            `Dataset.add_zone`.

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
        """
        assert zone_type in [ZoneType.FETriangle, ZoneType.FEQuad,
                             ZoneType.FETetra, ZoneType.FEBrick,
                             ZoneType.FELineSeg]
        return self.add_zone(zone_type, name, (num_points, num_elements),
                             **kwargs)

    def add_poly_zone(self, zone_type, name, num_points, num_elements,
                      num_faces=None, **kwargs):
        """Add a single polygonal `Zone <data_access>` to this `Dataset`.

        Parameters:
            zone_type (`ZoneType`): The type of `Zone <data_access>` to be
                created. Possible values are: `FEPolyhedron` and `FEPolygon`.
            name (`string <str>`): Name of the new `Zone <data_access>`. This
                does not have to be unique.
            num_points (`integer <int>`): Number of points in this zone.
            num_elements (`integer <int>`): Number of elements in this zone.
            num_faces (`integer <int>`, optional): Number of faces in this
                zone.
            **kwargs: These arguments are passed to `Dataset.add_zone`.

        .. seealso:: `Dataset.add_zone`

            Keyword arguments are passed to the parent zone creation method
            `Dataset.add_zone`.
        """
        assert zone_type in [ZoneType.FEPolyhedron, ZoneType.FEPolygon]
        return self.add_zone(zone_type, name, (num_points, num_elements,
                             num_faces), **kwargs)

    @lock()
    def delete_variables(self, *variables):
        """Remove `Variables <Variable>` from this `Dataset`.

        Parameters:
            *variables (`Variable` or index `integer <int>`): Variables to
                remove from this dataset.

        .. code-block:: python
            :emphasize-lines: 3

            >>> print([v.name for v in dataset.variables()])
            ['X','Y','Z']
            >>> dataset.delete_variables(dataset.variable('Z'))
            >>> print([v.name for v in dataset.variables()])
            ['X','Y']

        Notes:
            Multiple `Variables <Variable>` can be deleted at once, though
            the last `Variable` can not be deleted. This command deletes all
            but the first `Variable` in the `Dataset` (usually ``X``)::

                >>> # Try to delete all variables:
                >>> dataset.delete_variables(dataset.variables())
                >>> # Dataset requires at least one variable to
                >>> # exist, so it leaves the first one:
                >>> print([v.name for v in dataset.variables()])
                ['X']
        """
        variables = flatten_args(*variables)
        with self.frame.activated():
            with IndexSet(*variables) as vlist:
                _tecutil.DataSetDeleteVar(vlist)

    @lock()
    def delete_zones(self, *zones):
        """Remove `Zones <data_access>` from this `Dataset`.

        Parameters:
            *zones (`Zones <data_access>` or index `integers <int>`): Zones to
                remove from this dataset.

        .. code-block:: python
            :emphasize-lines: 3

            >>> print([z.name for z in dataset.zones()])
            ['Zone 1', 'Zone 2']
            >>> dataset.delete_zones(dataset.zone('Zone 2'))
            >>> print([z.name for z in dataset.zones()])
            ['Zone 1']

        Notes:
            Multiple `Zones <data_access>` can be deleted at once, though the
            at least one `Zone <data_access>` must remain. This command deletes
            all but the first `Zone <data_access>` in the `Dataset`::

                >>> dataset.delete_zones(dataset.zones())
        """
        zones = flatten_args(*zones)
        with self.frame.activated():
            with IndexSet(*zones) as zlist:
                _tecutil.DataSetDeleteZone(zlist)

    @property
    def num_solution_times(self):
        """Number of solution times for all zones in the dataset.

        :type: `int` (read-only)

        Example usage::

            >>> print(dataset.num_solution_times)
            10

        .. versionadded:: 2017.3
            Solution time manipulation requires Tecplot 360 2017 R3 or later.
        """
        if __debug__:
            sdk_required = (2017, 3)
            if version.sdk_version_info < sdk_required:
                msg = 'Solution time manipulation requires 2017 R3 or later.'
                raise TecplotOutOfDateEngineError(sdk_required, msg)
        res = _tecutil.SolutionTimeGetNumTimeStepsByDataSetID(self.uid)
        success, value = res
        if not success:
            raise TecplotSystemError()
        return value

    @property
    def solution_times(self):
        """`List <list>` of solution times for all zones in the dataset.

        :type: `list` of `floats <float>` (read-only)

        Example usage::

            >>> print(dataset.solution_times)
            [0.0, 1.0, 2.0, 3.0, 4.0, 5.0, 6.0, 7.0, 8.0, 9.0]

        .. versionadded:: 2017.3
            Solution time manipulation requires Tecplot 360 2017 R3 or later.
        """
        if __debug__:
            sdk_required = (2017, 3)
            if version.sdk_version_info < sdk_required:
                msg = 'Solution time manipulation requires 2017 R3 or later.'
                raise TecplotOutOfDateEngineError(sdk_required, msg)
        res = _tecutil.SolutionTimeGetSolutionTimesByDataSetID(self.uid)
        success, ntimes, times = res
        if not success:
            raise TecplotSystemError()
        ret = list(times[:ntimes])
        if not _tecutil_connector.connected:
            _tecutil.ArrayDealloc(times)
        return ret

    @lock()
    def branch_variables(self, zones, variables, copy_data=True):
        """Breaks data sharing between zones.

        Parameters:
            zones (`list` of `Zones <data_access>`): Zones to be branched.
            variables (`list` of `Variables <Variable>`): Variables to be
                branched.
            copy_data (`bool`, optional): Allocate space for the branched
                values and copy the data. If `False`, the new variables will
                be passive. (default: `True`)

        .. seealso:: `Dataset.share_variables()`

        Example usage::

            >>> z = dataset.zone('My Zone')
            >>> zcopy = z.copy(share_variables=True)
            >>> print([zn.index for zn in z.values(0).shared_zones])
            [0,1]
            >>> dataset.branch_variables(zcopy,dataset.variable(0))
            >>> print([zn.index for zn in z.values(0).shared_zones])
            []
            >>> print([zn.index for zn in z.values(1).shared_zones])
            [0,1]
        """
        if __debug__:
            sdk_required = (2017, 2)
            if version.sdk_version_info < sdk_required:
                msg = 'branching variables not supported.'
                raise TecplotOutOfDateEngineError(sdk_required, msg)
        if not isinstance(zones, Iterable):
            zones = [zones]
        if not isinstance(variables, Iterable):
            variables = [variables]

        for var in variables:
            try:
                varidx = getattr(var, 'index')
            except:
                varidx = self.variable(var).index
            for zone in zones:
                try:
                    zoneidx = getattr(zone, 'index')
                except:
                    zoneidx = self.zone(zone).index
                if not _tecutil.DataValueBranchShared(zoneidx + 1, varidx + 1,
                                                      copy_data):
                    raise TecplotSystemError()

    @lock()
    def share_variables(self, source_zone, destination_zones, variables):
        """Share field data between zones.

        This method links the underlying data `arrays <Array>` of the
        destination `zones <data_access>` to the data of the source `zone
        <data_access>`. Modifying the array data of one zone will affect all
        others in this group.

        Parameters:
            source_zone (`Zone <data_access>`): Zone which provides data to be
                shared.
            destination_zones (`list` of `Zones <data_access>`): Zones
                where data will be overwritten.
            variables (`list` of `Variables <Variable>`): Variables to be
                branched.

        .. seealso:: `Dataset.branch_variables()`

        Example usage::

            >>> z = dataset.zone('My Zone')
            >>> zcopy = z.copy(share_variables=False)
            >>> print([zn.index for zn in z.values(0).shared_zones])
            []
            >>> dataset.share_variables(zcopy,[z],[dataset.variable(0)])
            >>> print([zn.index for zn in z.values(0).shared_zones])
            [0,1]
            >>> print([zn.index for zn in z.values(1).shared_zones])
            []
        """
        if not isinstance(destination_zones, Iterable):
            destination_zones = [destination_zones]
        if not isinstance(variables, Iterable):
            variables = [variables]

        for var in variables:
            try:
                varidx = getattr(var, 'index')
            except:
                varidx = self.variable(var).index
            for zone in destination_zones:
                try:
                    zoneidx = getattr(zone, 'index')
                except:
                    zoneidx = self.zone(zone).index
                try:
                    source_zoneidx = getattr(source_zone, 'index')
                except:
                    source_zoneidx = self.zone(source_zone).index

                if not _tecutil.DataValueIsSharingOk(source_zoneidx+1, zoneidx+1, varidx+1):
                    raise TecplotSystemError()
                _tecutil.DataValueShare(source_zoneidx+1, zoneidx+1, varidx+1)


    @lock()
    def branch_connectivity(self, zones):
        """Breaks connectivity sharing between zones.

        Parameters:
            zones (`list` of `Zones <data_access>`): Zones to be branched.

        .. seealso:: `Dataset.share_connectivity()`

        Example usage::

            >>> z = dataset.zone('My Zone')
            >>> zcopy = z.copy()
            >>> print([zn.index for zn in z.shared_connectivity])
            [0,1]
            >>> dataset.branch_connectivity(zcopy)
            >>> print([zn.index for zn in z.shared_connectivity])
            []
        """
        if not isinstance(zones, Iterable):
            zones = [zones]

        for zone in zones:

            try:
                zoneidx = getattr(zone, 'index')
            except:
                zoneidx = self.zone(zone).index
            if not _tecutil.DataConnectBranchShared(zoneidx + 1):
                raise TecplotSystemError()

    @lock()
    def share_connectivity(self, source_zone, destination_zones):
        """Share connectivity between zones.

        This method links the connectivity (`nodemap` or `facemap`) of the
        destination `zones <data_access>` to the connectivity of the source
        zone. Modifying the connectivity of one zone will affect all others in
        this group.

        Parameters:
            source_zone (`Zone <data_access>`): Zone which provides data to be
                shared.
            destination_zones (`list` of `Zones <data_access>`): Zones where
                connectivity list will be overwritten.

        .. seealso:: `Dataset.branch_connectivity()`

        Example usage::

            >>> z = dataset.zone('My Zone')
            >>> zcopy = z.copy()
            >>> print([zn.index for zn in z.shared_connectivity])
            [0,1]
            >>> dataset.branch_connectivity(zcopy)
            >>> print([zn.index for zn in z.shared_connectivity])
            []
            >>> dataset.share_connectivity(z,zcopy)
            >>> print([zn.index for zn in z.shared_connectivity])
            [0,1]
        """
        if not isinstance(destination_zones, Iterable):
            destination_zones = [destination_zones]

        def _index(obj):
            i = getattr(obj, 'index', None)
            if i is None:
                i = self.zone(obj).index
            return i

        for zone in destination_zones:
            idst = _index(zone)
            isrc = _index(source_zone)
            if not _tecutil.DataConnectIsSharingOk(isrc + 1, idst + 1):
                raise TecplotSystemError()
            _tecutil.DataConnectShare(isrc + 1, idst + 1)


@property
@lock()
def dataset(frame):
    """`Dataset` attached to this `Frame`.

    Returns:
        `Dataset`: The object holding onto the data associated with this
        `Frame`.

    If no `Dataset` has been created for this `Frame`, a new one is created
    and returned::

        >>> dataset = frame.dataset
    """
    if version.sdk_version_info < (2017, 3):
        log.info(MESSAGES.PERFORMANCE_IMPROVEMENTS)
        with frame.activated():
            if not frame.has_dataset:
                frame.create_dataset(frame.name + ' Dataset')
            return Dataset(_tecutil.DataSetGetUniqueID(), frame)
    else:
        if not frame.has_dataset:
            frame.create_dataset(frame.name + ' Dataset')
        dataset_uid = _tecutil.FrameGetDataSetUniqueIDByFrameID(frame.uid)
        return Dataset(dataset_uid, frame)


@property
def has_dataset(frame):
    """Checks to see if the `Frame` as an attached `Dataset`

    :type: `boolean <bool>`

    Example usage::

        >>> if not frame.has_dataset:
        ...     dataset = frame.create_dataset('Dataset', ['x','y','z','p'])
    """
    return _tecutil.DataSetIsAvailableForFrame(frame.uid)

layout.Frame.dataset = dataset
layout.Frame.has_dataset = has_dataset
