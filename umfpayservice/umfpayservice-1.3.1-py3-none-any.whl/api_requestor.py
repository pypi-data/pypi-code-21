# -*- coding: utf-8 -*-

from umfpayservice import http_client, util, error

class APIRequestor(object):

    def __init__(self, client=None):
        self._client = client or http_client.new_default_http_client(
            verify_ssl_certs=False)

    def request(self, method, url, post_data=None, headers=None):
        rbody, rcode = self.request_raw(
            method.lower(), url, post_data, headers)

        if not (200 <= rcode < 300):
            raise error.APIError(
                "接口返回的响应错误: %r (响应码为： %d)" % (rbody, rcode),
                rbody, rcode)

        return rbody

    def download(self, method, url, params=None, headers=None):
        return self.request(method, url, params, headers)

    def upload(self, url, files=None, headers=None):
        util.logger.info("上传文件数据：files= %s" % files)
        rbody, rcode = self._client.upload(url, headers, files=files)

        if not (200 <= rcode < 300):
            raise error.APIError(
                "接口返回的响应错误: %r (响应码为： %d)" % (rbody, rcode),
                rbody, rcode)

        util.logger.info('请求后响应：'
                         '\n返回rcode: %d '
                         '\n返回rbody: %s ', rcode, rbody)
        return rbody

    def request_raw(self, method, url, post_data=None, headers=None):

        util.logger.info("请求前数据：post_data= %s" % post_data)
        rbody, rcode = self._client.request(
            method, url, headers, post_data)

        util.logger.info('请求后响应：'
            '\n返回rcode: %d '
            '\n返回rbody: %s ', rcode, rbody)
        return rbody, rcode
