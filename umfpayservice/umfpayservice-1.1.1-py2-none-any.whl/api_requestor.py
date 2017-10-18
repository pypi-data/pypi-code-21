# -*- coding: utf-8 -*-

import urllib
from bs4 import BeautifulSoup

import umfpayservice
from umfpayservice import http_client, util, sign, error

# 请求联动服务地址
service_url = 'https://pay.soopay.net/spay/pay/payservice.do'

def api_encode(data):
    '''
    api请求参数编码处理
    :param data: 发送请求的数据
    :return:
    '''
    for key, value in data.items():
        yield (util.utf8(key), util.utf8(value))

class APIRequestor(object):

    def __init__(self, client=None):
        self._client = client or http_client.new_default_http_client(
            verify_ssl_certs=False)

    def request(self, method, params=None):
        rbody, rcode = self.request_raw(
            method.lower(), params)
        resp = self.interpret_response(rbody, rcode)
        return resp

    def download(self, path, name, method, params=None):
        rbody, rcode = self.request_raw(
            method.lower(), params)
        return rbody, rcode

    def request_raw(self, method, params=None):
        post_data = util.url_encode(list(api_encode(params or {})))

        headers = {
            'Content-Type': 'application/x-www-form-urlencoded',
            'Content-Encoding': umfpayservice.umf_config.charset
        }
        util.logger.info("请求前数据：post_data= %s" % post_data)
        rbody, rcode = self._client.request(
            method, service_url, headers, post_data)

        util.logger.info('请求后响应：'
            '\n返回rcode: %d '
            '\n返回rbody: %s ', rcode, rbody)
        return rbody, rcode

    def interpret_response(self, rbody, rcode):
        '''
        解析response
        :param rbody:
        :param rcode:
        :return:
        '''
        if not (200 <= rcode < 300):
            raise error.APIError(
                "接口返回的响应错误: %r (响应码为： %d)" % (rbody, rcode),
                rbody, rcode)
        try:
            rbody_dict = self._interpret_meta(rbody.strip())
            if sign.verify(rbody_dict['plain'], rbody_dict['sign']):
                if 'sign' in rbody_dict:
                    del rbody_dict['sign']
                if 'sign_type' in rbody_dict:
                    del rbody_dict['sign_type']
                if 'version' in rbody_dict:
                    del rbody_dict['version']
                if 'plain' in rbody_dict:
                    del rbody_dict['plain']
                resp = rbody_dict

                util.logger.info("解析响应数据获得：\n%s" % str(resp))
                return resp
        except Exception as e:
            raise error.APIError(
                "接口返回的响应错误: %r (响应码为： %d)" % (rbody, rcode),
                rbody, rcode)
        return None

    def _interpret_meta(self, rbody):
        '''
        解析meta
        :param rbody:
        :return:
        '''
        try:
            soup = BeautifulSoup(rbody, "html.parser")
            content = soup.head.meta['content']
            content = util.utf8(content)

            resp = {param_key: param_value for param_key, param_value in (split_param.split('=', 1) for split_param in content.split('&'))}
            plain = sign.get_sorted_plain(resp)
            resp['plain'] = plain
        except:
            raise error.RequestError('解析服务器响应失败。body = %s' % rbody)
        return resp
