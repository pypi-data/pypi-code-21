import unittest

from dwolla import transactions, constants
from mock import MagicMock


class TransTest(unittest.TestCase):
    def setUp(self):
        transactions.r._get = MagicMock()
        transactions.r._post = MagicMock()
        transactions.r._put = MagicMock()
        transactions.r._delete = MagicMock()

        constants.client_id = "SOME ID"
        constants.client_secret = "SOME ID"
        constants.access_token = "AN OAUTH TOKEN"
        constants.pin = 1234

    def testsend(self):
        transactions.send('812-111-1234', 5.00, a='parameter', alternate_token='AN OAUTH TOKEN', dwollaparse='dwolla')
        transactions.r._post.assert_any_call('/transactions/send', {'a': 'parameter', 'destinationId': '812-111-1234', 'amount': 5.0, 'pin': 1234}, {'alternate_token':'AN OAUTH TOKEN', 'dwollaparse':'dwolla'})

    def testget(self):
        transactions.get(another='parameter', alternate_token='AN OAUTH TOKEN', dwollaparse='dwolla')
        transactions.r._get.assert_any_call('/transactions', {'client_secret': 'SOME ID', 'another': 'parameter', 'client_id': 'SOME ID'}, {'alternate_token':'AN OAUTH TOKEN', 'dwollaparse':'dwolla'})

    def testinfo(self):
        transactions.info('123456', alternate_token='AN OAUTH TOKEN', dwollaparse='dwolla')
        transactions.r._get.assert_any_call('/transactions/123456', {'client_secret': 'SOME ID', 'client_id': 'SOME ID'}, {'alternate_token':'AN OAUTH TOKEN', 'dwollaparse':'dwolla'})

    def testrefund(self):
        transactions.refund('12345', 'Balance', 10.50, a='parameter', alternate_token='AN OAUTH TOKEN', dwollaparse='dwolla')
        transactions.r._post.assert_any_call('/transactions/refund', {'fundsSource': 'Balance', 'a': 'parameter', 'pin': 1234, 'amount': 10.5, 'transactionId': '12345'}, {'alternate_token':'AN OAUTH TOKEN', 'dwollaparse':'dwolla'})

    def teststats(self):
        transactions.stats(a='parameter', alternate_token='AN OAUTH TOKEN', dwollaparse='dwolla')
        transactions.r._get.assert_any_call('/transactions/stats', {'a': 'parameter'}, {'alternate_token':'AN OAUTH TOKEN', 'dwollaparse':'dwolla'})

    def testschedule(self):
        transactions.schedule('812-111-1234', 5.00, '2018-01-01', 'abcdefunds', a='parameter', alternate_token='AN OAUTH TOKEN', dwollaparse='dwolla')
        transactions.r._post.assert_any_call('/transactions/scheduled', {'a': 'parameter', 'destinationId': '812-111-1234', 'amount': 5.0, 'scheduleDate': '2018-01-01', 'pin': 1234, 'fundsSource': 'abcdefunds'}, {'alternate_token':'AN OAUTH TOKEN', 'dwollaparse':'dwolla'})

    def testscheduled(self):
        transactions.scheduled(alternate_token='AN OAUTH TOKEN', dwollaparse='dwolla')
        transactions.r._get.assert_any_call('/transactions/scheduled', {}, {'alternate_token':'AN OAUTH TOKEN', 'dwollaparse':'dwolla'})

    def testscheduledbyid(self):
        transactions.scheduledbyid('1234', alternate_token='AN OAUTH TOKEN', dwollaparse='dwolla')
        transactions.r._get.assert_any_call('/transactions/scheduled/1234', {}, {'alternate_token':'AN OAUTH TOKEN', 'dwollaparse':'dwolla'})

    def testeditscheduledbyid(self):
        transactions.editscheduledbyid('1234', amount=5.5, alternate_token='AN OAUTH TOKEN', dwollaparse='dwolla')
        transactions.r._put.assert_any_call('/transactions/scheduled/1234', {'amount': 5.5, 'pin': 1234}, {'alternate_token':'AN OAUTH TOKEN', 'dwollaparse':'dwolla'})

    def testdeletescheduledbyid(self):
        transactions.deletescheduledbyid('1234', alternate_token='AN OAUTH TOKEN', dwollaparse='dwolla')
        transactions.r._delete.assert_any_call('/transactions/scheduled/1234', {'pin': 1234}, {'alternate_token':'AN OAUTH TOKEN', 'dwollaparse':'dwolla'})

    def testdeleteallscheduled(self):
        transactions.deleteallscheduled(alternate_token='AN OAUTH TOKEN', dwollaparse='dwolla')
        transactions.r._delete.assert_any_call('/transactions/scheduled', {'pin': 1234}, {'alternate_token':'AN OAUTH TOKEN', 'dwollaparse':'dwolla'})

if __name__ == '__main__':
    unittest.main()
