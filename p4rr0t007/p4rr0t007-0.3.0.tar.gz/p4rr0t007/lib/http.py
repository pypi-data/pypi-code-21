# -*- coding: utf-8 -*-

import random

import requests

from requests import Session as BaseClient
from requests.structures import CaseInsensitiveDict
from .core import utf8


USER_AGENTS = dict(
    iphone_ua_string='Mozilla/5.0 (iPhone; CPU iPhone OS 5_1 like Mac OS X) AppleWebKit/534.46 (KHTML, like Gecko) Version/5.1 Mobile/9B179 Safari/7534.48.3',
    ipad_ua_string='Mozilla/5.0(iPad; U; CPU iPhone OS 3_2 like Mac OS X; en-us) AppleWebKit/531.21.10 (KHTML, like Gecko) Version/4.0.4 Mobile/7B314 Safari/531.21.10',
    galaxy_tab_ua_string='Mozilla/5.0 (Linux; U; Android 2.2; en-us; SCH-I800 Build/FROYO) AppleWebKit/533.1 (KHTML, like Gecko) Version/4.0 Mobile Safari/533.1',
    galaxy_s3_ua_string='Mozilla/5.0 (Linux; U; Android 4.0.4; en-gb; GT-I9300 Build/IMM76D) AppleWebKit/534.30 (KHTML, like Gecko) Version/4.0 Mobile Safari/534.30',
    kindle_fire_ua_string='Mozilla/5.0 (Macintosh; U; Intel Mac OS X 10_6_3; en-us; Silk/1.1.0-80) AppleWebKit/533.16 (KHTML, like Gecko) Version/5.0 Safari/533.16 Silk-Accelerated=true',
    playbook_ua_string='Mozilla/5.0 (PlayBook; U; RIM Tablet OS 2.0.1; en-US) AppleWebKit/535.8+ (KHTML, like Gecko) Version/7.2.0.1 Safari/535.8+',
    nexus_7_ua_string='Mozilla/5.0 (Linux; Android 4.1.1; Nexus 7 Build/JRO03D) AppleWebKit/535.19 (KHTML, like Gecko) Chrome/18.0.1025.166  Safari/535.19',
    windows_phone_ua_string='Mozilla/5.0 (compatible; MSIE 9.0; Windows Phone OS 7.5; Trident/5.0; IEMobile/9.0; SAMSUNG; SGH-i917)',
    blackberry_torch_ua_string='Mozilla/5.0 (BlackBerry; U; BlackBerry 9800; zh-TW) AppleWebKit/534.8+ (KHTML, like Gecko) Version/6.0.0.448 Mobile Safari/534.8+',
    blackberry_bold_ua_string='BlackBerry9700/5.0.0.862 Profile/MIDP-2.1 Configuration/CLDC-1.1 VendorID/331 UNTRUSTED/1.0 3gpp-gba',
    blackberry_bold_touch_ua_string='Mozilla/5.0 (BlackBerry; U; BlackBerry 9930; en-US) AppleWebKit/534.11+ (KHTML, like Gecko) Version/7.0.0.241 Mobile Safari/534.11+',
    windows_rt_ua_string='Mozilla/5.0 (compatible; MSIE 10.0; Windows NT 6.2; ARM; Trident/6.0)',
    j2me_opera_ua_string='Opera/9.80 (J2ME/MIDP; Opera Mini/9.80 (J2ME/22.478; U; en) Presto/2.5.25 Version/10.54',
    ie_ua_string='Mozilla/5.0 (compatible; MSIE 10.0; Windows NT 6.2; Trident/6.0)',
    ie_touch_ua_string='Mozilla/5.0 (compatible; MSIE 10.0; Windows NT 6.2; Trident/6.0; Touch)',
    mac_safari_ua_string='Mozilla/5.0 (Macintosh; Intel Mac OS X 10_6_8) AppleWebKit/537.13+ (KHTML, like Gecko) Version/5.1.7 Safari/534.57.2',
    windows_ie_ua_string='Mozilla/5.0 (compatible; MSIE 9.0; Windows NT 6.1; Trident/5.0)',
    ubuntu_firefox_ua_string='Mozilla/5.0 (X11; Ubuntu; Linux i686; rv:15.0) Gecko/20100101 Firefox/15.0.1',
    google_bot_ua_string='Mozilla/5.0 (compatible; Googlebot/2.1; +http://www.google.com/bot.html)',
    nokia_n97_ua_string='Mozilla/5.0 (SymbianOS/9.4; Series60/5.0 NokiaN97-1/12.0.024; Profile/MIDP-2.1 Configuration/CLDC-1.1; en-us) AppleWebKit/525 (KHTML, like Gecko) BrowserNG/7.1.12344',
    android_firefox_aurora_ua_string='Mozilla/5.0 (Android; Mobile; rv:27.0) Gecko/27.0 Firefox/27.0',
    thunderbird_ua_string='Mozilla/5.0 (X11; Linux x86_64; rv:38.0) Gecko/20100101 Thunderbird/38.2.0 Lightning/4.0.2',
    outlook_usa_string='Mozilla/4.0 (compatible; MSIE 7.0; Windows NT 6.1; Trident/6.0; Microsoft Outlook 15.0.4420)',
)


def get_user_agent():
    return random.choice(USER_AGENTS.values())


# class WebPageResponse(object):
#     def __init__(self, response):
#         self.response = response
#         self.dom = dom_from_string(response.contents)

#     @property
#     def contents(self):
#         return self.response.contents

#     def query(self, xpath):
#         return self.dom.find(xpath)

#     def get_img(self, class_name='static'):
#         return filter(bool, [dict(x.attrs).get('src') for x in self.dom.findAll('img') if class_name in dict(x.attrs).get('class', '')])


class Client(BaseClient):
    def request(self, method, url, *args, **kw):
        response = self.raw_request(method, url, *args, **kw)
        return self.process_response(response)

    def raw_request(self, method, url, headers=None, data=None, as_json=False, **kw):
        method = method.strip().upper()
        headers = CaseInsensitiveDict(headers or {})
        if 'User-Agent' not in headers:
            headers['User-Agent'] = get_user_agent()

        if 'Content-Type' not in headers:
            if as_json:
                headers['Content-Type'] = 'application/json'

            elif method == 'POST' and isinstance(data, dict):
                headers['Content-Type'] = 'application/x-www-form-urlencoded'

        kw['headers'] = headers
        response = super(Client, self).request(method, url, **kw)
        return response

    def post_form(self, url, data, method='POST', headers=None, **kw):
        headers = CaseInsensitiveDict(headers or {})
        if 'Content-Type' not in headers:
            headers['Content-Type'] = 'application/x-www-form-urlencoded'

        return self.request(method, url, data=data, headers=headers, **kw)

    def process_response(self, response):
        # content_type = response.headers['Content-Type']
        # if 'html' in content_type:
        #     return WebPageResponse(response)

        return response


def read_url(url, method='GET', headers=None, connect_timeout=1, read_timeout=1, **kw):
    kw['timeout'] = (connect_timeout, read_timeout)
    return utf8(requests.request(method, url, headers, **kw).content.strip())


def get_my_ip():
    return read_url('https://api.ipify.org')
