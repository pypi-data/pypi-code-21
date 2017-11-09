import time
import json
import uuid
import base64
from descrypt import encrypter, decrypter, IDENTIFIER
import arrow

TEST_SECRET = 'XBWf3i,#Vk9x|fde(HG8(j'
class Token(object):
    SECRET = TEST_SECRET

    @classmethod
    def generator(cls, user_id, username, expire_date = None, secret = None, token = None):
        if expire_date == None:
            expire_date = Time.datetime_to_epoch(input_time=Time.offset_time(input_time=Time.now(type="datetime"), step_size="week", multiple=1)) # expire a week from generation

        if secret == None:
            secret = cls.SECRET

        if token == None:
            token = str(uuid.uuid4())[0:10]

        key = dict(token = token, expire_date = expire_date, username = username, user_id = user_id)
        key = json.dumps(key)

        encrypted_key = encrypter(key, des_key = secret)
        encrypted_key = encrypted_key[len(IDENTIFIER):]

        encoded_key = base64.b64encode(encrypted_key, altchars=None)
        return encoded_key

    @classmethod
    def degenerator(cls, astr, secret = None):
        if secret == None:
            secret = cls.SECRET

        try:
            unencoded_key = base64.decodestring(astr)
            encrypted_key = IDENTIFIER + unencoded_key
            decrypted_key = decrypter(encrypted_key, des_key = secret)
            key = json.loads(decrypted_key)
        except:
            raise Exception('Invalid Token.  Malformed:m')

        return key

    @classmethod
    def authenticate(cls, astr, secret = None, token = None):
        key = cls.degenerator(astr = astr, secret = secret)

        expire_date = key.get('expire_date', None)
        if expire_date == None:
            raise Exception('Invalid Token.  Malformed:e')

        key_token = key.get('auth_token', None)
        if key_token == None:
            raise Exception('Invalid Token.  Malformed:k')

        if token and key_token != token:
            raise Exception('Invalid Token.  Fail check.')

        return key

if __name__ == '__main__':
    a = Token.generator(user_id = 1, username = 'test12')
    print(a)
    print(len(a))
#     b = Token.degenerator(a + 'asdf')
#     print(b)
    c = Token.authenticate(a)
    print(c)

