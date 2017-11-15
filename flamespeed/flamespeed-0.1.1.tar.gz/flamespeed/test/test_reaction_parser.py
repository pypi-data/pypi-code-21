"""Test module for read_XML method."""

from flamespeed.test import env
from flamespeed import chemkin


# =================
# Read XML
# =================


def test_read_XML_01():
    """Test XML file import: Phase tag not included."""
    rc = chemkin.ReactionRate()
    try:
        f = rc.read_XML('../data/rxns_test/rxns_test_01.xml')
        return f
    except ValueError as err:
        assert(type(err) == ValueError)


def test_read_XML_02():
    """Test XML file import: New Arrhenius coefficient included."""
    rc = chemkin.ReactionRate()
    try:
        f = rc.read_XML('../data/rxns_test/rxns_test_02.xml')
        return f
    except NotImplementedError as err:
        assert(type(err) == NotImplementedError)


def test_read_XML_03():
    """Test XML file import: Includes reversible reaction."""
    rc = chemkin.ReactionRate()
    try:
        f = rc.read_XML('../data/rxns_test/rxns_test_03.xml')
        return f
    except NotImplementedError as err:
        assert(type(err) == NotImplementedError)


def test_read_XML_04():
        """Test XML file import: Includes duplicate reaction."""
        rc = chemkin.ReactionRate()
        try:
            f = rc.read_XML('../data/rxns_test/rxns_test_04.xml')
            return f
        except NotImplementedError as err:
            assert(type(err) == NotImplementedError)


def test_read_XML_05():
        """Test XML file import: Missing param for modified Arrhenius."""
        rc = chemkin.ReactionRate()
        try:
            f = rc.read_XML('../data/rxns_test/rxns_test_05.xml')
            return f
        except ValueError as err:
            assert(type(err) == ValueError)


def test_read_XML_06():
        """Test XML file import: Missing reaction coefficients."""
        rc = chemkin.ReactionRate()
        try:
            f = rc.read_XML('../data/rxns_test/rxns_test_06.xml')
            return f
        except ValueError as err:
            assert(type(err) == ValueError)
