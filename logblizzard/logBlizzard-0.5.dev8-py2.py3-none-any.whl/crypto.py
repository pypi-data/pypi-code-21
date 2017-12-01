import base64
import os
from cryptography.fernet import Fernet
from cryptography.hazmat.backends import default_backend
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC

class Crypto:
    '''main crypto module for message encryption and decryption'''
    def_password='password'

    def __init__(self,dcdmsg,password):
        self.dcdmsg=dcdmsg
        self.password=password


    def DecryptMsg(dcdmsg,password):
        '''uses read values from both salt file and pwf file
         to perform Fernet encryption'''

        password = bytes(password,"ascii")
        try:
            saltf = open('salt','r')
            salt=saltf.read()
            salt=bytes(salt,"ascii")
            saltf.close()
        except:
            print("Recieved message and can't decode. It appears there is no salt file.\n")
            salt_dec=input("Would you like to create one (Y) or manually import an existing file (N)?:")
            if salt_dec == 'Y':
                saltf = open('salt','w')
                salt = os.urandom(64)
                salt_st=str(salt)
                saltlen=len(salt_st)
                first=2
                last=saltlen-1
                salt_st=(salt_st[first:last])
                saltf.write(salt_st)
                saltf.close()

            else:
                print("Program exiting. Please include 'salt' file in the main program directory with the correct hash.")
                sys.exit()

        kdf = PBKDF2HMAC(
         algorithm=hashes.SHA256(),
         length=32,
         salt=salt,
         iterations=100000,
         backend=default_backend()
        )
        key = base64.urlsafe_b64encode(kdf.derive(password))
        fk = Fernet(key)
        try:
            dcdmsg = fk.decrypt(dcdmsg)
            dcdmsg = dcdmsg.decode("ascii")
            return dcdmsg
        except:
            print("Invalid Encrypted or Unencrypted Message Recieved, can't decode")
            print("Peer salt file and passwords must match.")
            pass

    def EncryptMsg(msg,password):
        '''uses read values from both salt file and pwf file
        to perform Fernet encryption'''

        password = bytes(password,"ascii")
        try:
            saltf = open('salt','r')
            salt=saltf.read()
            salt=bytes(salt,"ascii")
            saltf.close()
        except:
            print("It appears there is no salt file.\n")
            salt_dec=input("Would you like to create one (Y) or manually import an existing file (N)")
            if salt_dec == 'Y':
                saltf = open('salt','w')
                salt = os.urandom(64)
                salt_st=str(salt)
                saltlen=len(salt_st)
                first=2
                last=saltlen-1
                salt_st=(salt_st[first:last])
                saltf.write(salt_st)
                saltf.close()

            else:
                print("Program exiting. Please include 'salt' file in the main program directory with the correct hash.")
                sys.exit()

        kdf = PBKDF2HMAC(
         algorithm=hashes.SHA256(),
         length=32,
         salt=salt,
         iterations=100000,
         backend=default_backend()
        )
        key = base64.urlsafe_b64encode(kdf.derive(password))
        fk = Fernet(key)
        msg = fk.encrypt(msg)
        return msg

if __name__=='__main__':
    dcdmsg=b'test'
    with open ('pwf','r') as pwf:
        password=pwf.read()
    password=password.rstrip()
    msg=Crypto.EncryptMsg(dcdmsg,password)
    dcdmsg=Crypto.DecryptMsg(msg,password)
    print(msg)
    print(dcdmsg)
