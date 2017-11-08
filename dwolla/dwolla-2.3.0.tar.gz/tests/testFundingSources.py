import unittest

from dwolla import fundingsources, constants
from mock import MagicMock


class FundingSourcesTest(unittest.TestCase):
    def setUp(self):
        fundingsources.r._get = MagicMock()
        fundingsources.r._post = MagicMock()
        constants.client_id = "SOME ID"
        constants.client_secret = "SOME ID"
        constants.access_token = "AN OAUTH TOKEN"
        constants.pin = 1234

    def testinfo(self):
        fundingsources.info('123456', alternate_token='AN OAUTH TOKEN', dwollaparse='dwolla')
        fundingsources.r._get.assert_any_call('/fundingsources/123456', {}, {'alternate_token':'AN OAUTH TOKEN', 'dwollaparse':'dwolla'})

    def testget(self):
        fundingsources.get(a='parameter', alternate_token='AN OAUTH TOKEN', dwollaparse='dwolla')
        fundingsources.r._get.assert_any_call('/fundingsources', {'a': 'parameter'}, {'alternate_token':'AN OAUTH TOKEN', 'dwollaparse':'dwolla'})

    def testadd(self):
        fundingsources.add('123456', '654321', 'Checking', 'Unit Test Bank', alternate_token='AN OAUTH TOKEN', dwollaparse='dwolla')
        fundingsources.r._post.assert_any_call('/fundingsources', {'routing_number': '654321', 'account_type': 'Checking', 'account_number': '123456', 'account_name': 'Unit Test Bank'}, {'alternate_token':'AN OAUTH TOKEN', 'dwollaparse':'dwolla'})

    def testverify(self):
        fundingsources.verify(0.03, 0.02, '123456', alternate_token='AN OAUTH TOKEN', dwollaparse='dwolla')
        fundingsources.r._post.assert_any_call('/fundingsources/123456', {'deposit2': 0.02, 'deposit1': 0.03}, {'alternate_token':'AN OAUTH TOKEN', 'dwollaparse':'dwolla'})

    def testwithdraw(self):
        fundingsources.withdraw(20.50, '123456', alternate_token='AN OAUTH TOKEN', dwollaparse='dwolla')
        fundingsources.r._post.assert_any_call('/fundingsources/123456/withdraw', {'amount': 20.5, 'pin': 1234}, {'alternate_token':'AN OAUTH TOKEN', 'dwollaparse':'dwolla'})

    def testdeposit(self):
        fundingsources.deposit(30.50, '123456', alternate_token='AN OAUTH TOKEN', dwollaparse='dwolla')
        fundingsources.r._post.assert_any_call('/fundingsources/123456/deposit', {'amount': 30.5, 'pin': 1234}, {'alternate_token':'AN OAUTH TOKEN', 'dwollaparse':'dwolla'})


if __name__ == '__main__':
    unittest.main()
