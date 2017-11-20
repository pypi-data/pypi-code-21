u"""
Copyright 2015-2017 Hermann Krumrey

This file is part of kudubot.

kudubot is free software: you can redistribute it and/or modify
it under the terms of the GNU General Public License as published by
the Free Software Foundation, either version 3 of the License, or
(at your option) any later version.

kudubot is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
GNU General Public License for more details.

You should have received a copy of the GNU General Public License
along with kudubot.  If not, see <http://www.gnu.org/licenses/>.
"""

from __future__ import absolute_import
import unittest
from kudubot.users.Contact import Contact
from kudubot.tests.helpers.DummyConnection import DummyConnection
from kudubot.tests.helpers.test_config import generate_test_environment,\
    clean_up_test_environment


# noinspection SqlNoDataSourceInspection
class UnitTests(unittest.TestCase):
    u"""
    Class that tests the AddressBook class
    """

    def setUp(self):
        u"""
        Changes the class variables for testing and
        creates the testing directory

        :return: None
        """
        self.config_handler = generate_test_environment()
        self.connection = DummyConnection([], self.config_handler)
        self.connection.db.execute(u"DELETE FROM address_book")
        self.connection.db.commit()

    def tearDown(self):
        u"""
        Restores the class variables and deletes the testing directory

        :return: None
        """
        clean_up_test_environment()

    def test_invalid_contact_fetches(self):
        u"""
        Tests if the contact fetch methods return a None object
        if they fail to find a result

        :return: None
        """
        self.assertEqual(
            None,
            self.connection.address_book.get_contact_for_address(u"No_Address")
        )
        self.assertEqual(
            None, self.connection.address_book.get_contact_for_id(100)
        )

    def test_contact_operations(self):
        u"""
        Tests various contact operations in the addressbook.
        Uses subtest methods to make the tests a bit more readable

        :return: None
        """
        self.subtest_updating_contact()
        contact = self.connection.address_book.add_or_update_contact(
            Contact(-1, u"ABC", u"DEF")
        )
        self.assertEqual(contact.display_name, u"ABC")
        self.assertEqual(contact.database_id, 1)
        self.assertEqual(contact.address, u"DEF")
        self.subtest_fetching_contacts()

    def subtest_fetching_contacts(self):
        u"""
        Tests fetching the contact information from the database
        To be used at the end of the test_contact_operations method

        :return: None
        """
        address_contact = \
            self.connection.address_book.get_contact_for_address(u"DEF")
        id_contact = self.connection.address_book.get_contact_for_id(1)
        self.assertEqual(id_contact.display_name, address_contact.display_name)
        self.assertEqual(id_contact.database_id, address_contact.database_id)
        self.assertEqual(id_contact.address, address_contact.address)

    def subtest_updating_contact(self):
        u"""
        Tests Updating a contact

        :return: None
        """

        contact = Contact(-1, u"A", u"B")
        self.subtest_adding_contact_to_addressbook(contact)

        new_contact = Contact(1, u"ABC", u"DEF")
        self.connection.address_book.add_or_update_contact(new_contact)

        self.assertEqual(
            self.connection.address_book.get_contact_for_address(u"B"),
            None
        )
        new_inserted = \
            self.connection.address_book.get_contact_for_address(u"DEF")

        self.assertEqual(new_inserted.display_name, u"ABC")
        self.assertEqual(new_inserted.database_id, contact.database_id)
        self.assertEqual(new_inserted.address, u"DEF")

    def subtest_adding_contact_to_addressbook(self, contact):
        u"""
        Tests adding a contact to the addressbook

        :param contact: The contact to add
        :return: None
        """
        self.assertEqual(-1, contact.database_id)

        result = self.connection.address_book.add_or_update_contact(contact)

        self.assertEqual(1, result.database_id)

        self.assertEqual(contact.display_name, result.display_name)
        self.assertEqual(contact.address, result.address)

        inserted = self.connection.address_book.get_contact_for_address(u"B")
        self.assertEqual(inserted.display_name, result.display_name)
        self.assertEqual(inserted.database_id, result.database_id)
        self.assertEqual(inserted.address, result.address)
