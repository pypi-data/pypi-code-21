import abc
from typing import Generic, TypeVar, Union, Callable, Type, cast, Generator

from kallikrein.match_result import (MatchResult, SimpleMatchResult, BadNestedMatch, MatchResultAnd, MatchResultOr,
                                     MatchResultAlg, MatchResultNot)

from amino import Boolean, Maybe, List, __, Eval, Nil
from amino.tc.base import TypeClass
from amino.boolean import false
from amino.do import tdo
from amino.state import EvalState

A = TypeVar('A')
B = TypeVar('B')
C = TypeVar('C')


class MatcherAlg:

    @abc.abstractmethod
    def __and__(self, other: 'MatcherAlg') -> 'MatcherAlg':
        ...

    @abc.abstractmethod
    def __or__(self, other: 'MatcherAlg') -> 'MatcherAlg':
        ...

    @abc.abstractmethod
    def __invert__(self) -> 'MatcherAlg':
        ...


def cons_match_result_and(matchers: 'List[SimpleBoundMatcher[A, B]]', exp: A) -> MatchResult[A]:
    @tdo(EvalState[List[SimpleBoundMatcher[A, B]], List[MatchResult[A]]])
    def loop1(results: List[MatchResult[A]], head: SimpleBoundMatcher[A, B], tail: List[SimpleBoundMatcher[A, B]]
              ) -> EvalState[List[SimpleBoundMatcher[A, B]], List[MatchResult[A]]]:
        yield EvalState.set(tail)
        result = head.evaluate(exp)
        results1 = results.cat(result)
        yield EvalState.pure(results1) if result.failure else loop(results1)
    @tdo(EvalState[List[SimpleBoundMatcher[A, B]], List[MatchResult[A]]])
    def loop(results: List[MatchResult[A]]) -> Generator:
        matchers = yield EvalState.get()
        yield matchers.detach_head.map2(lambda h, t: loop1(results, h, t)) | EvalState.pure(results)
    return MatchResultAnd(loop(Nil).run_a(matchers).evaluate())


def cons_match_result_not(matchers: 'List[SimpleBoundMatcher[A, B]]', exp: A) -> MatchResult[A]:
    return MatchResultNot(matchers.map(__.evaluate(exp)))


def cons_match_result_or(matchers: 'List[SimpleBoundMatcher[A, B]]', exp: A) -> MatchResult[A]:
    return MatchResultOr(matchers.map(__.evaluate(exp)))


class BoundMatcher(Generic[A], MatcherAlg):

    @abc.abstractmethod
    def evaluate(self, exp: A) -> MatchResult[A]:
        ...

    def __and__(self, other: MatcherAlg) -> MatcherAlg:
        return BoundMatcherAlg(List(self, other), cons_match_result_and)

    def __invert__(self) -> MatcherAlg:
        return BoundMatcherAlg(List(self), cons_match_result_not)

    def __or__(self, other: MatcherAlg) -> MatcherAlg:
        return BoundMatcherAlg(List(self, other), cons_match_result_or)


class SimpleBoundMatcher(BoundMatcher[A], Generic[A, B]):

    def __init__(self, matcher: 'Matcher', handler: Callable[[A, B], MatchResult], target: B) -> None:
        self.matcher = matcher
        self.handler = handler
        self.target = target

    def __str__(self) -> str:
        return '{}({}, {})'.format(self.__class__.__name__, self.handler, self.target)

    def evaluate(self, exp: A) -> MatchResult[A]:
        return self.handler(exp, self.target)


class StrictMatcher(SimpleBoundMatcher[A, A], Generic[A]):

    def __call__(self, other: Union[A, BoundMatcher]) -> BoundMatcher:
        return ChainMatcher.fatal(self.matcher.matcher_type).chain(self, other)


class NestedMatcher(SimpleBoundMatcher[A, BoundMatcher], Generic[A]):
    pass


class BoundMatcherAlg(BoundMatcher[A], Generic[A, B]):

    def __init__(
            self,
            sub: List[SimpleBoundMatcher[A, B]],
            result_ctor: Callable[[List[SimpleBoundMatcher[A, B]], A], MatchResultAlg[A]]
    ) -> None:
        self.sub = sub
        self.result_ctor = result_ctor

    def evaluate(self, exp: A) -> MatchResult[A]:
        return self.result_ctor(self.sub, exp)


class ChainMatcher(TypeClass):

    @abc.abstractmethod
    def chain(self, matcher: StrictMatcher, other: Union[A, BoundMatcher]) -> BoundMatcher:
        ...


class Matcher(Generic[A]):

    def __call__(self, target: Union[A, BoundMatcher]) -> SimpleBoundMatcher:
        return (
            cast(SimpleBoundMatcher, NestedMatcher(self, self.match_nested, target))
            if isinstance(target, BoundMatcher) else
            StrictMatcher(self, self.match, target)
        )

    @abc.abstractmethod
    def match(self, exp: A, target: A) -> MatchResult[A]:
        ...

    @abc.abstractmethod
    def match_nested(self, exp: A, target: BoundMatcher) -> MatchResult[A]:
        ...

    @property
    def matcher_type(self) -> Type:
        return type(self)


class Predicate(Generic[A, B], TypeClass):

    @abc.abstractmethod
    def check(exp: A, target: B) -> Boolean:
        ...


class PredicateUnavailable(Generic[A, B], Predicate):

    def check(exp: A, target: B) -> Boolean:
        return false


class Nesting(Generic[A, C], TypeClass):

    @abc.abstractmethod
    def match(self, exp: A, target: BoundMatcher) -> C:
        ...

    @abc.abstractmethod
    def wrap(self, name: str, exp: A, nested: C) -> MatchResult:
        ...


class NestingUnavailable(Nesting):

    def match(self, exp: A, target: BoundMatcher) -> C:
        return BadNestedMatch(target)

    def wrap(self, name: str, exp: A, nested: C) -> MatchResult:
        return BadNestedMatch(nested)


class NestingUnavailableAny(NestingUnavailable, pred=lambda a: True):
    pass


class NoInstance(Exception):

    def __init__(self, pred: type, exp: A) -> None:
        msg = 'no {} defined for {}'.format(pred.__name__, exp)
        super().__init__(msg)


class TCMatcher(Matcher[A]):

    @abc.abstractproperty
    def pred_tc(self) -> Type[Predicate]:
        ...

    @abc.abstractproperty
    def nest_tc(self) -> Type[Nesting]:
        ...

    @abc.abstractmethod
    def format(self, success: bool, exp: A, target: B) -> List[str]:
        ...

    def pred(self, exp: A, target: B) -> Maybe[Predicate]:
        return self.pred_tc.m_for(exp)

    def pred_fatal(self, exp: A, target: B) -> Predicate:
        return (
            self.pred_tc.m_for(exp)
            .get_or_raise(NoInstance(self.pred_tc, exp))
        )

    def check_pred(self, exp: A, target: B) -> Boolean:
        return (
            self.pred_fatal(exp, target)  # type: ignore
            .check(exp, target)
        )

    def nest(self, exp: A) -> Nesting:
        return (
            self.nest_tc.m(type(exp)) | NestingUnavailable
        )

    def match(self, exp: A, target: B) -> MatchResult[A]:
        success = self.check_pred(exp, target)
        message = self.format(success, exp, target)
        return SimpleMatchResult(success, message)

    def match_nested(self, exp: A, target: BoundMatcher) -> MatchResult[A]:
        nest = self.nest(exp)
        nested = nest.match(exp, target)
        return nest.wrap(self.matcher_type.__name__, exp, nested)


class SimpleTCMatcherBase(TCMatcher):

    def __init__(self, tpe: Type, pred_tc: Type[Predicate], nest_tc: Type[Nesting]) -> None:
        self.tpe = tpe
        self._pred_tc = pred_tc
        self._nest_tc = nest_tc

    @property
    def pred_tc(self) -> Type[Predicate]:
        return self._pred_tc

    @property
    def nest_tc(self) -> Type[Nesting]:
        return self._nest_tc

    @property
    def matcher_type(self) -> Type:
        return self.tpe


class SimpleTCMatcher(SimpleTCMatcherBase):

    def __init__(self, tpe: Type, success_tmpl: str, failure_tmpl: str, pred_tc: Type[Predicate], nest_tc: Type[Nesting]
                 ) -> None:
        super().__init__(tpe, pred_tc, nest_tc)
        self.success_tmpl = success_tmpl
        self.failure_tmpl = failure_tmpl

    def format(self, success: bool, exp: A, target: B) -> List[str]:
        tmpl = self.success_tmpl if success else self.failure_tmpl
        return List(tmpl.format(exp, target))


class CallbackTCMatcher(SimpleTCMatcherBase):

    def __init__(self, tpe: Type, format_cb: Callable[[bool, A, B], List[str]], pred_tc: Type[Predicate],
                 nest_tc: Type[Nesting]) -> None:
        super().__init__(tpe, pred_tc, nest_tc)
        self.format_cb = format_cb

    def format(self, success: bool, exp: A, target: B) -> List[str]:
        return self.format_cb(success, exp, target)

matcher = SimpleTCMatcher
matcher_f = CallbackTCMatcher

__all__ = ('Matcher', 'BoundMatcher', 'Predicate', 'Nesting', 'NoInstance', 'TCMatcher', 'SimpleTCMatcher',
           'BoundMatcher', 'SimpleTCMatcherBase', 'matcher_f')
