"""Test module for reaction rate coefficients."""

from flamespeed.test import env
from flamespeed import chemkin

rc = chemkin.ReactionCoefficients()

# ============================================
# Constant Reaction Rate Coefficient
# ============================================

def test_k_const():
    """Test constant reaction coefficients"""
    assert(rc.k_const()  == 1)
    assert(rc.k_const(5) == 5)
    assert(rc.k_const(0) == 0)

# ============================================
# Arrhenius Reaction Rate Coefficient
# ============================================

def test_k_arr():
    """Test Arrhenius reaction coefficients"""
    t1 = rc.k_arrhenius(A=10**7, E=10**3, T=10**2)
    t2 = rc.k_arrhenius(A=1, E=1, T=1)
    assert("{0:.2f}".format(t1,2) == '3003549.09')
    assert("{0:.2f}".format(t2,2) == '0.89')
    try:
        rc.k_arrhenius(A=10**7, E=10**3, T=-100)
    except ValueError as err:
        assert(type(err) == ValueError)
    try:
        rc.k_arrhenius(A=-10**7, E=10**3, T=10**2)
    except ValueError as err:
        assert(type(err) == ValueError)
    try:
        rc.k_arrhenius(A=10**7, E=10**3, T=10**2,R=-10)
    except ValueError as err:
        assert(type(err) == ValueError)

# ============================================
# Modified Arrhenius Reaction Rate Coefficient
# ============================================

def test_k_arr_mod():
    """Test modified Arrhenius reaction coefficients"""
    t1 = rc.k_arrhenius_mod(A=10**7, E=10**3, T=10**2, b=0.5)
    t2 = rc.k_arrhenius_mod(A=10, E=144, T=112, b=0.8)

    assert("{0:.2f}".format(t1,2) == '30035490.89')
    assert("{0:.2f}".format(t2,2) == '373.43')
    try:
        rc.k_arrhenius_mod(A=-10**7, E=10**3, T=10**2, b=0.5)
    except ValueError as err:
        assert(type(err) == ValueError)
    try:
        rc.k_arrhenius_mod(A=10**7, E=10**3, T=-10**2, b=0.5)
    except ValueError as err:
        assert(type(err) == ValueError)
    try:
        rc.k_arrhenius_mod(A=10**7, E=10**3, T=10**2, b=0.5, R=-10)
    except ValueError as err:
        assert(type(err) == ValueError)
