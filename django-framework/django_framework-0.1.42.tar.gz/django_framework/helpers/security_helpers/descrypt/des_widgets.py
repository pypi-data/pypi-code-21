import des_encryption
import uuid

IDENTIFIER = '**DES**' # you really don't ever want to change this.  EVER.
KEY = 'D0N7Ch@ng3me'
IV = 'L1kE4R3@lz'


STATIC_IV = 'tton3*cAfux8zqzBFw_eCJjZiZQoOHsM'
SALT_LENGTH = 32
def get_uuid():
    s = str(uuid.uuid4())
    s = s.replace('-', '')[0:SALT_LENGTH]
    return s


def encrypter(astr, des_key, iv = None):
    '''encrypts a value based on the key and iv'''
    
    if des_key is None:
        raise IOError('des_key must be provided')
    
    if iv == None:
        iv = get_uuid()
    elif iv == 'static':
        iv = STATIC_IV
    
    if is_already_encrypted(astr) == False:
        value = iv + str(astr)
        astr =  des_encryption.encrypt(des_key, iv, value)

    return IDENTIFIER + iv + astr

def decrypter(astr, des_key, iv = None):
    '''decrypts avalue based on the key and iv'''

    if des_key is None:
        raise IOError('des_key must be provided')

    if iv == None:
        iv_length = SALT_LENGTH
    elif iv == 'static':
        iv_length = len(STATIC_IV)
    else:
        iv_length = len(iv)
        
    

    if is_already_encrypted(astr) == True:
        iv_value = str(astr[len(IDENTIFIER):])

        iv = iv_value[0:iv_length]
        value = iv_value[iv_length:]
        astr = des_encryption.decrypt(des_key, iv, value)
        astr = astr[iv_length : ]
    return astr

def is_already_encrypted(value):
    '''Check to see if the value is already encrypted using personal DES encryption scheme'''
    try:
        return value[0:len(IDENTIFIER)] == IDENTIFIER
    except Exception, e:
        return False


if __name__ == '__main__': # pragma: no cover
    key = 'now i shoudl be able to ' # pragma: no cover
#     iv = 'as' # pragma: no cover

    encrypt_me = 'weaskdjfalskdfjalskfdjasdfj;alsfjall..' # pragma: no cover
    mystr = encrypter(encrypt_me, key) # pragma: no cover

    print(mystr) # pragma: no cover

    dec = decrypter(mystr, key) # pragma: no cover
    print(dec) # pragma: no cover
    assert(encrypt_me == dec) # pragma: no cover


