# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0.  If a copy of the MPL was not distributed with this
# file, You can obtain one at http://mozilla.org/MPL/2.0/.
#
# Copyright 1997 - July 2008 CWI, August 2008 - 2016 MonetDB B.V.

import os
import unittest
#import logging
#logging.basicConfig(level=logging.DEBUG)
from pymonetdb.control import Control
from pymonetdb.exceptions import OperationalError

FULL_TEST = False
MAPIPORT = int(os.environ.get('MAPIPORT', 50000))
TSTHOSTNAME = os.environ.get('TSTHOSTNAME', 'localhost')
TSTPASSPHRASE = os.environ.get('TSTPASSPHRASE', 'testdb')

database_prefix = 'controltest_'
database_name = database_prefix + 'other'
passphrase = 'testdb'


def do_without_fail(function):
    try:
        function()
    except OperationalError:
        pass


class TestControl(unittest.TestCase):
    def setUp(self):
        # use tcp
        self.control = Control(TSTHOSTNAME, MAPIPORT, TSTPASSPHRASE)

        # use socket
        #self.control = Control()

        do_without_fail(lambda: self.control.stop(database_name))
        do_without_fail(lambda: self.control.destroy(database_name))
        self.control.create(database_name)

    def tear_down(self):
        do_without_fail(lambda: self.control.stop(database_name))
        do_without_fail(lambda: self.control.destroy(database_name))

    def test_create(self):
        create_name = database_prefix + "create"
        do_without_fail(lambda: self.control.destroy(create_name))
        self.control.create(create_name)
        self.assertRaises(OperationalError, self.control.create, create_name)
        do_without_fail(lambda: self.control.destroy(create_name))

    def test_destroy(self):
        destroy_name = database_prefix + "destroy"
        self.control.create(destroy_name)
        self.control.destroy(destroy_name)
        self.assertRaises(OperationalError, self.control.destroy, destroy_name)

    def test_lock(self):
        do_without_fail(lambda: self.control.release(database_name))
        self.control.lock(database_name)
        with self.assertRaises(OperationalError):
            self.control.lock(database_name)
        self.control.release(database_name)

    def test_release(self):
        do_without_fail(lambda: self.control.release(database_name))
        do_without_fail(lambda: self.control.lock(database_name))
        self.assertTrue(self.control.release(database_name))
        self.assertRaises(OperationalError, self.control.release, database_name)

    @unittest.skipUnless(FULL_TEST, "full test disabled")
    def test_status(self):
        status = self.control.status(database_name)
        self.assertEqual(status["name"], database_name)

    @unittest.skipUnless(FULL_TEST, "full test disabled")
    def test_statuses(self):
        status1 = database_prefix + "status1"
        status2 = database_prefix + "status2"
        do_without_fail(lambda: self.control.destroy(status1))
        do_without_fail(lambda: self.control.destroy(status2))
        self.control.create(status1)
        self.control.create(status2)
        statuses = self.control.status()
        self.assertTrue(status1 in [status["name"] for status in statuses])
        self.assertTrue(status2 in [status["name"] for status in statuses])
        do_without_fail(lambda: self.control.destroy(status1))
        do_without_fail(lambda: self.control.destroy(status2))

    def test_start(self):
        do_without_fail(lambda: self.control.stop(database_name))
        self.assertTrue(self.control.start(database_name))

    @unittest.skipUnless(FULL_TEST, "full test disabled")
    def test_stop(self):
        do_without_fail(lambda: self.control.start(database_name))
        self.assertTrue(self.control.stop(database_name))

    @unittest.skipUnless(FULL_TEST, "full test disabled")
    def test_kill(self):
        do_without_fail(lambda: self.control.start(database_name))
        self.assertTrue(self.control.kill(database_name))

    def test_set(self):
        property_ = "readonly"
        value = "yes"
        self.control.set(database_name, property_, value)
        properties = self.control.get(database_name)
        self.assertEqual(properties[property_], value)

    def test_get(self):
        self.control.get(database_name)

    def test_inherit(self):
        self.control.set(database_name, "readonly", "yes")
        self.assertTrue("readonly" in self.control.get(database_name))
        self.control.inherit(database_name, "readonly")
        # TODO: False on OSX, True on travis?
        #self.assertTrue("readonly" in self.control.get(database_name))

    def test_rename(self):
        old = database_prefix + "old"
        new = database_prefix + "new"
        do_without_fail(lambda: self.control.destroy(old))
        do_without_fail(lambda: self.control.destroy(new))
        self.control.create(old)
        self.control.rename(old, new)
        statuses = self.control.status()
        self.assertTrue(new in [status["name"] for status in statuses])
        do_without_fail(lambda: self.control.destroy(new))

    def test_defaults(self):
        defaults = self.control.defaults()
        self.assertTrue("readonly" in defaults)

    @unittest.skipUnless(FULL_TEST, "full test disabled")
    def test_neighbours(self):
        self.control.neighbours()

if __name__ == '__main__':
    unittest.main()
