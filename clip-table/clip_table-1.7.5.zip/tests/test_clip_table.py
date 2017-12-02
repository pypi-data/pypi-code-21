#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""Tests for `clip_table` package."""

import pytest


from clip_table import clip_table

import pytest

from clip_table import (get_clipboard, put_clipboard,
                                 parse_table_string, get_table,
                                 empty_clipboard)


_starting_clipboard = None


def setup_module():
    global _starting_clipboard
    _starting_clipboard = get_clipboard()


def teardown_module():
    if not _starting_clipboard:
        put_clipboard('')
    else:
        put_clipboard(_starting_clipboard)


TABLE = [['OrderDate', 'Region', 'Rep', 'Item', 'Units', 'Unit Cost', 'Total'],
         ['1/6/2016', 'East', 'Jones', 'Pencil', '95', '1.99', '189.05'],
         ['1/23/2016', 'Central', 'Kivell', 'Binder', '50', '19.99', '999.5'],
         ['2/9/2016', 'Central', 'Jardine', 'Pencil', '36', '4.99', '179.64'],
         ['2/26/2016', 'Central', 'Gill', 'Pen', '27', '19.99', '539.73'],
         ['3/15/2016', 'West', 'Sorvino', 'Pencil', '56', '2.99', '167.44'],
         ['4/1/2016', 'East', 'Jones', 'Binder', '60', '4.99', '299.4'],
         ['4/18/2016', 'Central', 'Andrews', 'Pencil', '75', '1.99', '149.25'],
         ['5/5/2016', 'Central', 'Jardine', 'Pencil', '90', '4.99', '449.1'],
         ['5/22/2016', 'West', 'Thompson', 'Pencil', '32', '1.99', '63.68'],
         ['6/8/2016', 'East', 'Jones', 'Binder', '60', '8.99', '539.4'],
         ['6/25/2016', 'Central', 'Morgan', 'Pencil', '90', '4.99', '449.1'],
         ['7/12/2016', 'East', 'Howard', 'Binder', '29', '1.99', '57.71'],
         ['7/29/2016', 'East', 'Parent', 'Binder', '81', '19.99', '1,619.19'],
         ['8/15/2016', 'East', 'Jones', 'Pencil', '35', '4.99', '174.65'],
         ['9/1/2016', 'Central', 'Smith', 'Desk', '2', '125', '250'],
         ['9/18/2016', 'East', 'Jones', 'Pen Set', '16', '15.99', '255.84'],
         ['10/5/2016', 'Central', 'Morgan', 'Binder', '28', '8.99', '251.72'],
         ['10/22/2016', 'East', 'Jones', 'Pen', '64', '8.99', '575.36'],
         ['11/8/2016', 'East', 'Parent', 'Pen', '15', '19.99', '299.85'],
         ['11/25/2016', 'Central', 'Kivell', 'Pen Set', '96', '4.99', '479.04'],
         ['12/12/2016', 'Central', 'Smith', 'Pencil', '67', '1.29', '86.43'],
         ['12/29/2016', 'East', 'Parent', 'Pen Set', '74', '15.99', '1,183.26'],
         ['1/15/2017', 'Central', 'Gill', 'Binder', '46', '8.99', '413.54'],
         ['2/1/2017', 'Central', 'Smith', 'Binder', '87', '15', '1,305.00'],
         ['2/18/2017', 'East', 'Jones', 'Binder', '4', '4.99', '19.96'],
         ['3/7/2017', 'West', 'Sorvino', 'Binder', '7', '19.99', '139.93'],
         ['3/24/2017', 'Central', 'Jardine', 'Pen Set', '50', '4.99', '249.5'],
         ['4/10/2017', 'Central', 'Andrews', 'Pencil', '66', '1.99', '131.34'],
         ['4/27/2017', 'East', 'Howard', 'Pen', '96', '4.99', '479.04'],
         ['5/14/2017', 'Central', 'Gill', 'Pencil', '53', '1.29', '68.37'],
         ['5/31/2017', 'Central', 'Gill', 'Binder', '80', '8.99', '719.2'],
         ['6/17/2017', 'Central', 'Kivell', 'Desk', '5', '125', '625'],
         ['7/4/2017', 'East', 'Jones', 'Pen Set', '62', '4.99', '309.38'],
         ['7/21/2017', 'Central', 'Morgan', 'Pen Set', '55', '12.49', '686.95'],
         [
             '8/7/2017', 'Central', 'Kivell', 'Pen Set', '42', '23.95',
             '1,005.90'],
         ['8/24/2017', 'West', 'Sorvino', 'Desk', '3', '275', '825'],
         ['9/10/2017', 'Central', 'Gill', 'Pencil', '7', '1.29', '9.03'],
         ['9/27/2017', 'West', 'Sorvino', 'Pen', '76', '1.99', '151.24'], [
             '10/14/2017', 'West', 'Thompson', 'Binder', '57', '19.99',
             '1,139.43'],
         ['10/31/2017', 'Central', 'Andrews', 'Pencil', '14', '1.29', '18.06'],
         ['11/17/2017', 'Central', 'Jardine', 'Binder', '11', '4.99', '54.89'],
         ['12/4/2017', 'Central', 'Jardine', 'Binder', '94', '19.99',
          '1,879.06'],
         ['12/21/2017', 'Central', 'Andrews', 'Binder', '28', '4.99', '139.72']]
TABLE_TEXT = b'OrderDate\tRegion\tRep\tItem\tUnits\tUnit ' \
             b'Cost\tTotal\r\n1/6/2016\tEast\tJones\tPencil\t95\t1.99\t189.05' \
             b'\r\n1/23/2016\tCentral\tKivell\tBinder\t50\t19.99\t999.5\r\n2' \
             b'/9/2016\tCentral\tJardine\tPencil\t36\t4.99\t179.64\r\n2/26' \
             b'/2016\tCentral\tGill\tPen\t27\t19.99\t539.73\r\n3/15/2016' \
             b'\tWest\tSorvino\tPencil\t56\t2.99\t167.44\r\n4/1/2016\tEast' \
             b'\tJones\tBinder\t60\t4.99\t299.4\r\n4/18/2016\tCentral' \
             b'\tAndrews\tPencil\t75\t1.99\t149.25\r\n5/5/2016\tCentral' \
             b'\tJardine\tPencil\t90\t4.99\t449.1\r\n5/22/2016\tWest' \
             b'\tThompson\tPencil\t32\t1.99\t63.68\r\n6/8/2016\tEast\tJones' \
             b'\tBinder\t60\t8.99\t539.4\r\n6/25/2016\tCentral\tMorgan' \
             b'\tPencil\t90\t4.99\t449.1\r\n7/12/2016\tEast\tHoward\tBinder' \
             b'\t29\t1.99\t57.71\r\n7/29/2016\tEast\tParent\tBinder\t81\t19' \
             b'.99\t1,619.19\r\n8/15/2016\tEast\tJones\tPencil\t35\t4.99\t174' \
             b'.65\r\n9/1/2016\tCentral\tSmith\tDesk\t2\t125\t250\r\n9/18' \
             b'/2016\tEast\tJones\tPen ' \
             b'Set\t16\t15.99\t255.84\r\n10/5/2016\tCentral\tMorgan\tBinder' \
             b'\t28\t8.99\t251.72\r\n10/22/2016\tEast\tJones\tPen\t64\t8.99' \
             b'\t575.36\r\n11/8/2016\tEast\tParent\tPen\t15\t19.99\t299.85\r' \
             b'\n11/25/2016\tCentral\tKivell\tPen ' \
             b'Set\t96\t4.99\t479.04\r\n12/12/2016\tCentral\tSmith\tPencil' \
             b'\t67\t1.29\t86.43\r\n12/29/2016\tEast\tParent\tPen ' \
             b'Set\t74\t15.99\t1,' \
             b'183.26\r\n1/15/2017\tCentral\tGill\tBinder\t46\t8.99\t413.54\r' \
             b'\n2/1/2017\tCentral\tSmith\tBinder\t87\t15\t1,' \
             b'305.00\r\n2/18/2017\tEast\tJones\tBinder\t4\t4.99\t19.96\r\n3' \
             b'/7/2017\tWest\tSorvino\tBinder\t7\t19.99\t139.93\r\n3/24/2017' \
             b'\tCentral\tJardine\tPen ' \
             b'Set\t50\t4.99\t249.5\r\n4/10/2017\tCentral\tAndrews\tPencil' \
             b'\t66\t1.99\t131.34\r\n4/27/2017\tEast\tHoward\tPen\t96\t4.99' \
             b'\t479.04\r\n5/14/2017\tCentral\tGill\tPencil\t53\t1.29\t68.37' \
             b'\r\n5/31/2017\tCentral\tGill\tBinder\t80\t8.99\t719.2\r\n6/17' \
             b'/2017\tCentral\tKivell\tDesk\t5\t125\t625\r\n7/4/2017\tEast' \
             b'\tJones\tPen Set\t62\t4.99\t309.38\r\n7/21/2017\tCentral' \
             b'\tMorgan\tPen ' \
             b'Set\t55\t12.49\t686.95\r\n8/7/2017\tCentral\tKivell\tPen ' \
             b'Set\t42\t23.95\t1,' \
             b'005.90\r\n8/24/2017\tWest\tSorvino\tDesk\t3\t275\t825\r\n9/10' \
             b'/2017\tCentral\tGill\tPencil\t7\t1.29\t9.03\r\n9/27/2017\tWest' \
             b'\tSorvino\tPen\t76\t1.99\t151.24\r\n10/14/2017\tWest\tThompson' \
             b'\tBinder\t57\t19.99\t1,' \
             b'139.43\r\n10/31/2017\tCentral\tAndrews\tPencil\t14\t1.29\t18' \
             b'.06\r\n11/17/2017\tCentral\tJardine\tBinder\t11\t4.99\t54.89\r' \
             b'\n12/4/2017\tCentral\tJardine\tBinder\t94\t19.99\t1,' \
             b'879.06\r\n12/21/2017\tCentral\tAndrews\tBinder\t28\t4.99\t139' \
             b'.72\r\n'.decode()

COLUMN_TEXT = b'OrderDate\r\n1/6/2016\r\n1/23/2016\r\n2/9/2016\r\n2/26/2016\r' \
              b'\n3/15/2016\r\n4/1/2016\r\n4/18/2016\r\n5/5/2016\r\n5/22/2016' \
              b'\r\n6/8/2016\r\n6/25/2016\r\n7/12/2016\r\n7/29/2016\r\n8/15' \
              b'/2016\r\n9/1/2016\r\n9/18/2016\r\n10/5/2016\r\n10/22/2016\r' \
              b'\n11/8/2016\r\n11/25/2016\r\n12/12/2016\r\n12/29/2016\r\n1/15' \
              b'/2017\r\n2/1/2017\r\n2/18/2017\r\n3/7/2017\r\n3/24/2017\r\n4' \
              b'/10/2017\r\n4/27/2017\r\n5/14/2017\r\n5/31/2017\r\n6/17/2017' \
              b'\r\n7/4/2017\r\n7/21/2017\r\n8/7/2017\r\n8/24/2017\r\n9/10' \
              b'/2017\r\n9/27/2017\r\n10/14/2017\r\n10/31/2017\r\n11/17/2017' \
              b'\r\n12/4/2017\r\n12/21/2017\r\n'.decode()
COLUMN = [
    ['OrderDate'], ['1/6/2016'], ['1/23/2016'], ['2/9/2016'],
    ['2/26/2016'],
    ['3/15/2016'], ['4/1/2016'], ['4/18/2016'], ['5/5/2016'],
    ['5/22/2016'],
    ['6/8/2016'], ['6/25/2016'], ['7/12/2016'], ['7/29/2016'],
    ['8/15/2016'],
    ['9/1/2016'], ['9/18/2016'], ['10/5/2016'], ['10/22/2016'],
    ['11/8/2016'],
    ['11/25/2016'], ['12/12/2016'], ['12/29/2016'], ['1/15/2017'],
    ['2/1/2017'],
    ['2/18/2017'], ['3/7/2017'], ['3/24/2017'], ['4/10/2017'],
    ['4/27/2017'],
    ['5/14/2017'], ['5/31/2017'], ['6/17/2017'], ['7/4/2017'],
    ['7/21/2017'],
    ['8/7/2017'], ['8/24/2017'], ['9/10/2017'], ['9/27/2017'],
    ['10/14/2017'],
    ['10/31/2017'], ['11/17/2017'], ['12/4/2017'], ['12/21/2017']
]

ROW_TEXT = b'1/6/2016\tEast\tJones\tPencil\t95\t1.99\t189.05\r\n'.decode()
ROW = [['1/6/2016', 'East', 'Jones', 'Pencil', '95', '1.99', '189.05']]

NEEDS_TRIM_TEXT = b'a\tb\tc\t\nd\te\tf\t\n\t\t\t\t'.decode()
NEEDS_TRIM = [['a', 'b', 'c'],
              ['d', 'e', 'f']]

BLANK = b'\r\n'.decode()
EXPECTED_BLANK = [[]]

TEST_VALUES = [(COLUMN_TEXT, COLUMN), (ROW_TEXT, ROW),
               (TABLE_TEXT, TABLE), (BLANK, EXPECTED_BLANK)]


def test_get_put():
    value = 'ABCDEFG'
    put_clipboard(value)
    result = get_clipboard()
    assert result == value


def test_clear():
    put_clipboard('A')
    value = get_clipboard()
    assert value == 'A'
    empty_clipboard()
    new = get_clipboard()
    assert not new


def test_trim():
    put_clipboard(NEEDS_TRIM_TEXT)
    got_table = get_table()
    assert len(got_table) == len(NEEDS_TRIM)
    for got_row, expected_row in zip(got_table, NEEDS_TRIM):
        expected_row = expected_row
        assert got_row == expected_row


@pytest.mark.parametrize('text,expected_table', TEST_VALUES)
def test_excel_format(text, expected_table):
    got_table = parse_table_string(text)
    assert len(got_table) == len(expected_table)
    for got_row, expected_row in zip(got_table, expected_table):
        expected_row = expected_row
        assert got_row == expected_row
