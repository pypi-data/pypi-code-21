# coding: utf-8
from unittest import TestCase
import swutils.encrypt

class EncryptTestCase(TestCase):

    def test_encrypt_decrypt(self):
        key = 'SuperPass123'
        value = 'Test string for encrypting.'

        encrypted_value = swutils.encrypt.encrypt(value, key)
        self.assertNotEquals(value, encrypted_value)

        decrypted_value = swutils.encrypt.decrypt(encrypted_value, key)
        self.assertNotEquals(decrypted_value, encrypted_value)
        self.assertEquals(value, decrypted_value)
