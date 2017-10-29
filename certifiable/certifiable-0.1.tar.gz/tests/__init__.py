# -*- coding: utf-8 -*-

"""Unit test package for certifiable."""

from enum import Enum, unique

from certifiable import CertifierError


@unique
class TestEnum(Enum):
    A = 'a'
    B = 'b'
    X = 'x'
    Y = 'y'


@unique
class TestEnum1(Enum):
    W = 'w'
    X = 'x'
    Y = 'y'
    Z = 'z'


class TestError(Exception):
    def __init__(self, value=None):
        super(TestError, self).__init__()
        self.value = value


class Doh(CertifierError):
    def __init__(self, x=None):
        super(Doh, self).__init__('')
        self.x = x


class Alt(CertifierError):
    def __init__(self, x=None):
        super(Alt, self).__init__(x)
        self.x = x


def ok():
    pass


def nok(x=None, err=None):
    if err is not None:
        raise err(x)
    raise Doh(x)
