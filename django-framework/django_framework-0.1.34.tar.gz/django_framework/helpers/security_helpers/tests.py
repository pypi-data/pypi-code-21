
from nose.tools import assert_equal, assert_not_equal, assert_raises
from hasher_helpers import md5_hasher
from unique_key_helper import generate_unique_key
from token_helpers import Token


class TestMD5Hasher():

    def test_hashing(self):
        assert_equal( md5_hasher('test', saltz = None, label = True), "**md5$a9bcf77e337411d274a977f23822c31c")

    def test_default(self):
        assert_equal( md5_hasher('test', saltz = None), "a9bcf77e337411d274a977f23822c31c")

    def test_no_headers(self):
        assert_equal( md5_hasher('test', saltz = None, label = False), 'a9bcf77e337411d274a977f23822c31c')

    def test_different_salt(self):
        assert_equal( md5_hasher('test', saltz = 'blah!', label = False), 'a906f1a08ecc6196a91092af0c8870db')

class TestGenerateUniqueKey():

    def test_default_length(self):
        mykey = generate_unique_key(length = None, dashes = True, numbers_only = False)
        assert_equal( len(mykey), 32)

    def test_length5(self):
        mykey = generate_unique_key(length = 5, dashes = True, numbers_only = False)
        assert_equal( len(mykey), 5)

    def test_no_dashes(self):
        mykey = generate_unique_key(length = None, dashes = False, numbers_only = False)
        assert_equal( len(mykey), 32)
        assert_equal(mykey.find('-'),  -1)

    def test_numbers(self):
        mykey = generate_unique_key(numbers_only = True)
        assert_equal( len(mykey), 32)


class TestPasswordHasher():

    def test_password_hasher(self):
        password = password_hasher(password = "blahblah")
        assert_equal(password, '1ab28a3a3197a53df362c7adb81fd0c9')

    def test_password_hasher2(self):
        password = password_hasher(password = "**md5$blahblah")
        assert_equal(password, "blahblah")

class TestToken():

    def test_generator(self):
        token = Token.generator(user_id = 'test', username = 'test', expire_date = 1234, secret = None, token = '1')
        assert_equal(token, 'M2EzMjE1YWQ3ZWM3OWI4NDRhOGUwZmFlMWI1YTI2YWMxNjU2YjhiNDRjZDU3ODI5NGI0NmFiMmI0YTU5ODdjZTVkNzk5MjAxM2ZiMDA0ZTFiOTBjYzIzZjM0NmJhZDBiM2U4NDgxNGJkMGE5MWM2MDBhNTM5ZDQ4YmI0NTFiMDI0ZDEzODJiZjBlYWRhM2I1MGQ3OWYxZGY4MzQ5Njc0Yw==')

        token = Token.generator(user_id = 'test', username = 'test', expire_date = 1234, secret = 'None', token = '1')
        assert_equal(token, 'NmI2MjRjN2Q0OTBkM2VjZmJiY2YxOWJjZmMzOWVkMjFkZDE1YWQxZmQzYzJjZTlhYzQwM2ZmN2Q4Nzc1MWUzOTFiNmQxYTFjNjQwZjBjYjgwOTRjNjFiYTE2NTY3ZjJkNTJjN2IxMWYzOWYwNzVmZjRkMGMwNDQ1YWNiMzIxODBmMjExMDFjNWQxM2IzNTNkM2E5OThiZDUyYjJjZGQ2Mw==')


    def test_generator_blank(self):
        token = Token.generator(user_id = 'test', username = 'test')
        assert_equal(len(token), 256) # there are things that are generated each time!

    def test_token_degenerator(self):
        token = Token.generator(user_id = 'test', username = 'test', expire_date = 1234, secret = None, token = '1')

        token = Token.degenerator(token)
        assert_equal(token, {u'username': u'test', u'auth_token': u'1', u'user_id': u'test', u'expire_date': 1234}) # there are things that are generated each time!

    def test_token_degenerator_fail_secret1(self):
        token = Token.generator(user_id = 'test', username = 'test', expire_date = 1234, secret = None, token = '1')
        assert_raises(Exception, Token.degenerator, token = token, secret = 'test') # there are things that are generated each time!

    def test_token_degenerator_fail_secret2(self):
        token = Token.generator(user_id = 'test', username = 'test', expire_date = 1234, secret = 'test', token = '1')
        assert_raises(Exception, Token.degenerator, token = token, secret = None) # there are things that are generated each time!

    def test_token_authenticate(self):
        token = Token.generator(user_id = 'test', username = 'test', expire_date = 1437679562*5, secret = None, token = '1')

        token = Token.authenticate(astr = token, secret = None, token = '1')
        assert_equal(token, {u'username': u'test', u'auth_token': u'1', u'user_id': u'test', u'expire_date': 1437679562*5}) # there are things that are generated each time!

    def test_authenticate_fail_decode(self):
        token = Token.generator(user_id = 'test', username = 'test', expire_date = 1437679562*5, secret = None, token = '1')
        assert_raises(Exception, Token.authenticate, astr = token, secret = 'tessdfsdt') # there are things that are generated each time!

    def test_authenticate_fail_expire(self):
        token = Token.generator(user_id = 'test', username = 'test', expire_date = 1, secret = None, token = '1')
        print("This test is supposed to fail until we expire tokens again.")
        assert_raises(Exception, Token.authenticate, astr = token) # there are things that are generated each time!

    def test_authenticate_fail_token(self):
        token = Token.generator(user_id = 'test', username = 'test', expire_date = 1, secret = None, token = '1')
        print("This test currently fails as we think about our auth strategy.")
        assert_raises(Exception, Token.authenticate, astr = token, token = '2') # there are things that are generated each time!
