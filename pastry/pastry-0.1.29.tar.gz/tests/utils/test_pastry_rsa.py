import mock
import unittest

from pastry.utils.pastry_rsa import sign


class PastryRsaTestCase(unittest.TestCase):

    @mock.patch('pastry.utils.pastry_rsa.rsa')
    def test_sign(self, rsa):
        private = mock.MagicMock()
        private.n = 'n'
        private.d = 'd'
        rsa.PrivateKey.load_pkcs1.return_value = private
        rsa.common.byte_size.return_value = 'byte_size'
        rsa.pkcs1._pad_for_signing.return_value = 'padded'
        rsa.transform.bytes2int.return_value = 'payload'
        rsa.core.encrypt_int.return_value = 'encrypted'
        rsa.transform.int2bytes.return_value = 'int2bytes'
        self.assertEqual('int2bytes', sign('message', 'key'))
        rsa.PrivateKey.load_pkcs1.assert_called_with('key')
        rsa.common.byte_size.assert_called_with('n')
        rsa.pkcs1._pad_for_signing.assert_called_with('message', 'byte_size')
        rsa.transform.bytes2int.assert_called_with('padded')
        rsa.core.encrypt_int.assert_called_with('payload', 'd', 'n')
        rsa.transform.int2bytes.assert_called_with('encrypted', 'byte_size')
