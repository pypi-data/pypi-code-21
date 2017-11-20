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
import logging
import sqlite3
from kudubot.users.Contact import Contact


# noinspection SqlDialectInspection,SqlNoDataSourceInspection,SqlResolve
class AddressBook(object):
    u"""
    Class that tracks and provides user information
    in the connection's database.

    The address book uses the following database schema:

    |id|display_name|address|
    """

    logger = logging.getLogger(__name__)
    u"""
    The Logger for this class
    """

    def __init__(self, database):
        u"""
        Initializes the address book. Makes sure that the
        address book's database table exists and has the correct schema

        :param database: The database connection to use
        """
        self.db = database
        self.db.execute(
             u"CREATE TABLE IF NOT EXISTS address_book ("
             u"    id INTEGER CONSTRAINT constraint_name PRIMARY KEY,"
             u"    display_name VARCHAR(255) NOT NULL,"
             u"    address VARCHAR(255) NOT NULL"
             u")"
        )
        self.db.commit()
        self.logger.info(u"Address Book initialized")

    def add_or_update_contact(self, contact,
                              database_override = None):
        u"""
        Adds or updates a contact in the address book

        :param contact: The contact to insert/update
        :param database_override: Can be specified to use a different
                                  database connection, useful for calling this
                                  method from a different thread
        :return: The contact, possibly with an altered id value
                 (in case the contact was inserted, not updated)
        """
        db = self.db if database_override is None else database_override
        # Check if the contact currently exists
        old = db.execute(
            u"SELECT id FROM address_book WHERE id=? OR address=?",
            (contact.database_id, contact.address)).fetchall()

        if len(old) > 0:
            db.execute(
                u"UPDATE address_book SET display_name=?, address=? WHERE id=?",
                (contact.display_name, contact.address, old[0][0]))
        else:
            db.execute(
                u"INSERT INTO address_book "
                u"(display_name, address) VALUES (?, ?)",
                (contact.display_name, contact.address))

        db.commit()
        contact.database_id = \
            db.execute(u"SELECT id FROM address_book WHERE address=?",
                       (contact.address,)).fetchall()[0][0]
        return contact

    def get_contact_for_address(self, address,
                                database_override = None):
        u"""
        Generates a Contact object for an address in the address book table.

        :param address: The address to look for
        :param database_override: Can be specified to use a different
                                  database connection, useful for calling this
                                  method from a different thread
        :return: The Contact object, or None if no contact was found
        """
        db = self.db if database_override is None else database_override
        result = db.execute(u"SELECT * FROM address_book WHERE address=?",
                            (address,)).fetchall()

        if len(result) != 1:
            # noinspection PyTypeChecker
            return None
        else:
            data = result[0]
            return Contact(int(data[0]), unicode(data[1]), unicode(data[2]))

    def get_contact_for_id(self, user_id,
                           database_override = None):
        u"""
        Generates a Contact object for a user ID in the address book table

        :param user_id: The user's ID
        :param database_override: Can be specified to use a different
                                  database connection, useful for calling this
                                  method from a different thread
        :return: The user as a Contact object
        """
        db = self.db if database_override is None else database_override
        result = db.execute(u"SELECT * FROM address_book WHERE id=?",
                            (user_id,)).fetchall()

        if len(result) != 1:
            # noinspection PyTypeChecker
            return None
        else:
            data = result[0]
            return Contact(int(data[0]), unicode(data[1]), unicode(data[2]))
