#! /usr/bin/python3
# -*- coding: utf-8 -*-

import pytest

from dimensionalquantity import Dimensional as D

# additions

def test_add_basics():
    q0 = D({'a':1, 'b':0, 'c':0})
    q1 = D({'a':0, 'b':1, 'd':0})
    q2_exp = D({'a':1, 'b':1, 'c': 0, 'd':0})

    q2_real = q0 + q1

    assert(q2_exp == q2_real)

def test_add_create_new_instances():
    q0 = D({'a':1, 'b':0, 'c':0})
    q1 = D({'a':0, 'b':1, 'd':0})
    q2 = q0+q1

    assert(id(q0)!=id(q2) and id(q1)!=id(q2))

def test_add_nomal_dict():
    q0 = D({'a':1, 'b':0, 'c':0})
    q_wrong = {'d':1} # this is a regular dict, not an instance of Dimensional

    q_exp = D({'a':1, 'b':0, 'c':0, 'd':1})

    assert(q_exp==q0+q_wrong) # this is True because Dimensional can handle the wrong type
    assert(q_exp==q_wrong+q0) # same for __radd__

def test_add_nondict():
    q0 = D({'a':1, 'b':0, 'c':0})
    with pytest.raises(TypeError):
        q2 = q0 + 1
    with pytest.raises(TypeError):
        q2 = 1 + q0

# subtractions

def test_sub_basics():
    q0 = D({'a':1, 'b':0, 'c':0})
    q1 = D({'a':0, 'b':1, 'd':0})
    q2_exp = D({'a':1, 'b':-1, 'c': 0, 'd':0})

    q2_real = q0 - q1

    assert(q2_exp == q2_real)

def test_sub_create_new_instances():
    q0 = D({'a':1, 'b':0, 'c':0})
    q1 = D({'a':0, 'b':1, 'd':0})
    q2 = q0-q1

    assert(id(q0)!=id(q2) and id(q1)!=id(q2))

def test_sub_nomal_dict():
    q0 = D({'a':1, 'b':0, 'c':0})
    q_wrong = {'d':1} # this is a regular dict, not an instance of Dimensional

    q_exp = D({'a':1, 'b':0, 'c':0, 'd':-1})
    q_exp_ = D({'a':-1, 'b':0, 'c':0, 'd':1})

    assert(q_exp==q0-q_wrong) # this is True because Dimensional can handle the wrong type
    assert(q_exp_==q_wrong-q0) # same for __rsub__

def test_sub_nondict():
    q0 = D({'a':1, 'b':0, 'c':0})
    with pytest.raises(TypeError):
        q2 = q0 - 1
    with pytest.raises(TypeError):
        q2 = 1 - q0

def test_mul():
    # __mul__ doesn't make sense hence it isn't implemented
    q0 = D({'a':1, 'b':0, 'c':0})
    q1 = D({'a':0, 'b':1, 'd':0})
    with pytest.raises(TypeError):
        q2 = q0 * q1

def test_mul_numeric():
    # __mul__ does make sense if the other is a number
    q0 = D({'a':1, 'b':0, 'c':0})
    q1 = -1*q0
    q0_ = D({'a':-1, 'b':0, 'c':0})
    assert( q1==q0_ )
    q2 = 2*q0
    assert( q2['a']==2 )

def test_div():
    # __div__ doesn't make sense hence it isn't implemented
    q0 = D({'a':1, 'b':0, 'c':0})
    q1 = D({'a':0, 'b':1, 'd':0})
    with pytest.raises(TypeError):
        q2 = q0 / q1

def test_decorator_wrapping():
    q0 = D({'a':1, 'b':0, 'c':0})

    assert( q0.__add__.__name__ == '__add__' )
    assert( q0.__sub__.__name__ == '__sub__' )
    assert( q0.__mul__.__name__ == '__mul__' )

    assert( q0.__radd__.__name__ == '__radd__' )
    assert( q0.__rsub__.__name__ == '__rsub__' )
    assert( q0.__rmul__.__name__ == '__rmul__' )

