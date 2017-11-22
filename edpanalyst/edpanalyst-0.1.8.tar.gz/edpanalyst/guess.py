from typing import Any, Dict, Iterable, Iterator, List, Optional, Tuple  # NOQA
import numbers
import six

import numpy as np  # type: ignore
import pandas as pd  # type: ignore # NOQA

from .population_schema import PopulationSchema, ColumnDefinition

# How small a number of values guarantees categorical
_CATEGORICAL_THRESHOLD = 20

# How many values should cover what fraction of the space to accept
# categorical?
_CATEGORICAL_COVERAGE_COUNT = 10
_CATEGORICAL_COVERAGE_RATIO = 0.6


def guess_schema(df):  # type: (pd.DataFrame) -> PopulationSchema
    """Guesses a schema for a data frame."""
    coldefs = {col: _guess_given_vals(col, df[col]) for col in df.columns}
    return PopulationSchema(coldefs, order=df.columns)


def _guess_given_vals(col_name, data):
    # type: (str, pd.Series) -> ColumnDefinition
    """Returns a guess as to the definition of a column given its data.

    These heuristics are utterly unprincipled and simply seem to work well on a
    minimal set of test datasets. They should be improved as failures crop up.
    """
    if all(x is None or _is_like_list_of_numbers(x) for x in data):
        return _most_likely_sequence_def(col_name, data)
    try:
        unique_vals = data.dropna().unique()
    except TypeError:
        # If the values are non-hashable, and we didn't detect it as a
        # sequence, give up.
        return ColumnDefinition(
            col_name, 'void',
            'Column is neither sequences of numbers nor scalars')

    # Constant columns are uninteresting.  Do not model them.
    cardinality = len(unique_vals)
    if cardinality == 0:
        return ColumnDefinition(col_name, 'void', 'Column is empty')
    elif cardinality == 1:
        return ColumnDefinition(col_name, 'void', 'Column is constant')

    # Use categorical for anything with less than 20 values, even numbers.
    if cardinality < 20:
        return ColumnDefinition(col_name, 'categorical',
                                'Only %d distinct values' % cardinality,
                                values=_infer_categorical_values(data))

    non_num_vals = [v for v in unique_vals if not _numbery(v)]
    if len(non_num_vals) == 0:
        # We have to do math. Turn them into the numbers they are.
        converted_vals = np.array([float(v) for v in unique_vals])
        stat_type, transform_reason = _guess_real_stat_type_and_reason(
            converted_vals)
        precision = _guess_precision(converted_vals)
        return ColumnDefinition(
            col_name, stat_type, 'Contains only numbers (%d of them, %s)' %
            (cardinality, transform_reason), precision=precision)

    if cardinality == len(data):
        return ColumnDefinition(col_name, 'void',
                                'Non-numeric and all values unique')

    non_null = len(data.dropna())
    counts = data.dropna().value_counts()
    if non_null:
        coverage = (
            counts.iloc[:_CATEGORICAL_COVERAGE_COUNT].sum() * 1.0 / non_null)
    if coverage > _CATEGORICAL_COVERAGE_RATIO:
        reason = ('{} distinct values, {} non-numeric, '
                  'first {} cover {:.2%} of the space').format(
                      cardinality, len(non_num_vals),
                      _CATEGORICAL_COVERAGE_COUNT, coverage)
        return ColumnDefinition(col_name, 'categorical', reason,
                                values=_infer_categorical_values(data))

    # Ignore anything with more than 20 distinct non-numeric values
    # and poor coverage.
    nonnum_str = ", ".join(non_num_vals[:3])
    if len(non_num_vals) > 3:
        nonnum_str += ", ..."
    return ColumnDefinition(col_name, 'void',
                            '%d distinct values. %d are non-numeric (%s)' %
                            (cardinality, len(non_num_vals), nonnum_str))


def make_column_from_hint(col_name, data, hint):
    # type: (str, pd.Series, Dict[str, str]) -> ColumnDefinition
    if 'stat_type' not in hint:
        raise ValueError('hint %s for column %s does not contain stat_type' %
                         (hint, col_name))

    if hint['stat_type'] == 'void':
        return ColumnDefinition(col_name, 'void', 'Hinted')

    elif hint['stat_type'] == 'categorical':
        return ColumnDefinition(col_name, 'categorical', 'Hinted',
                                values=_infer_categorical_values(data))

    elif hint['stat_type'] in ('real', 'realAdditive', 'realMultiplicative'):
        try:
            data = data.astype(float)
        except ValueError:
            # Provide a more explicit error message
            raise ValueError('Numeric hint %s for column %s, but column '
                             'contains non-numeric values' % (hint, col_name))

        if hint['stat_type'] == 'realMultiplicative' and (data <= 0).any():
            raise ValueError('Hinted realMultiplicative, but column contains '
                             'non-positive values: %s' % hint)

        if hint['stat_type'] == 'real':
            stat_type, _ = _guess_real_stat_type_and_reason(data)
        else:
            stat_type = hint['stat_type']

        return ColumnDefinition(col_name, stat_type, 'Hinted',
                                precision=_guess_precision(data))
    else:
        # Notably, we can't hint a sequence stat_type.
        raise ValueError('invalid stat_type hint %s for column %s' %
                         (hint, col_name))


def _infer_categorical_values(data):  # type: (np.ndarray) -> List[str]
    # TODO(asilvers): Categoricals have to be strings, but auto-converting
    # still allows ambiguity in representations of floats. This probably
    # doesn't get solved until guess is done on the server.
    str_vals = data.dropna().unique().astype(six.text_type)
    # TODO(asilvers): What order do we want to use here? Lexicographic?
    # Descending frequency? This is also the order that gets used in UIs
    # (should that stay true?) so getting it right-ish for humans is also
    # important. Currently this is just lexicographic except with a silly hack
    # to sort numbers numerically and put them first.
    # Why zfill(10)? asilvers made up the 10. He figures if your numbers are
    # longer than that then are you really worried about if they're sorted?
    return sorted(str_vals, key=lambda v: v.zfill(10) if _numbery(v) else v)


def _guess_real_stat_type_and_reason(vals):
    # type: (np.ndarray) -> Tuple[str, str]
    """Guesses either realAdditive or realMultiplicative for `vals`."""
    x = np.sort(vals[~np.isnan(vals)])
    if any(np.less_equal(x, 0)):
        return 'realAdditive', 'not all values are positive'
    # Compute the correlation of the column's values and their logs with
    # uniform quantiles.
    q = np.linspace(1, len(x), num=len(x)) / (len(x) + 1)
    q_cor = np.corrcoef(q, x)[0, 1]
    lq_cor = np.corrcoef(q, np.log(x))[0, 1]
    if np.isnan(q_cor) or np.isnan(lq_cor):
        # Should never happen, since we're guaranteed two distinct values.
        raise ValueError('could not infer type for %r' % (vals,))
    # If both uniform and log-uniform quantiles match the distribution of the
    # values well, return realAdditive. Otherwise, pick realMultiplicative if
    # log-uniform quantiles match better, and realAdditive if uniform quantiles
    # match better.
    reason = 'uniform cor. %.3f, log-uniform cor. %.3f' % (q_cor, lq_cor)
    if lq_cor > q_cor and q_cor < 0.95:
        return 'realMultiplicative', reason
    else:
        return 'realAdditive', reason


def _guess_precision(vals):  # type: (np.ndarray) -> Tuple[int, int]
    """Returns a (n, d) tuple such that `vals` are measured to only n/d.

    For example, if all values are multiples of 1000, returns (1000, 1).
    Returns None if it looks like `vals` use all of the bits available.
    Currently only guesses decimal precision.
    """
    abs_max = np.max(np.abs(vals))
    # Try units of 1,000,000 down to 0.000001, counting down so that we take
    # the coarsest one possible.
    for places in range(-6, 7):
        # If places is 2, `max_normalized_err` is 0.7 on `vals` of
        # [0.01, 0.027, 0.04].
        z = vals * 10**places
        max_normalized_err = np.max(np.abs(np.round(z) - z))
        # If we have at least six places of accuracy, we've found a precision.
        # Except, check `abs_max` so we don't accept either 1e-30 as being even
        # units of 1e-6 since it rounds to zero with 30 places of accuracy, and
        # we don't accept 1e+30 even though it's an exact multiple of 1e+6.
        if (max_normalized_err < 1e-6 and
                10**(-places) <= abs_max < 10**(9 - places)):
            if places < 0:
                return (10**-places, 1)
            else:
                return (1, 10**places)
    return None


def _first_present(seq):  # type: (np.ndarray) -> float
    """Returns the first non-None element of `seq`.

    If all the elements of `seq` are None, or if it has length zero, returns
    None.
    """
    return next((x for x in seq if x is not None), None)


def _most_likely_sequence_def(col_name, vals):
    # type: (str, np.ndarray) -> ColumnDefinition
    """Return a sequence ColumnDefinition for an array of lists and Nones.

    Returns a void ColumnDefinition if a sequence type can't be inferred.
    """
    if all(x is None for x in vals):
        return ColumnDefinition(col_name, 'void', 'All values are missing.')
    length = max(len(x) for x in vals if x is not None)
    if length == 0:
        return ColumnDefinition(col_name, 'void', 'All sequences are empty.')
    # the elements of the non-missing sequences of `vals`
    elements = _flatten_iterable_of_iterable(
        seq for seq in vals if seq is not None)
    # an array with every non-missing number in any sequence in `vals`
    nums = np.fromiter((e for e in elements if e is not None), np.float64)
    if len(nums) == 0:
        return ColumnDefinition(col_name, 'void',
                                'No sequence has any numbers.')
    if len(set(nums)) < 2:
        return ColumnDefinition(
            col_name, 'void',
            'Fewer than two distinct values in all sequences.')
    first_elements = set(
        _first_present(seq) for seq in vals if seq is not None)
    first_elements.discard(None)
    if len(set(first_elements)) < 2:
        return ColumnDefinition(
            col_name, 'void',
            'A collection of sequences must have at least two distinct '
            'first values to be modeled.')
    scalar_type, scalar_reason = _guess_real_stat_type_and_reason(nums)
    transform = {
        'realAdditive': 'identity',
        'realMultiplicative': 'log',
    }[scalar_type]
    reason = 'All Nones and sequences of numbers (%s) ' % (scalar_reason,)
    return ColumnDefinition(col_name, 'sequence', reason, length=length,
                            transform=transform)


def _numbery(val):
    """Returns True if a value looks like a number."""
    try:
        float(val)
        return True
    except ValueError:
        return False
    except TypeError:
        return False


def _is_like_list_of_numbers(val):
    """Returns whether `val` looks like a list of numbers and Nones."""
    if isinstance(val, bytes):
        return False
    try:
        val[0:0]  # raises TypeError on dicts and IndexError on scalars
        return all(x is None or isinstance(x, numbers.Number) for x in val)
    except IndexError:
        return False
    except TypeError:
        return False


def _flatten_iterable_of_iterable(list_of_lists):
    # type: (Iterable[Iterable[Any]]) -> Iterator[Any]
    return (elem for inner_list in list_of_lists for elem in inner_list)
