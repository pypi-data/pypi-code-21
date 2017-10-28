#! /usr/bin/python3
# -*- coding: utf-8 -*-

"""
Dimensional works with a regular dict.
Problem with regular dicts:
the order of their keys isn't guaranteed.
From a functional point of view this is not a problem:
'm.s-1' are absolutely equivalent to 's-1.m'.
But from a testing point of view, these two strings differ from each other.
Consequentially, the following tests pass
for any of several equivalent strings.
"""

import pytest

from dimensionalquantity import Dimensional as D
from dimensionalquantity import BaseDimQuant as BDQ
from dimensionalquantity import DimQuant as DQ

def accept_multiple_possibilities(possibilities, dimquant, method):
    """As mentioned in the doc-string describing the tests collected in this file,
    the str() and repr() can result in multiple equally valid strings.
    This function helps to abstract this fact."""
    passed = False
    for possibility in possibilities:
        if method(dimquant)==possibility:
            passed = True
            break
    return passed

def test_dimquant_with_str_init():
    q0 = DQ('1 m')
    q1 = DQ('1 s')
    q2 = DQ('1 m/s')
    assert( q2==(q0/q1) )
    q2_ = DQ('1 m.s-1')
    assert( q2==q2_ )

@pytest.mark.parametrize('expected_strs,dq',(
                         ( ('1 m.s-1','1 s-1.m'),
                             DQ(1, D({'L': 1, 't': -1}))),
                         ( ('2 m.s-1','2 s-1.m'),
                             DQ(2, D({'L': 1, 't': -1}))),
                         ( ('1 m2.s-1','1 s-1.m2'),
                             DQ(1, D({'L': 2, 't': -1}))),
                        ))
def test_dimquant_str_out(expected_strs,dq):
    assert( accept_multiple_possibilities(expected_strs, dq, str) )

@pytest.mark.parametrize('expected_reprs,dq',(
                         ( ('BaseDimQuant(1, Dimensional({\'L\': 1, \'t\': -1}))',
                            'BaseDimQuant(1, Dimensional({\'t\': -1, \'L\': 1}))'),
                             BDQ(1, D({'L': 1, 't': -1}))),
                         ( ('BaseDimQuant(2, Dimensional({\'L\': 1, \'t\': -1}))',
                            'BaseDimQuant(2, Dimensional({\'t\': -1, \'L\': 1}))'),
                             BDQ(2, D({'L': 1, 't': -1}))),
                         ( ('BaseDimQuant(1, Dimensional({\'L\': 2, \'t\': -1}))',
                            'BaseDimQuant(1, Dimensional({\'t\': -1, \'L\': 2}))'),
                             BDQ(1, D({'L': 2, 't': -1}))),
                        ))
def test_basedimquant_repr_out(expected_reprs,dq):
    assert( accept_multiple_possibilities(expected_reprs, dq, repr) )

@pytest.mark.parametrize('expected_reprs,dq',(
                         ( ('DimQuant(1, Dimensional({\'L\': 1, \'t\': -1}))',
                            'DimQuant(1, Dimensional({\'t\': -1, \'L\': 1}))'),
                             DQ(1, D({'L': 1, 't': -1}))),
                         ( ('DimQuant(2, Dimensional({\'L\': 1, \'t\': -1}))',
                            'DimQuant(2, Dimensional({\'t\': -1, \'L\': 1}))'),
                             DQ(2, D({'L': 1, 't': -1}))),
                         ( ('DimQuant(1, Dimensional({\'L\': 2, \'t\': -1}))',
                            'DimQuant(1, Dimensional({\'t\': -1, \'L\': 2}))'),
                             DQ(1, D({'L': 2, 't': -1}))),
                        ))
def test_dimquant_repr_out(expected_reprs,dq):
    assert( accept_multiple_possibilities(expected_reprs, dq, repr) )

@pytest.mark.parametrize('expected_strs, dq', (
                         ( ('1.0 m/s', '1.0 m.s-1.0', '1.0 s-1.0.m', '1.0 s-1.m', '1.0 m.s-1'),
                             DQ('1 m')/DQ('1 s')),
                         ( ('2.0 m/s', '2.0 m.s-1.0', '2.0 s-1.0.m', '2.0 s-1.m', '2.0 m.s-1'),
                             DQ('1 m/s')+DQ('1 m/s')),
                         ( ('3.0 m/s', '3.0 m.s-1.0', '3.0 s-1.0.m', '3.0 s-1.m', '3.0 m.s-1'),
                             DQ('4 m/s')-DQ('1 m/s')),
                         ( ('4.0 m/s', '4.0 m.s-1.0', '4.0 s-1.0.m', '4.0 s-1.m', '4.0 m.s-1'),
                             DQ('2 m')*DQ('2 s-1')),
                         ))
def test_dimquant_str_out_after_calc(expected_strs, dq):
    assert( accept_multiple_possibilities(expected_strs, dq, str) )
