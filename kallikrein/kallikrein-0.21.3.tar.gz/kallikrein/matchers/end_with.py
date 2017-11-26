from typing import TypeVar, Sequence
from collections.abc import Sequence as SequenceABC

from amino import Boolean, L, _

from kallikrein.matcher import Predicate, matcher, NestingUnavailable

A = TypeVar('A')
B = TypeVar('B')


class EndWith:
    pass


class PredEndWith(Predicate):
    pass


is_seq = L(issubclass)(_, SequenceABC)


class PredEndWithString(PredEndWith, tpe=str):

    def check(self, exp: str, target: str) -> Boolean:
        return Boolean(exp.endswith(target))


class PredEndWithCollection(PredEndWith, pred=is_seq):

    def check(self, exp: Sequence[A], target: A) -> Boolean:
        return Boolean(exp[-len(target):] == target)


success = '`{}` ends with `{}`'
failure = '`{}` does not end with `{}`'
end_with = matcher(EndWith, success, failure, PredEndWith, NestingUnavailable)

__all__ = ('end_with',)
