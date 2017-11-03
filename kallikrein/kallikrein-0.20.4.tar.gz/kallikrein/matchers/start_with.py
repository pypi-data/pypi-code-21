from typing import TypeVar, Sequence
from collections.abc import Sequence as SequenceABC

from amino import Boolean, L, _

from kallikrein.matcher import Predicate, matcher, NestingUnavailable

A = TypeVar('A')
B = TypeVar('B')


class StartWith:
    pass


class PredStartWith(Predicate):
    pass


is_seq = L(issubclass)(_, SequenceABC)


class PredStartWithString(PredStartWith, tpe=str):

    def check(self, exp: str, target: str) -> Boolean:
        return Boolean(exp.startswith(target))


class PredStartWithCollection(PredStartWith, pred=is_seq):

    def check(self, exp: Sequence[A], target: A) -> Boolean:
        return Boolean(exp[:len(target)] == target)


success = '`{}` starts with `{}`'
failure = '`{}` does not start with `{}`'
start_with = matcher(StartWith, success, failure, PredStartWith, NestingUnavailable)

__all__ = ('start_with',)
