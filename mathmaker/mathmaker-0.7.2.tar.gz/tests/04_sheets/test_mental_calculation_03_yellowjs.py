# -*- coding: utf-8 -*-

# Mathmaker creates automatically maths exercises sheets
# with their answers
# Copyright 2006-2017 Nicolas Hainaux <nh.techn@gmail.com>

# This file is part of Mathmaker.

# Mathmaker is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation; either version 3 of the License, or
# any later version.

# Mathmaker is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.

# You should have received a copy of the GNU General Public License
# along with Mathmaker; if not, write to the Free Software
# Foundation, Inc., 51 Franklin St, Fifth Floor, Boston, MA  02110-1301  USA


from mathmaker.lib import shared
from mathmaker.lib.document.frames import Sheet


def test_03_yellow_complements():
    """Check this sheet is generated without any error."""
    shared.machine.write_out(str(Sheet('mental_calculation',
                                       '03_yellow',
                                       'complements',
                                       enable_js_form=True)))


def test_03_yellow_addi_subtr_hole():
    """Check this sheet is generated without any error."""
    shared.machine.write_out(str(Sheet('mental_calculation',
                                       '03_yellow',
                                       'addi_subtr_hole',
                                       enable_js_form=True)))


def test_03_yellow_units_conversions():
    """Check this sheet is generated without any error."""
    shared.machine.write_out(str(Sheet('mental_calculation',
                                       '03_yellow',
                                       'units_conversions',
                                       enable_js_form=True)))


def test_03_yellow_decimal_numerals():
    """Check this sheet is generated without any error."""
    shared.machine.write_out(str(Sheet('mental_calculation',
                                       '03_yellow',
                                       'decimal_numerals',
                                       enable_js_form=True)))


def test_03_yellow_operations_vocabulary():
    """Check this sheet is generated without any error."""
    shared.machine.write_out(str(Sheet('mental_calculation',
                                       '03_yellow',
                                       'operations_vocabulary',
                                       enable_js_form=True)))


def test_03_yellow_positional_notation():
    """Check this sheet is generated without any error."""
    shared.machine.write_out(str(Sheet('mental_calculation',
                                       '03_yellow',
                                       'positional_notation',
                                       enable_js_form=True)))


def test_03_yellow_rectangles():
    """Check this sheet is generated without any error."""
    shared.machine.write_out(str(Sheet('mental_calculation',
                                       '03_yellow',
                                       'rectangles',
                                       enable_js_form=True)))


def test_03_yellow_tables_15_25():
    """Check this sheet is generated without any error."""
    shared.machine.write_out(str(Sheet('mental_calculation',
                                       '03_yellow',
                                       'tables_15_25',
                                       enable_js_form=True)))


def test_03_yellow_exam():
    """Check this sheet is generated without any error."""
    shared.machine.write_out(str(Sheet('mental_calculation',
                                       '03_yellow',
                                       'exam',
                                       enable_js_form=True)))
