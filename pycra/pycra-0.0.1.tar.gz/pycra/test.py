from unittest import TestCase
from pycra.core import create_challenge, calculate_answer, auth_check, calculate_answer_for_pbkdf2
import pbkdf2helper

# Example Models for Testing


class ClientUser(object):
    """
    My Test Client User Model
    """

    def __init__(self, username, password):
        self.username = username
        self.password = password
        self.cnonce = '' # TODO
        self.psk = '' # TODO


class ServerUser(object):
    """
    My Test Sever User Model
    """

    def __init__(self, username, password):
        self.username = username
        self.password = password
        self.nonce = ''
        self.cnonce = ''
        self.psk = ''


class CRATest(TestCase):

    def setUp(self):
        # 0. Init User Credentials

        # user with password in plaintext
        self.serverUser1 = ServerUser(password="secret",
                                      username="kungalex")
        self.clientUser1 = ClientUser(password="secret",
                                      username="kungalex")

        # user with PBKDF2 hashed password (only on Server)
        self.serverUser2 = ServerUser(password=pbkdf2helper.encode("secret", pbkdf2helper.generate_salt(12),1000),
                                      username="kungalex-with-hashed-pw")
        self.clientUser2 = ClientUser(password="secret",
                                      username="kungalex-with-hashed-pw")

    def test_init_plain_passwords(self):
        self.assertEqual(self.serverUser1.username, self.clientUser1.username)
        self.assertEqual(self.serverUser1.password, self.clientUser1.password)

    def test_init_hashed_passwords(self):
        self.assertEqual(self.serverUser2.username, self.clientUser2.username)
        self.assertNotEqual(self.serverUser2.password, self.clientUser2.password)

        algorithm, iterations, salt, h = pbkdf2helper.split(self.serverUser2.password)
        self.assertEqual("sha256", algorithm)

    def test_auth_with_plain_stored_passwords(self):

        # 1. client -> Server POST:{username}
        # ... simulation

        # 2. on Server: create challenge
        challenge = create_challenge(self.serverUser1)
        self.serverUser1.nonce = challenge
        self.assertNotEqual("", self.serverUser1.nonce)

        # 3. Server -> client  response: {challenge}
        # ... simulation

        # 4. on Client calculate answer = HMAC(challenge+password)
        response = calculate_answer(self.serverUser1.nonce, self.clientUser1.password)

        # 5. client -> Server POST: {response}
        # ... simulation

        # 6. on Server: calculate answer = HMAC(challenge+password) and compare digest(answer, response)
        is_auth = auth_check(self.serverUser1, response)
        self.assertTrue(is_auth)

    def test_auth_with_hashed_passwords(self):

        # 1. client -> Server POST:{username}
        # ... simulation

        # 2. on Server: create challenge
        challenge = create_challenge(self.serverUser2)
        self.serverUser2.nonce = challenge
        self.assertNotEqual("", self.serverUser2.nonce)
        algorithm, iterations, salt, h = pbkdf2helper.split(self.serverUser2.password)
        self.assertEqual("sha256", algorithm)

        # 3. Server -> client  response: {challenge}
        # ... simulation

        # 4. on Client calculate answer = HMAC(challenge+password hash)

        response = calculate_answer_for_pbkdf2(challenge, self.clientUser2.password, algorithm, salt, iterations)

        # 5. client -> Server POST: {response}
        # ... simulation

        # 6. on Server: calculate answer = HMAC(challenge+password) and compare digest(answer, response)
        is_auth = auth_check(self.serverUser2, response)
        self.assertTrue(is_auth)

