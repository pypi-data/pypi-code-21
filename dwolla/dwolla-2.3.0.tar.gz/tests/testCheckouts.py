import unittest
from dwolla import checkouts, constants
from mock import MagicMock


class CheckoutsTest(unittest.TestCase):
    def setUp(self):
        checkouts.r._get_without_token = MagicMock()
        checkouts.r._post_without_token = MagicMock()

        checkouts.r._post_without_token.return_value = dict({'CheckoutId': 'TEST'})

        constants.client_id = "SOME ID"
        constants.client_secret = "SOME ID"
        constants.access_token = "AN OAUTH TOKEN"
        constants.pin = 1234

    def testcreate(self, dwollaparse='dwolla'):
        checkouts.create({
            'orderItems': {
                frozenset({
                    'name': 'Prime Rib Sandwich',
                    'description': 'A somewhat tasty non-vegetarian sandwich',
                    'quantity': '1',
                    'price': '15.00'
                })
            },
            'destinationId': '812-740-4294',
            'total': 15.00,
            'notes': 'blahhh',
            'metadata': frozenset({
                'key1': 'something',
                'key2': 'another thing'
            })}, dwollaparse='dwolla')
        checkouts.r._post_without_token.assert_any_call('/offsitegateway/checkouts', {'client_secret': 'SOME ID', 'purchaseOrder': {'destinationId': '812-740-4294', 'total': 15.0, 'notes': 'blahhh', 'orderItems': set([frozenset(['price', 'description', 'name', 'quantity'])]), 'metadata': frozenset(['key2', 'key1'])}, 'client_id': 'SOME ID'}, {'dwollaparse': 'dwolla'})

    def testget(self):
        checkouts.get('123456', dwollaparse='dwolla')
        checkouts.r._get_without_token.assert_any_call('/offsitegateway/checkouts/123456', {'client_secret': 'SOME ID', 'client_id': 'SOME ID'}, {'dwollaparse':'dwolla'})

    def testcomplete(self):
        checkouts.complete('123456', dwollaparse='dwolla')
        checkouts.r._get_without_token.assert_any_call('/offsitegateway/checkouts/123456/complete', {'client_secret': 'SOME ID', 'client_id': 'SOME ID'}, {'dwollaparse':'dwolla'})

if __name__ == '__main__':
    unittest.main()