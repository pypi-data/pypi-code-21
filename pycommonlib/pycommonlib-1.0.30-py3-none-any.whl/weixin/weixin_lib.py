# -*- coding: utf-8 -*-
import requests
import logging
import json
from django.conf import settings
from pycommonlib.util import cache
from .exceptions import APIError

CACHE_WEIXIN_ACCESSTOEKN = 'weixin_access_token_{}'

_logger = logging.getLogger(__name__)


class WeiXinClient:
    def __init__(self, appId, appSecKey):
        self.appId = appId
        self.appSecKey = appSecKey
        self.CACHE_WEIXIN_ACCOUNTTOKEN = 'weixin_account_token_{}'.format(appId)
        self.CACHE_WEIXIN_JS_TICKET = 'weixin_js_ticket_{}'.format(appId)

    def get_token(self):
        token = cache.get(self.CACHE_WEIXIN_ACCOUNTTOKEN)
        if token:
            _logger.info('get_token load token from cache:{}'.format(token))
            return token
        # get token from weixin server
        url = 'https://api.weixin.qq.com/cgi-bin/token?grant_type=client_credential&appid={}&secret={}'.format(self.appId, self.appSecKey)
        r = requests.get(url, verify=False)
        if r.status_code == 200:
            response_data = r.json()
            if response_data.get('errcode', 0) == 0:
                cache.put(self.CACHE_WEIXIN_ACCOUNTTOKEN, response_data['access_token'], response_data['expires_in'])
                _logger.info(_format_log_message('get_token succeed', r))
                return response_data['access_token']
            else:
                _logger.error(_format_log_message('get_token failed', r))
                raise APIError()
        else:
            _logger.error(_format_log_message('get_token failed', r))
            raise APIError()

    def get_access_token(self, code):
        '''
        @return: {'access_token':'','openid','','unionid':''}
        '''
        assert code
        cacheKey = CACHE_WEIXIN_ACCESSTOEKN.format(code)
        token = cache.get(cacheKey)
        if token:
            _logger.info('get_access_token load token from cache:{}'.format(token))
            return token
        url = 'https://api.weixin.qq.com/sns/oauth2/access_token?appid={}&secret={}&code={}&grant_type=authorization_code'.format(self.appId, self.appSecKey, code)
        r = requests.get(url, verify=False)
        if r.status_code == 200:
            response_data = r.json()
            if response_data.get('errcode', 0) == 0:
                _logger.info(_format_log_message('get_access_token succeed', r))
                token = {'access_token': response_data['access_token'], 'openid': response_data['openid'], 'unionid': response_data.get('unionid')}
                cache.put(cacheKey, token, response_data['expires_in'])
                return token
            else:
                _logger.error(_format_log_message('get_access_token failed', r))
                raise APIError()
        else:
            _logger.error(_format_log_message('get_access_token failed', r))
            raise APIError()

    def refresh_access_token(self, refreshToken):
        url = 'https://api.weixin.qq.com/sns/oauth2/refresh_token?appid={}&grant_type=refresh_token&refresh_token={}'.format(self.appId, refreshToken)
        r = requests.get(url, verify=False)
        if r.status_code == 200:
            response_data = r.json()
            if response_data.get('errcode', 0) == 0:
                _logger.info(_format_log_message('get_access_token succeed', r))
                return response_data
            else:
                _logger.error(_format_log_message('get_access_token failed', r))
                raise APIError()
        else:
            _logger.error(_format_log_message('get_access_token failed', r))
            raise APIError()

    def get_user_info_with_code(self, code, depth=3):
        accessToken = self.get_access_token(code)
        url = 'https://api.weixin.qq.com/sns/userinfo?access_token={}&openid={}'.format(accessToken['access_token'], accessToken['openid'])
        r = requests.get(url, verify=False)
        r.encoding = 'utf-8'
        if r.status_code == 200:
            response_data = r.json()
            if 'errcode' in response_data:
                if response_data['errcode'] == 40001 and depth > 0:
                    depth = depth - 1
                    cache.delete(CACHE_WEIXIN_ACCESSTOEKN.format(code))
                    return get_user_info_with_code(code, depth)
                else:
                    _logger.error(_format_log_message('get_user_info_with_code failed', r))
                    raise APIError()
            else:
                _logger.info(_format_log_message('get_user_info_with_code succeed', r))
                return r.json()
        else:
            _logger.error(_format_log_message('get_user_info_with_code failed', r))
            raise APIError()

    def get_jsapi_ticket(self):
        ticket = cache.get(self.CACHE_WEIXIN_JS_TICKET)
        if ticket:
            _logger.info('get_jsapi_ticket load ticket from cache:{}'.format(ticket))
            return ticket
        token = self.get_token()
        url = 'https://api.weixin.qq.com/cgi-bin/ticket/getticket?access_token={}&type=jsapi'.format(token)
        r = requests.get(url, verify=False)
        if r.status_code == 200:
            response_data = r.json()
            if response_data['errcode'] == 0:
                cache.put(self.CACHE_WEIXIN_JS_TICKET, response_data['ticket'], response_data['expires_in'])
                _logger.info(_format_log_message('get_jsapi_ticket succeed', r))
                return response_data['ticket']
            else:
                _logger.error(_format_log_message('get_jsapi_ticket failed', r))
                raise APIError()
        else:
            _logger.error(_format_log_message('get_jsapi_ticket failed', r))
            raise APIError()

    def get_user_info(self, openId, depth=3):
        token = self.get_token()
        url = 'https://api.weixin.qq.com/cgi-bin/user/info?access_token={}&openid={}&lang=zh_CN'.format(token, openId)
        r = requests.get(url, verify=False)
        r.encoding = 'utf-8'
        if r.status_code == 200:
            response_data = r.json()
            if 'errcode' in response_data:
                if response_data['errcode'] == 40001 and depth > 0:
                    depth = depth - 1
                    cache.delete(self.CACHE_WEIXIN_ACCOUNTTOKEN)
                    return get_user_info(openId, depth)
                else:
                    _logger.error(_format_log_message('get_user_info failed', r))
                    raise APIError()
            else:
                _logger.info(_format_log_message('get_user_info succeed', r))
                return r.json()
        else:
            _logger.error(_format_log_message('get_user_info failed', r))
            raise APIError()

    def send_template_message(self, toOpenId, templateId, url, templateData):
        data = {"touser": toOpenId, "template_id": templateId, "url": url, "topcolor": "#FF0000", "data": templateData}
        token = self.get_token()
        url = 'https://api.weixin.qq.com/cgi-bin/message/template/send?access_token={}'.format(token)
        r = requests.post(url, data=json.dumps(data), headers={'Content-Type': 'application/json'}, verify=False)
        if r.status_code == 200:
            response_data = r.json()
            if response_data['errcode'] == 0:
                _logger.info(_format_log_message('sent_template_message succeed', r))
            else:
                _logger.error(_format_log_message('sent_template_message failed', r))
                raise APIError()
        else:
            _logger.error(_format_log_message('sent_template_message failed', r))
            raise APIError()


def _format_log_message(message, r):
    return u'''
           {}
           url:{}
           response code:{}
           response body:{}
           '''.format(message, r.url, r.status_code, r.text)
