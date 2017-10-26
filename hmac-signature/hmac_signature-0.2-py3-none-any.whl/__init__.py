'''create the class to make a signature with the hmac algorithm'''
import hmac
import hashlib
import base64


class Signature:
    '''make a signature with the hmac algorithm'''
    methodDict = {
        'sha1': hashlib.sha1,
        'sha256': hashlib.sha256
    }

    @classmethod
    def methods(cls):
        '''return the encryption methods supported'''
        return cls.methodDict

    @classmethod
    def create(cls, key, method, content):
        '''create a signature, need key, contnet and encryption method'''
        machine = hmac.new(key=key, digestmod=cls.methodDict[method])
        machine.update(content)
        signature = machine.digest()
        return base64.b64encode(signature)
