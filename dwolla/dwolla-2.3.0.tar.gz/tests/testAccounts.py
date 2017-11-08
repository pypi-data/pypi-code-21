import unittest

from dwolla import accounts, constants
from mock import MagicMock


class AccountsTest(unittest.TestCase):
    def setUp(self):
        accounts.r._get = MagicMock()
        accounts.r._get_without_token = MagicMock()
        accounts.r._post = MagicMock()
        accounts.r._post_without_token = MagicMock()
        constants.client_id = "SOME ID"
        constants.client_secret = "SOME ID"
        constants.access_token = "AN OAUTH TOKEN"

    def testbasic(self):
        accounts.basic('123456', dwollaparse='dwolla')
        accounts.r._get_without_token.assert_any_call('/users/123456', {'client_secret': 'SOME ID', 'client_id': 'SOME ID'}, {'dwollaparse': 'dwolla'})

    def testfull(self):
        accounts.full(alternate_token='AN OAUTH TOKEN', dwollaparse='dwolla')
        accounts.r._get.assert_any_call('/users', {}, {'alternate_token':'AN OAUTH TOKEN', 'dwollaparse':'dwolla'})

    def testbalance(self):
        accounts.balance(alternate_token='AN OAUTH TOKEN', dwollaparse='dwolla')
        accounts.r._get.assert_any_call('/balance', {}, {'alternate_token':'AN OAUTH TOKEN', 'dwollaparse':'dwolla'})

    def testnearby(self):
        accounts.nearby(45, 50, dwollaparse='dwolla')
        accounts.r._get_without_token.assert_any_call('/users/nearby', {'latitude': 45, 'client_secret': 'SOME ID', 'longitude': 50, 'client_id': 'SOME ID'}, {'dwollaparse': 'dwolla'})

    def testautowithdrawalstatus(self):
        accounts.autowithdrawalstatus(alternate_token='AN OAUTH TOKEN', dwollaparse='dwolla')
        accounts.r._get.assert_any_call('/accounts/features/auto_withdrawl', {}, {'alternate_token':'AN OAUTH TOKEN', 'dwollaparse':'dwolla'})

    def testtoggleautowithdrawalstatus(self):
        accounts.toggleautowithdrawalstatus(True, '123456', alternate_token='AN OAUTH TOKEN', dwollaparse='dwolla')
        accounts.r._post.assert_any_call('/accounts/features/auto_withdrawl', {'enabled': True, 'fundingId': '123456'}, {'alternate_token':'AN OAUTH TOKEN', 'dwollaparse':'dwolla'})


if __name__ == '__main__':
    unittest.main()