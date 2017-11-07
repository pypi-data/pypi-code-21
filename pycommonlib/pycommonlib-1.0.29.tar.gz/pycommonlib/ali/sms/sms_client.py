import hashlib
import hmac
import uuid
import base64
import logging
from urllib import parse

import requests

from pycommonlib.util import datetime

_logger = logging.getLogger('ALI-SMS')


def compose_string_to_sign(params, httpMethod):
    stringtoSign = []
    keylist = sorted(params.keys())
    for key in keylist:
        stringtoSign.append(parse.urlencode({key: params.get(key)}, safe='~', encoding='utf8', quote_via=parse.quote))
    stringtoSign = '&'.join(stringtoSign)
    stringtoSign = '{}&%2F&{}'.format(httpMethod, parse.quote(stringtoSign, safe='~', encoding='utf8'))
    return stringtoSign


def sign(AccessKeySecret, stringToSign):
    h = hmac.new('{}&'.format(AccessKeySecret).encode(), stringToSign.encode(), hashlib.sha1)
    signature = str(base64.b64encode(h.digest()), 'utf-8')
    signature = parse.quote(signature, safe='~', encoding='utf8')
    return signature


def sign_param(params, httpMethod, AccessKeySecret):
    stringtosign = compose_string_to_sign(params, httpMethod)
    return sign(AccessKeySecret, stringtosign)


class SMSClient(object):
    def __init__(self, AccessKeyId, AccessKeySecret):
        self.AccessKeyId = AccessKeyId
        self.AccessKeySecret = AccessKeySecret

    def send(self, RecNum, SignName, TemplateCode, ParamString):
        '''
        @ParamString RecNum: 目标手机号，多个手机号可以逗号分隔
        @ParamString SignName: 管理控制台中配置的短信签名（状态必须是验证通过),例如:阿里云短信服务
        @ParamString TemplateCode: 管理控制台中配置的审核通过的短信模板的模板CODE（状态必须是验证通过）
        @ParamString ParamString: 短信模板中的变量；数字需要转换为字符串；个人用户每个变量长度必须小于15个字符。 
        例如:短信模板为：“接受短信验证码${no}”,此参数传递{“no”:”123456”}，用户将接收到[短信签名]接受短信验证码123456
        '''
        params = {
            'Action': 'SingleSendSms',
            'SignName': SignName,
            'TemplateCode': TemplateCode,
            'ParamString': ParamString,
            'RecNum': RecNum,
            ######### common parameter #######
            'Format': 'JSON',
            'Version': '2016-09-27',
            'AccessKeyId': self.AccessKeyId,
            'SignatureMethod': 'HMAC-SHA1',
            'Timestamp': datetime.utc_now().strftime("%Y-%m-%dT%H:%M:%SZ"),
            'SignatureVersion': '1.0',
            'SignatureNonce': str(uuid.uuid4()),
        }
        signature = sign_param(params, 'POST', self.AccessKeySecret)
        params['Signature'] = signature
        requestBody = '&'.join(['{}={}'.format(key, value) for key, value in params.items()])
        r = requests.post('https://sms.aliyuncs.com/', data=requestBody.encode('utf-8'), headers={'Content-Type': 'application/x-www-form-urlencoded'})
        # print('request url:{}, \n method:{} \n heaeder:{} \n body: {}'.format(r.request.url, r.request.method, r.request.headers, r.request.body))
        if r.status_code == 200:
            _logger.debug('sent succeed')
            return True
        else:
            # print('sent failed. response:\n status:{}\n body:{}'.format(r.status_code, r.text))
            _logger.debug('sent failed. response:\n status:{}\n body:{}'.format(r.status_code, r.text))
            return False
