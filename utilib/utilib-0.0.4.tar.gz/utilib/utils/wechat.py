from utilib.core import http
import json
import hashlib


async def get_access_token(appid, secret):
    _r = await http.async_fetch_url(
        'https://api.weixin.qq.com/cgi-bin/token',
        'GET',
        {},
        True,
        grant_type='client_credential',
        appid=appid,
        secret=secret
    )
    return json.loads(_r.body.decode())


async def get_jsapi_ticket(access_token):
    _r = await http.async_fetch_url(
        'https://api.weixin.qq.com/cgi-bin/ticket/getticket',
        'GET',
        {},
        True,
        type='jsapi',
        access_token=access_token
    )
    return json.loads(_r.body.decode())


async def get_oauth_access_token(appid, secret, code):
    _r = await http.async_fetch_url(
        'https://api.weixin.qq.com/sns/oauth2/access_token',
        'GET',
        {},
        True,
        appid=appid,
        secret=secret,
        code=code,
        grant_type='authorization_code'
    )
    return json.loads(_r.body.decode())


async def get_user_info(access_token, openid):
    _r = await http.async_fetch_url(
        'https://api.weixin.qq.com/sns/userinfo',
        'GET',
        {},
        True,
        access_token=access_token,
        openid=openid,
        lang='zh_CN'
    )
    return json.loads(_r.body.decode())


def get_signature(**kwargs):
    return hashlib.sha1(
        ('&'.join(
            str.format(
                '{k}={v}', k=k, v=v) for k, v in sorted(
                kwargs.items()))).encode('utf-8')).hexdigest()
