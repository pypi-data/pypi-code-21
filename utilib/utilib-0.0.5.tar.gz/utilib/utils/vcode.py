from tornado.httpclient import AsyncHTTPClient, HTTPRequest, HTTPError
from utilib.core import exceptions
import urllib


class VcodeHelper:

    def __init__(self, apikey):
        self.apikey = apikey

    async def send_sms_vcode(self, code, mobile, expire=2):
        template = '【超盟数据】您的验证码是{code}，有效期为{minute}分钟。如非本人操作，请忽略本短信'
        _data = {
            'apikey': self.apikey,
            'mobile': mobile,
            'text': str.format(template, code=code, minute=expire)
        }
        request = HTTPRequest(
            'https://sms.yunpian.com/v2/sms/single_send.json',
            body=urllib.parse.urlencode(_data), method='POST')
        http_client = AsyncHTTPClient()
        try:
            await http_client.fetch(request)
        except HTTPError:
            raise exceptions.SMSSendFailed

    async def send_voice_vcode(self, code, mobile):
        _data = {
            'apikey': self.apikey,
            'mobile': mobile,
            'code': code
        }
        request = HTTPRequest(
            'https://voice.yunpian.com/v2/voice/send.json',
            body=urllib.parse.urlencode(_data), method='POST')
        http_client = AsyncHTTPClient()
        await http_client.fetch(request)


def require_params(*args):
    if None in args:
        raise exceptions.MissingRequiredParams
