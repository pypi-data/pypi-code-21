# coding:utf-8
'''
Module for serving a qiniu object storage.
'''
import hmac
import hashlib
import base64
import six
import requests
from . import util


class QiniuClient(object):
    HOST = "https://rs.qbox.me"

    def __init__(self, ak, sk):
        self.ak = six.b(ak) if isinstance(ak, six.text_type) else ak
        self.sk = six.b(sk) if isinstance(sk, six.text_type) else sk
        self.session = requests.Session()

    def request(self, method, path, **kw):
        req = requests.Request(method, "%s%s" % (self.HOST, path), **kw)
        preq = req.prepare()
        sign_str = six.b(preq.url.replace(self.HOST, '') + '\n' + (preq.body or ''))
        encode_sign = base64.urlsafe_b64encode(hmac.new(self.sk, sign_str, hashlib.sha1).digest())
        access_token = b"%s:%s" % (self.ak, encode_sign)
        print(access_token)
        preq.headers['Authorization'] = b"QBox %s" % access_token
        return self.session.send(preq)


class ModuleQiniuServe(object):
    @classmethod
    def from_resp_spec(cls, req_spec, resp_spec, **kw):
        pass

    def __init__(self, prefix, key_prefix, bucket, ak, sk, bind=True, **kw):
        self.prefix = util.format_prefix(prefix)
        self.key_prefix = key_prefix




