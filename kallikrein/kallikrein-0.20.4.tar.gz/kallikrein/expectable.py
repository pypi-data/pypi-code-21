import abc
from typing import Generic, TypeVar, Union, Callable, Any

from kallikrein.match_result import MatchResult, SuccessMatchResult
from kallikrein.matcher import Matcher, BoundMatcher
from kallikrein.expectation import (Expectation, SingleStrictExpectation, SingleCallableExpectation,
                                    SingleExpectationResult)
from kallikrein.matchers import equal
from kallikrein.matchers.any import be_any
from kallikrein.unsafe import UnsafeExpectation
from kallikrein.matchers.comparison import not_equal

A = TypeVar('A')


class ExpectableBase(Generic[A]):

    def __init__(self, value: A) -> None:
        self.value = value

    @abc.abstractmethod
    def match(self, match: BoundMatcher) -> Expectation[A]:
        ...

    def __call__(self, mm: Union[BoundMatcher, Matcher[A]]) -> Expectation[A]:
        match = mm if isinstance(mm, BoundMatcher) else mm(be_any)
        return self.match(match)

    must = __call__
    should = __call__

    def safe_match(self, matcher: BoundMatcher) -> Expectation[A]:
        return self.default_expectation(matcher)

    # FIXME UnsafeExpectation has no ctor
    def unsafe_match(self, matcher: BoundMatcher) -> Expectation[A]:
        expectation = self.safe_match(matcher)
        expectation.fatal_eval()
        return UnsafeExpectation(matcher, self.value)

    def default_expectation(self, matcher: BoundMatcher) -> Expectation[A]:
        return SingleStrictExpectation(matcher, self.value)

    def __eq__(self, value: Any) -> Expectation[A]:
        return self.must(equal(value))

    def __ne__(self, value: Any) -> Expectation[A]:
        return self.must(not_equal(value))

    @property
    def true(self) -> MatchResult[A]:
        return self.must(equal(True))

    @property
    def false(self) -> MatchResult[A]:
        return self.must(equal(False))


class Expectable(ExpectableBase):

    def match(self, matcher: BoundMatcher) -> Expectation[A]:
        return self.safe_match(matcher)


class UnsafeExpectable(ExpectableBase):

    def match(self, matcher: BoundMatcher) -> Expectation[A]:
        return self.unsafe_match(matcher)


class CallableExpectable(ExpectableBase):

    def __init__(self, value: Callable[..., A], a: Any, kw: Any) -> None:
        self.value = value
        self.a = a
        self.kw = kw

    def match(self, matcher: BoundMatcher) -> Expectation[A]:
        return SingleCallableExpectation(matcher, self.value, self.a, self.kw)


class UnsafeCallableExpectable(ExpectableBase):

    def __init__(self, value: Callable[..., A], a: Any, kw: Any) -> None:
        self.wrapped = CallableExpectable(value, a, kw)

    def match(self, matcher: BoundMatcher) -> Expectation[A]:
        value = self.wrapped.match(matcher).fatal_eval()
        return UnsafeExpectation(matcher, value)


def k(value: A) -> ExpectableBase[A]:
    return Expectable(value)


def unsafe_k(value: A) -> ExpectableBase[A]:
    return UnsafeExpectable(value)


def kf(value: Callable[..., A], *a: Any, **kw: Any) -> ExpectableBase[A]:
    return CallableExpectable(value, a, kw)


def unsafe_kf(value: Callable[..., A], *a: Any, **kw: Any) -> ExpectableBase[A]:
    return UnsafeCallableExpectable(value, a, kw)

__all__ = ('Expectable', 'k', 'UnsafeExpectable', 'kf', 'unsafe_k', 'unsafe_kf')
