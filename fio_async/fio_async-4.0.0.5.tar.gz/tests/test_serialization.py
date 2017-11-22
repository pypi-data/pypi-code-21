# -*- coding: utf-8 -*-
import json
import unittest
import datetime
from decimal import Decimal

import trytond.tests.test_tryton
from trytond.tests.test_tryton import POOL, USER
from trytond.tests.test_tryton import DB_NAME, CONTEXT
from trytond.transaction import Transaction
from trytond_async.serialization import JSONEncoder, JSONDecoder


class TestSerialization(unittest.TestCase):
    'Test Serialization'

    def setUp(self):
        """
        Set up data used in the tests.
        this method is called before each test function execution.
        """
        trytond.tests.test_tryton.install_module('async')

    def dumps_loads(self, value):
        self.assertEqual(
            json.loads(
                json.dumps(value, cls=JSONEncoder),
                object_hook=JSONDecoder()
            ), value
        )

    def test_datetime(self):
        'Test datetime'
        self.dumps_loads(datetime.datetime.now())

    def test_date(self):
        'Test date'
        self.dumps_loads(datetime.date.today())

    def test_time(self):
        'Test time'
        self.dumps_loads(datetime.datetime.now().time())

    def test_bytes(self):
        'Test Bytes'
        self.dumps_loads(bytearray("foo"))

    def test_decimal(self):
        'Test Decimal'
        self.dumps_loads(Decimal('3.141592653589793'))

    def test_active_record(self):
        with Transaction().start(DB_NAME, USER, context=CONTEXT):
            View = POOL.get('ir.ui.view')

            # Result from search
            self.dumps_loads(View.search([], limit=1)[0])
            self.dumps_loads(View.search([]))

            # Result from ID lookup
            self.dumps_loads(View(1))

            # Result from unsaved record
            # self.dumps_loads(View(name='bla bla'))


def suite():
    """
    Define suite
    """
    test_suite = trytond.tests.test_tryton.suite()
    test_suite.addTests(
        unittest.TestLoader().loadTestsFromTestCase(TestSerialization)
    )
    return test_suite

if __name__ == '__main__':
    unittest.TextTestRunner(verbosity=2).run(suite())
