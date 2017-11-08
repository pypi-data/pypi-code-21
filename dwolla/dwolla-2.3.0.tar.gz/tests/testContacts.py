import unittest

from dwolla import contacts, constants
from mock import MagicMock


class ContactsTest(unittest.TestCase):
    def setUp(self):
        contacts.r._get = MagicMock()
        contacts.r._post = MagicMock()
        contacts.r._get_without_token = MagicMock()
        constants.client_id = "SOME ID"
        constants.client_secret = "SOME ID"
        constants.access_token = "AN OAUTH TOKEN"

    def testget(self):
        contacts.get(a='parameter', alternate_token='AN OAUTH TOKEN', dwollaparse='dwolla')
        contacts.r._get.assert_any_call('/contacts', {'a': 'parameter'}, {'alternate_token': 'AN OAUTH TOKEN', 'dwollaparse':'dwolla'})

    def testnearby(self):
        contacts.nearby(45, 50, another='parameter', dwollaparse='dwolla')
        contacts.r._get_without_token.assert_any_call('/contacts/nearby', {'latitude': 45, 'client_secret': 'SOME ID', 'another': 'parameter', 'client_id': 'SOME ID', 'longitude': 50}, {'dwollaparse': 'dwolla'})

if __name__ == '__main__':
    unittest.main()