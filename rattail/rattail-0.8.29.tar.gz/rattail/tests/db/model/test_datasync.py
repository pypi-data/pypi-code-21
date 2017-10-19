# -*- coding: utf-8 -*-

from __future__ import unicode_literals, absolute_import

from rattail.db import model
from rattail.tests import DataTestCase


class TestDataSyncChange(DataTestCase):

    def test_unicode(self):
        change = model.DataSyncChange()
        self.assertEqual(unicode(change), "(empty)")

        change = model.DataSyncChange(payload_type='Product', payload_key='00074305001321')
        self.assertEqual(unicode(change), "Product: 00074305001321")

        change = model.DataSyncChange(payload_type='Product', payload_key='00074305001321', deletion=True)
        self.assertEqual(unicode(change), "Product: 00074305001321 (deletion)")
