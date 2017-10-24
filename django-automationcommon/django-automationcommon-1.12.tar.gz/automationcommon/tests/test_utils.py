from collections import namedtuple

from django.contrib.auth.models import User
from django.test import TestCase
from mock import Mock, MagicMock

import automationcommon.utils as utils


class UtilsTests(TestCase):

    def setUp(self):

        def create_connection_fake():
            return None

        self.createConnection = utils.createConnection
        utils.createConnection = Mock(side_effect=create_connection_fake)

        self.PersonMethods_getPerson = utils.PersonMethods.getPerson

    def test_get_users_email_address_from_lookup(self):

        # named tuples to help with results
        Attributes = namedtuple('Attributes', 'attributes')
        Value = namedtuple('Value', 'value')

        # setup user where lookup fails
        user_none = User(username='jfk1000', last_name="John F Kennedy")
        utils.PersonMethods.getPerson = MagicMock(return_value=None)

        # test for full address
        result = utils.get_users_email_address_from_lookup(user_none)
        self.assertEqual(result, "John F Kennedy <jfk1000@cam.ac.uk>")

        # test for email only
        result = utils.get_users_email_address_from_lookup(user_none, True)
        self.assertEqual(result, "jfk1000@cam.ac.uk")

        # setup user where lookup success
        user_found = User(username='fsf1000', last_name="F Scott Fitzgerald")
        utils.PersonMethods.getPerson = MagicMock(return_value=Attributes(attributes=[Value(value="fsf1001@cam.ac.uk")]))

        # test for full address
        result = utils.get_users_email_address_from_lookup(user_found)
        self.assertEqual(result, "F Scott Fitzgerald <fsf1001@cam.ac.uk>")

        # test for email only
        result = utils.get_users_email_address_from_lookup(user_found, True)
        self.assertEqual(result, "fsf1001@cam.ac.uk")

    def test_paginate(self):
        Request = namedtuple('Request', 'GET')
        object_list = [1, 2, 3, 4, 5, 6, 7]
        # 1st page
        paginator = utils.paginate(Request(GET={}), object_list, 3)
        self.assertEqual(paginator[0], 1)
        self.assertEqual(paginator[2], 3)
        # last page
        paginator = utils.paginate(Request(GET={"page": 3}), object_list, 3)
        self.assertEqual(paginator[0], 7)
        # out of range (last page)
        paginator = utils.paginate(Request(GET={"page": 4}), object_list, 3)
        self.assertEqual(paginator[0], 7)

    def tearDown(self):
        utils.createConnection = self.createConnection
        utils.PersonMethods.getPerson = self.PersonMethods_getPerson
