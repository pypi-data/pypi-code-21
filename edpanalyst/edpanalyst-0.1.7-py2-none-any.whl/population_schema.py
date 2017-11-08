from collections import OrderedDict
from typing import Any, Dict, Iterator, List, Tuple  # NOQA
import numbers
import pprint
import six

import numpy as np  # type: ignore

# TODO(asilvers): I don't like re-defining these here.
STAT_TYPES = [
    'categorical', 'realAdditive', 'realMultiplicative', 'proportion',
    'magnitude', 'sequence', 'void'
]


class ValueDefinition(object):

    def __init__(self, value, display_value=None,
                 description=None):  # type: (str, str, str) -> None
        self.value = value
        self.display_value = display_value
        self.description = description

    def __repr__(self):
        return pprint.pformat(self.to_json())

    def to_json(self):
        d = {'value': self.value}
        if self.display_value:
            d['display_value'] = self.display_value
        if self.description:
            d['description'] = self.description
        return d


class ColumnDefinition(object):

    def __init__(
            self,
            name,  # type: str
            stat_type,  # type: str
            stat_type_reason=None,  # type: str
            values=None,  # type: List[str]
            length=None,  # type: int
            transform=None,  # type: str
            precision=None,  # type: Tuple[int, int]
            description=None,  # type: str
            display_name=None,  # type: str
            display_values=None,  # type: Dict[str, str]
            value_descriptions=None,  # type: Dict[str, str]
            value_script=None,  # type: str
            dependencies=None,  # type: List[str]
    ):  # type: (...) -> None
        self.name = name
        self.description = description
        self.display_name = display_name
        self.set_stat_type(stat_type, stat_type_reason=stat_type_reason,
                           values=values, length=length, transform=transform,
                           precision=precision, display_values=display_values,
                           value_descriptions=value_descriptions)
        self.value_script = value_script
        self.dependencies = dependencies or []

    @property
    def stat_type(self):
        return self._stat_type

    @property
    def values(self):
        if self._values is None:
            return None
        else:
            return list(self._values.values())

    @property
    def length(self):
        if self._stat_type == 'sequence':
            return self._length
        else:
            raise AttributeError('length only defined on sequences')

    @property
    def transform(self):
        if self._stat_type == 'sequence':
            return self._transform
        else:
            raise AttributeError('transform only defined on sequences')

    @property
    def precision(self):  # type: () -> Tuple[int, int]
        if self.is_real():
            return self._precision
        else:
            raise AttributeError('precision only defined on reals')

    def is_real(self):  # type: () -> bool
        return self._stat_type in ('realAdditive', 'realMultiplicative',
                                   'proportion', 'magnitude')

    def set_display_values(self,
                           display_values):  # type: (Dict[str, str]) -> None
        for v, dv in display_values.items():
            self._values[v].display_value = dv

    @staticmethod
    def _validate_precision(prec):  # type: (Any) -> Tuple[int, int]
        """Validates `prec` as a precision and returns an immutable copy."""
        try:
            if len(prec) != 2:
                raise ValueError('%r does not have length 2' % (prec,))
        except TypeError:
            raise ValueError('%r does not have length 2' % (prec,))
        n, d = prec
        if int(n) != n or int(d) != d or n < 1 or d < 1:
            raise ValueError('invalid precision: %r' % (prec,))
        if n != 1 and d != 1:
            raise ValueError('at least one element of %r must be 1' % (prec,))
        return (n, d)

    def set_stat_type(self, stat_type, stat_type_reason=None, values=None,
                      display_values=None, value_descriptions=None,
                      length=None, transform=None, precision=None):
        if stat_type not in STAT_TYPES:
            raise ValueError('%r is not a valid stat type' % (stat_type,))
        # TODO(asilvers): We could maybe be nice and, if your values are the
        # same, keep the display_values around.
        self._stat_type = stat_type
        self._stat_type_reason = stat_type_reason
        display_values = display_values or {}
        value_descriptions = value_descriptions or {}
        if stat_type == 'categorical':
            if values is None:
                raise ValueError(
                    '`values` must be provided for categorical columns')
            self._values = OrderedDict([(val, ValueDefinition(
                val, display_values.get(val), value_descriptions.get(val)))
                                        for val in values])
        else:
            # Clear the values if we're not categorical
            self._values = None
        if stat_type == 'sequence':
            if (not isinstance(length, numbers.Real) or
                    np.round(length) != length or length < 1):
                raise ValueError(
                    '%r is not a valid length; it must be a positive integer' %
                    (length,))
            self._length = length
            self._transform = transform or 'identity'
            if self._transform not in ('identity', 'log'):
                raise ValueError('%r is not a valid transform' % (transform,))
        else:
            if transform:
                raise ValueError('`transform` is only valid for sequences.')
            if length:
                raise ValueError('`length` is only valid for sequences.')

        if precision:
            if self.is_real():
                self._precision = self._validate_precision(precision)
            else:
                raise ValueError('`precision` is only valid for reals.')
        else:
            self._precision = None

    def __repr__(self):
        return pprint.pformat(self.to_json())

    def __eq__(self, other):  # type: (Any) -> bool
        if isinstance(other, ColumnDefinition):
            return self.to_json() == other.to_json()
        else:
            return NotImplemented

    def to_json(self, drop_reasons=False):
        col_def = {}
        col_def['name'] = self.name
        if self.display_name:
            col_def['display_name'] = self.display_name
        if self.description:
            col_def['description'] = self.description
        col_def['stat_type'] = self._stat_type
        if not drop_reasons and self._stat_type_reason:
            col_def['stat_type_reason'] = self._stat_type_reason
        if self._values:
            col_def['values'] = [
                val.to_json() for val in self._values.values()
            ]
        if self._stat_type == 'sequence':
            col_def['length'] = self.length
            col_def['transform'] = self.transform
        if self.is_real() and self.precision is not None:
            col_def['precision'] = [self.precision[0], self.precision[1]]
        if self.value_script:
            col_def['value_script'] = self.value_script
        if self.dependencies:
            col_def['dependencies'] = self.dependencies
        return col_def


# TODO(asilvers): This thing needs better testing. It's currently only tested
# indirectly in session_test.py.
class PopulationSchema(object):
    """Represents a schema for a population.

    The set of columns is immutable. The API is super rough and subject to
    change.
    """

    def __init__(
            self,
            columns,  # type: Dict[str, ColumnDefinition]
            order=None,  # type: List[str]
            derived_columns=None,  # type: Dict[str, ColumnDefinition]
            derived_order=None,  # type: List[str]
    ):  # type: (...) -> None
        """Create a schema from a dict of ColumnDefinitions.

        The order may be specified by passing `order`, which must contain
        exactly the keys in `columns`. If unspecified, the order of the columns
        is the same as the iteration order in `columns`, so passing an
        OrderedDict does the right thing.
        """
        self._identifying_columns = []  # type: List[str]
        order = order if order is not None else list(columns)
        self._columns = OrderedDict((k, columns[k]) for k in order)
        derived_columns = derived_columns or {}
        derived_order = (derived_order if derived_order is not None else
                         list(derived_columns))
        self._derived_columns = OrderedDict((k, derived_columns[k])
                                            for k in derived_order)

    def __getitem__(self, key):
        if key in self._columns:
            return self._columns[key]
        elif key in self._derived_columns:
            return self._derived_columns[key]
        else:
            raise KeyError('Unknown column: ' + key)

    def __delitem__(self, key):
        if key in self._columns:
            del self._columns[key]
        elif key in self._derived_columns:
            del self._derived_columns[key]
        else:
            raise KeyError('Unknown column: ' + key)

    def __iter__(self):  # type: () -> Iterator[ColumnDefinition]
        return iter(six.viewvalues(self._columns))

    def columns(self):  # type: () -> List[str]
        return list(self._columns.keys())

    def derived_columns(self):  # type: () -> List[str]
        return list(self._derived_columns.keys())

    @property
    def identifying_columns(self):  # type: () -> List[str]
        # Make a copy so callers can't modify our state.
        return list(self._identifying_columns)

    def set_identifying_columns(self, columns):  # type: (List[str]) -> None
        if isinstance(columns, six.string_types):
            raise ValueError(
                '`columns` takes a list of columns, not a single column')
        bad_cols = set(columns).difference(self._columns)
        if bad_cols:
            raise ValueError('%r are not columns' % (bad_cols,))
        self._identifying_columns = columns

    def __repr__(self):
        # pprint returns something a little more compact than json.dumps can
        # be made to produce.
        return pprint.pformat(self.to_json())

    def __eq__(self, other):  # type: (Any) -> bool
        if isinstance(other, PopulationSchema):
            return self.to_json() == other.to_json()
        else:
            return NotImplemented

    def to_json(self, drop_reasons=False):  # type: (bool) -> Dict[str, Any]
        columns = [col.to_json(drop_reasons) for col in self._columns.values()]
        derived_columns = [
            col.to_json(drop_reasons)
            for col in self._derived_columns.values()
        ]
        resp = {'columns': columns, 'derived_columns': derived_columns}
        if self._identifying_columns:
            resp['identifying_columns'] = self._identifying_columns
        return resp

    @staticmethod
    def from_json(json_schema):
        derived_cols = json_schema.get('derived_columns', [])
        schema = PopulationSchema(
            columns=make_column_dict(json_schema['columns']),
            derived_columns=make_column_dict(derived_cols))
        if 'identifying_columns' in json_schema:
            schema.set_identifying_columns(json_schema['identifying_columns'])
        return schema


def make_column_dict(columns):
    col_dict = OrderedDict()  # type: Dict[str, ColumnDefinition]
    for col in columns:
        name = col['name']
        values = None
        display_values = None
        value_descriptions = None
        if 'values' in col:
            values = []
            display_values = {}
            value_descriptions = {}
            for v in col['values']:
                values.append(v['value'])
                if 'display_value' in v:
                    display_values[v['value']] = v['display_value']
                if 'description' in v:
                    value_descriptions[v['value']] = v['description']
        col_def = ColumnDefinition(
            name=name, stat_type=col['stat_type'],
            stat_type_reason=col.get('stat_type_reason'), values=values,
            length=col.get('length'), transform=col.get('transform'),
            precision=col.get('precision'), description=col.get('description'),
            display_name=col.get('display_name'),
            display_values=display_values,
            value_descriptions=value_descriptions,
            value_script=col.get('value_script'),
            dependencies=col.get('dependencies'))
        col_dict[name] = col_def
    return col_dict
