#!/usr/bin/env python
# -*- coding:utf8 -*-
try: import httplib
except ImportError:
    import http.client as httplib
import sys

if sys.version_info[0]==3:
    from urllib.request import quote, urlopen
    from urllib.parse import  urlencode

else:
    from urllib import quote,urlencode, urlopen


import time
import json
import base64
import hmac,ssl
import uuid
from hashlib import sha1

try:
    _create_unverified_https_context = ssl._create_unverified_context
except AttributeError:
    # Legacy Python that doesn't verify HTTPS certificates by default
    pass
else:
    # Handle target environment that doesn't support HTTPS verification
    ssl._create_default_https_context = _create_unverified_https_context

class AliyunClient:
    def __init__(self, id, secret, endpoint='https://ecs.aliyuncs.com', version='2014-05-26'):
        self.access_id = id
        self.access_secret = secret
        self.version= version

        self.url = endpoint

    def sign(self,accessKeySecret, parameters):
        sortedParameters = sorted(parameters.items(), key=lambda parameters: parameters[0])
        canonicalizedQueryString = ''
        for (k,v) in sortedParameters:
            canonicalizedQueryString += '&' + self.percent_encode(k) + '=' + self.percent_encode(v)
        stringToSign = 'GET&%2F&' + self.percent_encode(canonicalizedQueryString[1:])
        bs = accessKeySecret +'&'
        if sys.version_info[0]==3:
            bs = bytes(bs,encoding='utf8')
            stringToSign = bytes(stringToSign,encoding='utf8')
        h = hmac.new(bs, stringToSign, sha1)
        # 进行编码
        signature = base64.b64encode(h.digest()).strip()
        return signature
    def percent_encode(self,encodeStr):
        encodeStr = str(encodeStr)
        res = quote(encodeStr)
        res = res.replace('+', '%20')
        res = res.replace('*', '%2A')
        res = res.replace('%7E', '~')
        return res
    # 构建除共公参数外的所有URL
    def make_url(self,params):
        timestamp = time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())
        parameters = {
            'Format' : 'JSON',
            'Version' : self.version,
            'AccessKeyId' : self.access_id,
            'SignatureVersion' : '1.0',
            'SignatureMethod' : 'HMAC-SHA1',
            'SignatureNonce' : str(uuid.uuid1()),
            'TimeStamp' : timestamp,
        }
        for key in params.keys():
            parameters[key] = params[key]
        signature = self.sign(self.access_secret,parameters)
        parameters['Signature'] = signature
        url = self.url + "/?" + urlencode(parameters)
        return url
    def do_action(self,params):
        url = self.make_url(params)

        try:
            conn = urlopen(url)
            response = conn.read().decode()
        except Exception as e:
            response = e.read().decode()
        try:
            res = json.loads(response)
        except ValueError as e:
            raise SystemExit(e)
        return res




# 继承原始类
class EcsClient(AliyunClient):

    def DescribeInstanceTypes(self, region):
        action_dict = {"Action":"DescribeInstanceTypes","RegionId":region }
        return self.do_action(action_dict)


if __name__ == "__main__":
    clt = EcsClient('xx', 'bb','https://ecs.aliyuncs.com','2014-05-26')
    res = clt.DescribeInstanceTypes('cn-shenzhen')
    print(res)