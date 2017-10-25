from typing import Any
from copy import deepcopy
import re


class Expectations(object):
    """
    Fluent interface for defining response expectations. Usage:

    checks = Expectations()
    checks.expect('status').to.be_equal_to(200)
    checks.expect('body').to.include('hello world')
    """
    def __init__(self):
        self._expectations = []

    @classmethod
    def _unmarshall(cls, marshalled):
        ret = Expectations()
        ret._expectations = [Matcher._from_dict(d) for d in marshalled]
        return ret

    def clone(self) -> 'Expectations':
        """Returns a copy of this object"""
        new_expec = Expectations()
        new_expec._expectations = deepcopy(self._expectations)
        return new_expec

    def extend(self, expectations: 'Expectations') -> None:
        """
        Extends the expectations defined in this instance with all the expectations defined in the passed argument
        """
        self._expectations.extend(deepcopy(expectations._expectations))

    def expect(self, field: str) -> 'Matcher':
        """
        Instantiates a Matcher for the given response field.
        """
        f = Matcher(field)
        self._expectations.append(f)
        return f

    def _marshall(self):
        return [exp._dict for exp in self._expectations]

    def __str__(self):
        return "\n".join(str(matcher) for matcher in self._expectations)

    def _verify(self, actual):
        success = True
        errors = []
        for matcher in self._expectations:
            actual_value = actual.get(matcher._field)
            result = getattr(Verifier, matcher._operation)(actual_value, *matcher._args)
            if matcher._not:
                result = not result
            if not result:
                success = False
                e = "%s (actual: %s)" % (matcher, actual_value)
                errors.append(e)
        return success, errors


class Verifier(object):
    range_spec = re.compile(r'^\d+(-\d+)?(,\d+(-\d+)?)*$')

    @classmethod
    def match(cls, actual, pattern):
        return re.search(pattern, actual) is not None

    @classmethod
    def be_in_range(cls, actual, from_value, to_value):
        return from_value <= actual <= to_value

    @classmethod
    def be_equal_to(cls, actual, expected):
        return actual == expected

    @classmethod
    def include(cls, actual, *needles):
        return all(needle in actual for needle in needles)

    @classmethod
    def be_in(cls, actual, *the_whole):
        return actual in the_whole

    @classmethod
    def be_in_ranges(cls, actual, range_spec):
        spec = range_spec.replace(' ', '')
        if not cls.range_spec.search(spec):
            raise ValueError("Invalid int ranges spec '%s': Use e.g. 1-5,8,11-13"
                             % range_spec)
        for item in spec.split(','):
            parts = [int(part) for part in item.split('-')]
            if len(parts) == 1:
                start = end = parts[0]
            else:
                start, end = parts
            if start > end:
                raise ValueError("Invalid int ranges spec '%s': Unsorted pair %d-%d"
                                 % (range_spec, start, end))
            if actual in range(start, end + 1):
                return True
        return False


class Matcher(object):
    def __init__(self, field, operation=None, args=None, negative=False):
        self._field = field
        self._operation = operation
        self._args = args
        self._not = negative
        self._single_arg = False

    @classmethod
    def _from_dict(cls, d):
        return Matcher(d['field'], d['op'], d['args'], d.get('not', False))

    @property
    def to(self) -> 'Matcher':
        """No operation, just to improve readability when fluently defining expectations"""
        return self

    @property
    def not_to(self) -> 'Matcher':
        """Inverts the matching result. E.g. `not_to.include('this')`"""
        self._not = True
        return self

    def match(self, value: str) -> None:
        """Expects the result to be successful if the target matches the given regex"""
        self._operation = 'match'
        self._args = [value]

    def be_in_range(self, from_value: Any, to_value: Any) -> None:
        """Expects the result to be successful if the from_value <= target <= to_value"""
        self._operation = 'be_in_range'
        self._args = [from_value, to_value]

    def be_in_ranges(self, range_spec: str) -> None:
        """Expects the result to be successful if the numeric target matches the given range specification.
        The specification is a list of numbers or intervals. E.g: `1,2,5-10,56,70-90`"""
        Verifier.be_in_ranges(None, range_spec)
        self._operation = 'be_in_ranges'
        self._args = [range_spec]

    def be_in(self, *the_whole: Any) -> None:
        """Expects the result to be successful if the target is included in the given list of arguments"""
        self._operation = 'be_in'
        self._args = list(the_whole)

    def be_equal_to(self, value: Any) -> None:
        """Expects the result to be successful if the target is equal to the given argument"""
        self._operation = 'be_equal_to'
        self._args = [value]

    def include(self, *values: Any):
        """Expects the result to be successful if the target includes all the given argument"""
        self._operation = 'include'
        self._args = list(values)

    def __str__(self):
        to_be_or_not_be = 'not to' if self._not else 'to'
        op = self._operation.replace('_', ' ')

        return "Expecting '%s' %s %s %s" % (self._field, to_be_or_not_be, op, self._args)

    def __copy__(self):
        return Matcher(self._field,
                       operation=self._operation,
                       args=self._args,
                       negative=self._not)

    def __deepcopy__(self, memodict={}):
        return Matcher(deepcopy(self._field, memo=memodict),
                       operation=deepcopy(self._operation, memo=memodict),
                       args=deepcopy(self._args, memo=memodict),
                       negative=self._not)

    @property
    def _dict(self):
        ret = {
          'field': self._field,
          'op': self._operation,
          'args': self._args
        }
        if self._not:
            ret['not'] = True
        return ret
