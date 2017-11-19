"""Test module for progress and reaction rate methods."""

import os
from flamespeed.test import env
from flamespeed import chemkin
import numpy as np

# =================
# Progress rate
# =================

def test_progress_rate_01():
    """Test progress rate values."""
    rc = chemkin.ReactionRate()
    rate = rc.read_XML('./data/rxns_hw5.xml').set_temp(1500).get_progress_rate(np.array([2.0, 1.0, 0.5, 1.0, 1.0]))
    test1 = [2.81117621e+08, 5.00000000e+03, 4.48493847e+06]

    np.testing.assert_allclose(rate, test1)

    
def test_progress_rate_02():
    """Test progress rate values."""
    rc = chemkin.ReactionRate()
    rate = rc.read_XML('./data/rxns_reversible.xml').set_temp(750).get_progress_rate(np.array([1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0]))
    test1 = [ -6.877890e+16,  -5.885899e+11,   2.734187e+12,  -2.207822e+15,\
            1.454746e+13,   6.751893e+13,   3.250000e+13,   3.129776e+13,\
            1.275004e+13,   1.346908e+13,   2.841957e+12]

    np.testing.assert_allclose(rate, test1, 1e-06)

# test_progress_rate_02()
# =================
# Reaction rate
# =================


def test_reaction_rate_results_01():
    """Test reaction rate values."""
    rc = chemkin.ReactionRate()
    rate = rc.read_XML('./data/rxns_hw5.xml').set_temp(750).get_reaction_rate(np.array([2.0, 1.0, 0.5, 1.0, 1.0]))
    test1 = np.array([-3607077.87280406, -5613545.18362079, 9220623.05642485, 2006467.31081673, -2006467.31081673])
    np.testing.assert_allclose(rate, test1)


def test_reaction_rate_results_02():
    """Test reaction rate values."""
    rc = chemkin.ReactionRate()
    rate = rc.read_XML('./data/rxns_hw5.xml').set_temp(1500).get_reaction_rate(np.array([2.0, 1.0, 0.5, 1.0, 1.0]))
    test1 = np.array([-2.81117621e+08, -2.85597559e+08, 5.66715180e+08, 4.47993847e+06, -4.47993847e+06])
    np.testing.assert_allclose(rate, test1)


def test_reaction_rate__results_03():
    """Test reaction rate values."""
    rc = chemkin.ReactionRate()
    rate = rc.read_XML('./data/rxns_hw5.xml').set_temp(1500).get_reaction_rate(np.array([0, 0, 0, 0, 0]))
    test1 = np.array([0, 0, 0, 0, 0])
    np.testing.assert_allclose(rate, test1)


# =========================
# Reaction rate (reversible)
# =========================

def test_reaction_rate_reversible_results_01():
    """Test reaction rate values."""
    rc = chemkin.ReactionRate()
    rate = rc.read_XML('./data/rxns_reversible.xml').set_temp(750).get_reaction_rate(np.array([2.0, 1.0, 0.5, 1.0, 1.0, 1.5, 0.5, 1]))
    test1 = np.array([3.42136106e+16, -3.38140521e+16, -3.52810647e+16,  4.07078985e+13,
                      5.86479725e+14,  3.43859595e+16, -7.63606069e+13, -5.52803119e+13])
    np.testing.assert_allclose(rate, test1)
 
def test_reaction_rate_reversible_results_02():
    """Test reaction rate values."""
    rc = chemkin.ReactionRate()
    cwd = os.getcwd()
    print (cwd)
    rate = rc.read_XML('./data/rxns_reversible.xml').set_temp(1500).get_reaction_rate(np.array([0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0]))
    test1 = np.array([ 0., 0., 0., 0., 0., 0., 0., 0.])
    np.testing.assert_allclose(rate, test1)

# =========================
# Reaction rate (input)
# =========================

def test_reaction_rate__input_01():
    """Test reaction rate input checks: Incorrect concentration array dimension."""
    rc = chemkin.ReactionRate()
    try:
        rate = rc.read_XML('./data/rxns_hw5.xml').set_temp(1500).get_reaction_rate(np.array([0, 0, 0]))
        return rate
    except ValueError as err:
        assert(type(err) == ValueError)


def test_reaction_rate__input_02():
    """Test reaction rate input checks: Negative temperature."""
    rc = chemkin.ReactionRate()
    try:
        rate = rc.read_XML('./data/rxns_hw5.xml').set_temp(1500).get_reaction_rate(np.array([1, 1, 1, 1, 1]))
        return rate
    except ValueError as err:
        assert(type(err) == ValueError)


def test_reaction_rate__input_03():
    """Test reaction rate input checks: Negative concentrations."""
    rc = chemkin.ReactionRate()
    try:
        rate = rc.read_XML('./data/rxns_hw5.xml').set_temp(1500).get_reaction_rate(np.array([-0.5, 1, 1, 1, 1]))
        return rate
    except ValueError as err:
        assert(type(err) == ValueError)
        
def test_reaction_rate__input_04():
    """Test reaction rate input checks: Negative concentrations."""
    rc = chemkin.ReactionRate()
    try:
        rate = rc.read_XML('./data/rxns_reversible.xml').set_temp(150).get_reaction_rate(np.array([-0.5, 1, 1, 1, 1]))
        return rate
    except ValueError as err:
        assert(type(err) == ValueError)