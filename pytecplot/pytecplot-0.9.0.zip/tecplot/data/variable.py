from builtins import int

import logging

from six import string_types
from textwrap import dedent

from ..tecutil import _tecutil
from ..constant import *
from ..exception import *
from .. import layout, session
from ..tecutil import Index, lock, lock_attributes
from .array import Array

log = logging.getLogger(__name__)


@lock_attributes
class Variable(object):
    """Key value for a data array within a `Dataset`.

    `Variables <Variable>` can be identified (uniquely) by the index within
    their parent `Dataset` or (non-uniquely) by name. In general, a `Zone
    <data_access>` must also be selected to access the underlying data array.
    This object is used by several style controlling classes such as contours
    and vectors. The following example sets the contour variable for the first
    contour group to the first variable named 'S'::

        >>> plot.contour(0).variable = dataset.variable('S')
    """
    def __init__(self, uid, dataset):
        self.uid = uid
        self.dataset = dataset

    def __str__(self):
        """Brief string representation.

        Returns:
            `string <str>`: Brief representation of this `Variable`, showing
            `Zones <data_access>`.

        Example::

            >>> p = dataset.variable('Pressure')
            >>> print(p)
            Pressure
        """
        return self.name

    def __repr__(self):
        """Executable string representation.

        Returns:
            `string <str>`: Internal representation of this `Variable`.

        The string returned can be executed to generate a
        clone of this `Variable` object::

            >>> x = dataset.variable('x')
            >>> print(repr(x))
            Variable(uid=41, Dataset(uid=21, frame=Frame(uid=11,
            page=Page(uid=1)))
            >>> exec('x_clone = '+repr(x))
            >>> x_clone
            Variable(uid=41, Dataset(uid=21, frame=Frame(uid=11,
            page=Page(uid=1)))
            >>> x == x_clone
            True
        """
        return 'Variable(uid={uid}, dataset={dataset})'.format(
            uid=self.uid, dataset=repr(self.dataset))

    def __eq__(self, other):
        """Checks for equality in the |Tecplot Engine|.

        Returns:
            `bool`: `True` if the unique ID numbers are the same for both
            `Variables <Variable>`.
        """
        return self.uid == other.uid

    def __ne__(self, other):
        return not (self == other)

    @property
    def aux_data(self):
        """Auxiliary data for this variable.

        Returns:
            `AuxData`

        This is the auxiliary data attached to the variable. Such data is
        written to the layout file by default and can be retrieved later.
        Example usage::

            >>> frame = tp.active_frame()
            >>> aux = frame.dataset.variable('X').aux_data
            >>> aux['X_weighted_avg'] = '3.14159'
            >>> print(aux['X_weighted_avg'])
            3.14159
        """
        return session.AuxData(self.dataset.frame, AuxDataObjectType.Variable,
                               self.index)

    @property
    def index(self):
        """Zero-based position within the parent `Dataset`.

        :type: `Index`

        Example usage::

            >>> plot.contour(0).variable_index = dataset.variable('S').index
        """
        return Index(_tecutil.VarGetNumByUniqueID(self.uid) - 1)

    def minmax(self):
        """Limits of the values stored in this variable across all zones.

        :type: 2-tuple of `floats <float>`

        This always returns `floats <float>` regardless of the underlying data
        type::

            >>> print(dataset.variable('x').minmax())
            (0, 10)
        """
        with self.dataset.frame.activated():
            success, vmin, vmax = _tecutil.VarGetMinMax(self.index + 1)
            if not success:
                raise TecplotSystemError()
            return vmin, vmax

    def min(self):
        """Lower bound of the values stored in this variable across all zones.

        :type: `float`

        This always returns a `float` regardless of the underlying data type::

            >>> print(dataset.variable('x').min())
            0
        """
        return self.minmax()[0]

    def max(self):
        """Upper bound of the values stored in this variable across all zones.

        :type: `float`

        This always returns a `float` regardless of the underlying data type::

            >>> print(dataset.variable('x').max())
            10
        """
        return self.minmax()[1]

    @property
    def name(self):
        """Returns or sets the name.

        :type: `string <str>`

        Example usage::

            >>> print(dataset.variable(0).name)
            X
        """
        res, var_name = _tecutil.VarGetNameByDataSetID(self.dataset.uid,
                                                       self.index + 1)
        if not res:
            raise TecplotSystemError()
        return var_name

    @name.setter
    @lock()
    def name(self, name):
        _tecutil.VarRenameByDataSetID(self.dataset.uid, self.index + 1, name)

    @property
    def num_zones(self):
        """Number of `Zones <data_access>` in the parent `Dataset`.

        :type: `integer <int>`

        Example usage, looping over all zones by index::

            >>> for zindex in range(dataset.num_zones):
            ...     zone = dataset.zone(zindex)
        """
        return self.dataset.num_zones

    def values(self, pattern):
        """Returns `Array` by index or string pattern.

        Parameters:
            pattern (`integer <int>` or `string <str>`):  Zero-based index or
                `glob-style pattern <fnmatch.fnmatch>` in which case, the first
                match is returned, or a `Zone <data_access>` object.

        The `Zone.name <OrderedZone.name>` attribute is used to match the
        *pattern* to the desired `Array` though this is not necessarily
        unique::

            >>> ds = frame.dataset
            >>> print(ds)
            Dataset:
              Zones: 'Rectangular zone'
              Variables: 'x', 'y', 'z'
            >>> x = ds.variable('x')
            >>> rectzone = x.values('Rectangular zone')
            >>> rectzone == x.values(0)
            True
        """
        if isinstance(pattern, (string_types, int)):
            zone_id = pattern
        else:
            zone_id = pattern.index
        return Array(self.dataset.zone(zone_id), self)
