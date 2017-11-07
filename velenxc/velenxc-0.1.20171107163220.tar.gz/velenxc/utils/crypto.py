
import re
import hashlib
import base64
from Crypto.Cipher import AES


class Crypt(object):

    @staticmethod
    def pkcs5_padding(text):
        text = text.encode()
        padding = (AES.block_size - len(text) % AES.block_size) * chr(AES.block_size - len(text) % AES.block_size)

        return text + padding.encode()

    @staticmethod
    def pkcs5_eliminate_padding(text):

        return text[0:-ord(text[-1])]

    @classmethod
    def aes_base64_encrypt(cls, text, key, iv='1234567890123456'):
        """
        aes加密, MODE_CBC, key, IV
        """
        aes_encrypt = AES.new(key, mode=AES.MODE_CBC, IV=iv)
        text = Crypt.pkcs5_padding(text)
        encrypt_text = aes_encrypt.encrypt(text)
        return base64.b64encode(encrypt_text)

    @classmethod
    def aes_base64_decrypt(cls, text, key, iv='1234567890123456'):
        """
        aes解密, MODE_CBC, KEY, IV
        """
        try:
            aes_decrypt = AES.new(key, mode=AES.MODE_CBC, IV=iv)
            decode_text = base64.b64decode(text)
            decode_text = aes_decrypt.decrypt(decode_text)
            return Crypt.pkcs5_eliminate_padding(decode_text.decode())
        except (UnicodeError, TypeError, ValueError, AssertionError, Exception) as e:
            return None

    @classmethod
    def md5(cls, text):
        """ md5加密算法

        :param text 被加密的文本

        :return 加密的密文
        """
        try:
            text = text.encode(encoding='utf-8')
        except Exception:
            pass

        m = hashlib.md5(text)
        return m.hexdigest()


class ChineseCoding(object):
    """ 对中文做编码，适用于分类特征中的中文分类转成数字分类表达 """

    @classmethod
    def check_chinese(cls, string):
        re_chinese = re.compile(r'[\u4e00-\u9fa5]+')
        if re_chinese.search(string):
            return True

        return False
