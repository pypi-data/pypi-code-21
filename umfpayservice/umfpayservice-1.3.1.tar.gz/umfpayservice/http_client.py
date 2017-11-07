# -*- coding: utf-8 -*-

import sys
import textwrap

from umfpayservice import util, error

# - Requests是优先级最高的HTTP请求库
# - 谷歌的应用程序引擎使用urlfetch
# - Pycurl是第三优先级的库，毕竟它可以进行SSL认证。
# - 回落到urlurllib2.
try:
    import urllib2
except ImportError:
    pass

try:
    import pycurl
except ImportError:
    pycurl = None

try:
    import requests
except ImportError:
    requests = None
else:
    try:
        # Require version 0.8.8, but don't want to depend on distutils
        version = requests.__version__
        major, minor, patch = [int(i) for i in version.split('.')]
    except Exception:
        # Probably some new-fangled version, so it should support verify
        pass
    else:
        if (major, minor, patch) < (0, 8, 8):
            util.logger.warning('警告：你的requests库版本为：%s。'
                                'umfservice库需要你的requests库的版本大于0.8.8。'
                                'umfservice会使用另外的HTTP请求库以便使umfservice正常工作。\n'
                                '我们建议你升级你的requests库')
            requests = None

try:
    from google.appengine.api import urlfetch
except ImportError:
    urlfetch = None


def new_default_http_client(*args, **kwargs):
    if urlfetch:
        impl = UrlFetchClient
    elif requests:
        requests.adapters.DEFAULT_RETRIES = 5
        s = requests.session()
        s.keep_alive = False

        impl = RequestsClient
    elif pycurl:
        impl = PycurlClient
    else:
        impl = Urllib2Client

        util.logger.warning('由于没有requests和pycurl库，umfservice请求库已回落到urllib2/urllib'
                            'urllib2没有SSL验证服务器证书，出于安全考虑，请安装requests库')

    return impl(*args, **kwargs)


class HTTPClient(object):

    def __init__(self, verify_ssl_certs=True):
        self._verify_ssl_certs = verify_ssl_certs

    def request(self, method, url, headers, post_data=None):
        raise NotImplementedError(
            'HTTPClient子类必须重写request方法')

    def upload(self, url, headers, files, post_data):
        raise NotImplementedError(
            'HTTPClient子类必须重写upload方法')
        # raise ImportError(
        #     '检测到未安装request库，使用上传文件功能请安装request库')


class RequestsClient(HTTPClient):
    name = 'requests'

    def request(self, method, url, headers, post_data=None):
        kwargs = {}

        try:
            try:
                result = requests.request(method,
                                          url,
                                          headers=headers,
                                          data=post_data,
                                          timeout=80,
                                          **kwargs)
            except TypeError as e:
                raise error.RequestError(
                    'requests库版本与umfpayservice不兼容，请更新requests库。')

            content = result.content
            status_code = result.status_code
        except Exception as e:
            self._handle_request_error(e)
        return content, status_code

    def upload(self, url, headers, files, post_data=None):
        kwargs = {}
        try:
            try:
                result = requests.post(url,
                                       headers=headers,
                                       data=post_data,
                                       timeout=180,
                                       files = files,
                                       **kwargs)
            except TypeError as e:
                raise error.RequestError(
                    'requests库版本与umfpayservice不兼容，请更新requests库。')

            content = result.content
            status_code = result.status_code
        except Exception as e:
            self._handle_request_error(e)
        return content, status_code

    def _handle_request_error(self, e):
        if isinstance(e, requests.exceptions.RequestException):
            msg = ("网络异常：：：  ")
            err = "%s: %s" % (type(e).__name__, str(e))
        else:
            msg = ("网络异常：：： "
                   "可能是配置错误导致，")
            err = "%s异常被抛出，" % (type(e).__name__,)
            if str(e):
                err += " 错误信息为： %s。" % (str(e),)
            else:
                err += " 没有错误信息。"
        msg = textwrap.fill(msg) + "\n\n(网络错误: %s)" % (err,)
        raise error.RequestError(msg)


class UrlFetchClient(HTTPClient):
    name = 'urlfetch'

    def request(self, method, url, headers, post_data=None):
        try:
            result = urlfetch.fetch(
                url=url,
                method=method,
                headers=headers,
                validate_certificate=self._verify_ssl_certs,
                deadline=55,
                payload=post_data
            )
        except urlfetch.Error as e:
            self._handle_request_error(e, url)

        return result.content, result.status_code

    def _handle_request_error(self, e, url):
        msg = '网络异常：：：'
        msg = textwrap.fill(msg) + "\n\n(Network error: " + str(e) + ")"
        raise error.RequestError(msg)


class PycurlClient(HTTPClient):
    name = 'pycurl'

    def request(self, method, url, headers, post_data=None):
        s = util.StringIO.StringIO()
        curl = pycurl.Curl()

        if method == 'get':
            curl.setopt(pycurl.HTTPGET, 1)
        elif method == 'post':
            curl.setopt(pycurl.POST, 1)
            curl.setopt(pycurl.POSTFIELDS, post_data)
        else:
            curl.setopt(pycurl.CUSTOMREQUEST, method.upper())

        # pycurl doesn't like unicode URLs
        curl.setopt(pycurl.URL, util.utf8(url))

        curl.setopt(pycurl.WRITEFUNCTION, s.write)
        curl.setopt(pycurl.NOSIGNAL, 1)
        curl.setopt(pycurl.CONNECTTIMEOUT, 30)
        curl.setopt(pycurl.TIMEOUT, 80)
        curl.setopt(pycurl.HTTPHEADER, ['%s: %s' % (k, v)
                    for k, v in headers.items()])

        curl.setopt(pycurl.SSL_VERIFYHOST, False)

        try:
            curl.perform()
        except pycurl.error as e:
            self._handle_request_error(e)
        rbody = s.getvalue()
        rcode = curl.getinfo(pycurl.RESPONSE_CODE)
        return rbody, rcode

    def _handle_request_error(self, e):
        msg = "网络异常：：："
        msg = textwrap.fill(msg) + "\n\n(Network error: " + e[1] + ")"
        raise error.RequestError(msg)

class Urllib2Client(HTTPClient):
    if sys.version_info >= (3, 0):
        name = 'urllib.request'
    else:
        name = 'urllib2'

    def request(self, method, url, headers, post_data=None):
        if sys.version_info >= (3, 0) and isinstance(post_data, str):
            post_data = post_data.encode('utf-8')

        req = urllib2.Request(url, post_data, headers)

        if method not in ('get', 'post'):
            req.get_method = lambda: method.upper()

        try:
            response = urllib2.urlopen(req)
            rbody = response.read()
            rcode = response.code
        except urllib2.HTTPError as e:
            rcode = e.code
            rbody = e.read()
        except (urllib2.URLError, ValueError) as e:
            self._handle_request_error(e)
        return rbody, rcode

    def _handle_request_error(self, e):
        msg = ("网络异常：：：")
        msg = textwrap.fill(msg) + "\n\n(Network error: " + str(e) + ")"
        raise error.RequestError(msg)
