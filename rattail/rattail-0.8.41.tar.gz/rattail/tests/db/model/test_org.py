# -*- coding: utf-8 -*-

from __future__ import unicode_literals, absolute_import

import decimal

from rattail.db import model
from rattail.tests import DataTestCase


class TestDepartment(DataTestCase):

    def test_unicode(self):
        dept = model.Department()
        self.assertEqual(unicode(dept), "")

        dept = model.Department(name=b"Grocery")
        self.assertEqual(unicode(dept), "Grocery")


class TestSubdepartment(DataTestCase):

    def test_unicode(self):
        subdept = model.Subdepartment()
        self.assertEqual(unicode(subdept), "")

        subdept = model.Subdepartment(name=b"Canned Goods")
        self.assertEqual(unicode(subdept), "Canned Goods")


class TestCategory(DataTestCase):

    def test_unicode(self):
        category = model.Category()
        self.assertEqual(unicode(category), "")

        category = model.Category(name=b"Various Odds and Ends")
        self.assertEqual(unicode(category), "Various Odds and Ends")


class TestFamily(DataTestCase):

    def test_unicode(self):
        family = model.Family()
        self.assertEqual(unicode(family), "")

        family = model.Family(name=b"Various Odds and Ends")
        self.assertEqual(unicode(family), "Various Odds and Ends")


class TestReportCode(DataTestCase):

    def test_unicode(self):
        code = model.ReportCode()
        self.assertEqual(unicode(code), "")

        code = model.ReportCode(code=42, name=b"Various Odds and Ends")
        self.assertEqual(unicode(code), "42 - Various Odds and Ends")
