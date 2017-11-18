from typing import TypeVar, Sized, Any

from amino import Boolean, L, _, List

from kallikrein.matcher import Predicate, matcher_f, NestingUnavailable

A = TypeVar('A')
B = TypeVar('B')


class Empty:
    pass


class PredEmpty(Predicate):
    pass


is_sized = L(issubclass)(_, Sized)


class PredEmptyCollection(PredEmpty, pred=is_sized):

    def check(self, exp: Sized, target: bool) -> Boolean:
        return Boolean((len(exp) == 0) == target)


def msg(success: bool, exp: Any, target: bool) -> List[str]:
    pref = 'non' if target ^ success else ''
    return List(f'`{exp}` is {pref}empty')

empty = matcher_f(Empty, msg, PredEmpty, NestingUnavailable)
be_empty = empty(True)
be_nonempty = empty(False)

__all__ = ('empty', 'be_empty', 'be_nonempty')
