"""Test module for progress and reaction rate methods."""

from flamespeed.test import env
from flamespeed import chemkin
import numpy as np

# =================
# Progress rate
# =================


def test_progress_rate_01():
    """Test progress rate values."""
    rc = chemkin.ReactionRate()
    rate = rc.read_XML('../data/rxns_hw5.xml').set_temp(1500).get_progress_rate(np.array([2.0, 1.0, 0.5, 1.0, 1.0]))
    test1 = [2.81117621e+08, 5.00000000e+03, 4.48493847e+06]
    assert((rate == test1).all)

# =================
# Reaction rate
# =================


def test_reaction_rate_results_01():
    """Test reaction rate values."""
    rc = chemkin.ReactionRate()
    rate = rc.read_XML('../data/rxns_hw5.xml').set_temp(750).get_reaction_rate(np.array([2.0, 1.0, 0.5, 1.0, 1.0]))
    test1 = np.array([-3607077.87280406, -5613545.18362079, 9220623.05642485, 2006467.31081673, -2006467.31081673])
    assert((rate == test1).all)


def test_reaction_rate_results_02():
    """Test reaction rate values."""
    rc = chemkin.ReactionRate()
    rate = rc.read_XML('../data/rxns_hw5.xml').set_temp(1500).get_reaction_rate(np.array([2.0, 1.0, 0.5, 1.0, 1.0]))
    test1 = np.array([-2.81117621e+08, -2.85597559e+08, 5.66715180e+08, 4.47993847e+06, -4.47993847e+06])
    assert((rate == test1).all)


def test_reaction_rate__results_03():
    """Test reaction rate values."""
    rc = chemkin.ReactionRate()
    rate = rc.read_XML('../data/rxns_hw5.xml').set_temp(1500).get_reaction_rate(np.array([0, 0, 0, 0, 0]))
    test1 = np.array([0, 0, 0, 0, 0])
    assert((rate == test1).all)


def test_reaction_rate__input_01():
    """Test reaction rate input checks: Incorrect concentration array dimension."""
    rc = chemkin.ReactionRate()
    try:
        rate = rc.read_XML('../data/rxns_hw5.xml').set_temp(1500).get_reaction_rate(np.array([0, 0, 0]))
        return rate
    except ValueError as err:
        assert(type(err) == ValueError)


def test_reaction_rate__input_02():
    """Test reaction rate input checks: Negative temperature."""
    rc = chemkin.ReactionRate()
    try:
        rate = rc.read_XML('../data/rxns_hw5.xml').set_temp(1500).get_reaction_rate(np.array([1, 1, 1, 1, 1]))
        return rate
    except ValueError as err:
        assert(type(err) == ValueError)


def test_reaction_rate__input_03():
    """Test reaction rate input checks: Negative concentrations."""
    rc = chemkin.ReactionRate()
    try:
        rate = rc.read_XML('../data/rxns_hw5.xml').set_temp(1500).get_reaction_rate(np.array([-0.5, 1, 1, 1, 1]))
        return rate
    except ValueError as err:
        assert(type(err) == ValueError)
