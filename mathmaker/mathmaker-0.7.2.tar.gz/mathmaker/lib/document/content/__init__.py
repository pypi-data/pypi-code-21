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

"""All possible questions."""
from .algebra import expand_simple, expand_double
from .calculation import calculation_order_of_operations, multi_direct
from .calculation import multi_reversed, multi_hole, divi_direct, multi_clever
from .calculation import addi_direct, subtr_direct, rank_direct, rank_reversed
from .calculation import rank_numberof, vocabulary_simple_part_of_a_number
from .calculation import vocabulary_simple_multiple_of_a_number
from .calculation import vocabulary_multi, vocabulary_divi
from .calculation import vocabulary_addi, vocabulary_subtr
from .calculation import fraction_of_a_rectangle
from .calculation import addi_hole, subtr_hole
from .calculation import units_conversion, decimal_numerals
from .geometry import intercept_theorem_triangle
from .geometry import intercept_theorem_triangle_formula
from .geometry import intercept_theorem_butterfly
from .geometry import intercept_theorem_butterfly_formula
from .geometry import intercept_theorem_converse_triangle
from .geometry import intercept_theorem_converse_butterfly
from .geometry import trigonometry_calculate_length
from .geometry import trigonometry_calculate_angle
from .geometry import trigonometry_formula
from .geometry import trigonometry_vocabulary
from .geometry import area_rectangle, area_square, perimeter_rectangle
from .geometry import perimeter_square, rectangle_length_or_width

__all__ = ['expand_simple', 'expand_double',
           'multi_direct', 'multi_reversed', 'multi_hole', 'divi_direct',
           'multi_clever',
           'addi_direct', 'subtr_direct', 'rank_direct', 'rank_reversed',
           'rank_numberof', 'vocabulary_simple_part_of_a_number',
           'vocabulary_simple_multiple_of_a_number', 'vocabulary_multi',
           'vocabulary_divi', 'vocabulary_addi', 'vocabulary_subtr',
           'fraction_of_a_rectangle', 'calculation_order_of_operations',
           'addi_hole', 'subtr_hole',
           'units_conversion', 'decimal_numerals',
           'area_rectangle', 'area_square', 'perimeter_rectangle',
           'perimeter_square', 'rectangle_length_or_width',
           'intercept_theorem_triangle', 'intercept_theorem_triangle_formula',
           'intercept_theorem_butterfly',
           'intercept_theorem_butterfly_formula',
           'intercept_theorem_converse_triangle',
           'intercept_theorem_converse_butterfly',
           'trigonometry_calculate_length',
           'trigonometry_calculate_angle',
           'trigonometry_formula',
           'trigonometry_vocabulary']
