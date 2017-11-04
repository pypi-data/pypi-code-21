import unittest

from velenxc.utils.crypto import Crypt, ChineseCoding


class CryptTestCase(unittest.TestCase):
    def test_md5_should_return_correctly_even_if_input_is_incorrect(self):
        crypt = Crypt()
        self.assertEqual(len(crypt.md5('我们都是牛人'.encode())), 32)

    def test_md5_should_return_utf8_str(self):
        crypt = Crypt()
        payload = '123456'
        md5_result = crypt.md5(payload)
        md5_result_utf8 = crypt.md5(payload.encode('utf-8').decode('utf-8'))
        self.assertEqual(md5_result, md5_result_utf8)

    def test_md5_should_return_only_utf8_str(self):
        crypt = Crypt()
        payload = '中文'
        md5_result = crypt.md5(payload)
        md5_result_non_utf8 = crypt.md5(payload.encode('big5').decode('big5'))
        self.assertEqual(md5_result, md5_result_non_utf8)

    def test_md5_should_return_256_bits(self):
        crypt = Crypt()
        self.assertEqual(len(crypt.md5('123456556')), 32)
        self.assertEqual(len(crypt.md5('1')), 32)
        self.assertEqual(len(crypt.md5('我们都是牛人！')), 32)

    def test_aes_base64_encrypt_should_return_encrypt_string(self):
        self.assertEqual(Crypt.aes_base64_encrypt('{"grant_type": "client_credentials", "client_secret": "kXXNuP6IOMYr'
                                                  '5WxhZihef4Ub6QbOFRPglX0WPPZ5D2sAydh3vDZTCvuMGRFAwlJcu3LoqlQuzs60XE7'
                                                  '2mxlisrZfhW2DGGCjUHJojkPhiouYrjKrkBj357ThuC61qupk"}',
                                                  'sjdguhcphysghcih').decode(),
                         '2jyl7NpoGelBLKxzY/WZ3JqFpWlxadcxnODYkv2VrS8YHLhzU/J8aD9oOgD/ghYd+WQkZmbjWVsY4kL5w8oidZ7Evm7t'
                         'WuN+Fp521+UYNMZW9jZ5bA0K1LXfGIzXMKVyv4/vpVS8nDJeN6EwvAJZRhGu/px+Qi65eXfpPfSlojzyc+w3aavfd+bb'
                         'MvFtKeZNcXb4fTpvWd/oekddaCMINaRBG1GKa0CMTgQh7G5LbT2KJoU+lsuo8EXrE/s8T/TH')

    def test_pkcs5_padding_should_return_padding_string(self):
        self.assertEqual(Crypt.pkcs5_padding('syph'), 'syph'.encode())

    def test_aes_base64_decrypt_should_return_decrypt_string(self):
        self.assertEqual(Crypt.aes_base64_decrypt('QhXJ9KgcbDg9HclRNM8qSZBYBSfBexbU2qn50itjBAOxV4ZwRH3gLfM1qp/zV6cgS1'
                                                  '8GgPMgUt7R/ckGA9WthidY8/a89hHpX2HSPiWKGHNgpB9PS09c+silIvu9HXMzBecb'
                                                  'ayyTOL3mkpfcw85mVDtgCZX9lOpuyMGtDhYXG+k=',
                                                  'sjdguhcphysghcih'),
                         '{"access_token": "X65ODhmqoOvRuhoT83MqNostoGfxzC", "token_type": "Bearer", "expires_in": 600,'
                         ' "scope": "read write"}')

    def test_aes_base64_decrypt_should_return_none(self):
        self.assertIsNone(Crypt.aes_base64_decrypt('', ''))

    def test_pkcs5_eliminate_padding_should_eliminate_padding_string(self):
        self.assertEqual(Crypt.pkcs5_eliminate_padding('syph'), 'syph')


class ChineseCodingTestCase(unittest.TestCase):
    """ Test case """

    def test_check_chinese_return_true(self):
        check_res = ChineseCoding.check_chinese('轻轻的你走了ma')
        check_res2 = ChineseCoding.check_chinese('aaa中 dei()*32')

        self.assertTrue(True in (check_res, check_res2))

    def test_check_chinese_return_false(self):
        check_res = ChineseCoding.check_chinese('womeiyouzhognwen')
        check_res2 = ChineseCoding.check_chinese('123USY weu *(@(@##')

        self.assertTrue(True not in (check_res, check_res2, ))
