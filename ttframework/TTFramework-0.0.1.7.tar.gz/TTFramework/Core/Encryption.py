import base64,hashlib
from Crypto.Cipher import AES
from binascii import b2a_hex, a2b_hex
from .FuncHelper import FuncHelper

class Encryption(object):

    @staticmethod
    def encode_base64(s=''):
        return base64.b64encode(bytes(s,'utf-8'))

    @staticmethod
    def decode_base64(s=''):
        return base64.b64decode(s).decode(encoding="utf-8")

    @staticmethod
    def encrypt_md5_by_str(s=''):
        return hashlib.md5(s.encode('utf-8')).hexdigest().upper()

    @staticmethod
    def encrypt_md5_by_file(file_path):
        try:
            with open(file_path,'rb') as f:
                return hashlib.md5(f.read()).hexdigest().upper()
        except Exception as e:
            return None

    @staticmethod
    def encrypt_aes(s,key):
        cryptor = AES.new(key, AES.MODE_CBC, key)
        text = s.encode("utf-8")
        # 这里密钥key 长度必须为16（AES-128）、24（AES-192）、或32（AES-256）Bytes 长度.目前AES-128足够用
        length = 16
        count = len(text)
        add = length - (count % length)
        text = text + (b'\0' * add)
        ciphertext = cryptor.encrypt(text)
        # 因为AES加密时候得到的字符串不一定是ascii字符集的，输出到终端或者保存时候可能存在问题
        # 所以这里统一把加密后的字符串转化为16进制字符串
        return b2a_hex(ciphertext).decode("ASCII")

    # 解密后，去掉补足的空格用strip() 去掉
    @staticmethod
    def decrypt_aes(s,key):
        cryptor = AES.new(key, AES.MODE_CBC, key)
        plain_text = cryptor.decrypt(a2b_hex(s))
        return plain_text.rstrip(b'\0').decode("utf-8")


if __name__ == '__main__':
    print(Encryption.encode_base64('lisigu'))
    print(Encryption.encode_base64('12345689'))