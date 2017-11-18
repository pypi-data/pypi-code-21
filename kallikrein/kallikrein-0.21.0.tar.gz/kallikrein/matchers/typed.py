from typing import TypeVar, Type, Union, Any

from kallikrein.matcher import (Predicate, matcher_f, NestingUnavailable,
                                BoundMatcher, StrictMatcher, ChainMatcher)

from amino import Boolean, List
from amino.tc.base import TypeClass
from amino.dat import qualified_type

A = TypeVar('A')


class Typed:
    pass


class ChainTyped(TypeClass):

    def chain(self, tpe: Type) -> BoundMatcher:
        ...


class ChainMatcherTyped(ChainMatcher, tpe=Typed):

    def chain(self, matcher: StrictMatcher, other: Union[A, BoundMatcher]) -> BoundMatcher:
        return ChainTyped.fatal(matcher.target).chain(matcher, other)


class PredTyped(Predicate):
    pass


class PredTypedAny(PredTyped, pred=lambda a: True):

    def check(self, exp: A, tpe: type) -> Boolean:
        return Boolean(isinstance(exp, tpe))


success = '`{}` is a `{}`'
failure = '`{}` is not a `{}`'


def msg(success: bool, exp: Any, target: type) -> List[str]:
    conj = 'is a' if success else 'is not a'
    desc = qualified_type(target)
    return List(f'`{exp}` {conj} `{desc}`')


typed = matcher_f(Typed, msg, PredTyped, NestingUnavailable)
have_type = typed

__all__ = ('typed', 'have_type')
