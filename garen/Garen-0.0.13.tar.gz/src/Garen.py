#!/usr/bin/env python
# -*- coding: utf-8 -*-
# yishenggudou@gmail.com
# @timger http://weibo.com/zhanghaibo
import threading
import requests
import re
import urllib
import urlparse
import json

from flask import Flask, Blueprint, request, Response, url_for, send_from_directory
from werkzeug.datastructures import Headers
from werkzeug.exceptions import NotFound

"""
.. automodule:: Garen

"""

# Default Configuration
DEBUG_FLAG = True
LISTEN_PORT = 7788
METHOD_LIST = ["GET", "POST", "PUT", "DELETE", "PATCH", "OPTIONS"]

proxy = Blueprint('proxy', __name__)

# You can insert Authentication here.
# proxy.before_request(check_login)

# Filters.
HTML_REGEX = re.compile(r'((?:src|action|href)=["\'])/')
JQUERY_REGEX = re.compile(r'(\$\.(?:get|post)\(["\'])/')
JS_LOCATION_REGEX = re.compile(r'((?:window|document)\.location.*=.*["\'])/')
CSS_REGEX = re.compile(r'(url\(["\']?)/')

REGEXES = [HTML_REGEX, JQUERY_REGEX, JS_LOCATION_REGEX, CSS_REGEX]


class Garen(threading.Thread):
    """
    使用线程方便集成到其它系统


    """
    DEFAULT_CONFIG_NAME = ".garen.yml"
    SESSION_MAP = {}

    def __init__(self, port=8899,
                 browser_name='chrome',
                 config_fpath=None,
                 static_root_path=None,
                 queue=None,
                 pipe_filter=None,
                 proxy_headers=None,
                 proxy_cookies=None
                 ):
        """

        :param port:
        :param browser_name:
        :param config_fpath:
        :param static_root_path:
        """
        self._port = port
        self.browser_name = browser_name
        self._config_fpath = config_fpath
        self._static_root_path = static_root_path
        self.app = Flask(__name__)
        super(Garen, self).__init__()
        self.daemon = True
        self.queue = queue
        self.proxy_headers = proxy_headers or {}
        self.proxy_cookies = proxy_cookies or {}
        self.pipe_filter = pipe_filter

    @property
    def pipe_filter_fun(self):
        if self.pipe_filter:
            return self.pipe_filter
        else:
            return lambda x: x

    @property
    def pipe_queue(self):
        """

        :return:
        """
        return self.queue

    @property
    def user_directory(self):
        """

        :return:
        """
        from os import path
        return path.expanduser("~")

    @property
    def config_fpath(self):
        """

        :return:
        """
        from os import path
        if not self._config_fpath:
            self._config_fpath = path.join(self.user_directory, self.DEFAULT_CONFIG_NAME)
        return self._config_fpath

    @property
    def config(self):
        """
        获取到路由配置
        和 HOST 文件类似
        Lazy Load config File

        .. code-block::

            www.aliyun.com 127.0.0.1
            www.google.com 127.0.0.1

        :return:
        """
        import codecs
        if not hasattr(self, '_config'):
            self._config = {}
            with codecs.open(self.config_fpath, 'rb+', 'utf8') as fr:
                for line in fr:
                    if not line.startswith('#'):
                        key = line.strip().split(' ')[0]
                        value = ' '.join(line.strip().split(' ')[1:]).strip()
                        self._config[key] = value
        return self._config

    @property
    def browser_cookie(self):
        """

        :return:
        """
        import browsercookie
        from exceptions import Exception as NotSupportError
        if self.browser_name == 'chrome':
            _ = browsercookie.chrome()
        elif self.browser_name == 'firefox':
            _ = browsercookie.firefox()
        else:
            raise NotSupportError("just support chrome and firefox")
        return _

    def get_cookie_items_from_netloc(self, netloc):
        """

        :param netloc:
        :return:
        """
        _ = []
        for cookie in self.browser_cookie:
            if cookie.domain.find(netloc) >= 0:
                #print cookie, dir(cookie)
                _.append((cookie.name, cookie.value))
        return _

    def get_response_headers(self, headers):
        """

        :param headers:
        :return:
        """
        _ = ','.join(headers.keys())
        response_headers = Headers({
            "Access-Control-Allow-Origin": "*",
            "Access-Control-Allow-Methods": "PUT,GET,POST,DELETE,PATCH",
            "Access-Control-Allow-Headers": _
        })
        return response_headers

    def get_dest_origin_str_by_host(self, host_str):
        """
        获取目标 IP
        1. 根据配置获取
        2. 根据 DNS 获取
        :param host_str:
        :return:
        """
        import socket
        if self.config.get(host_str):
            dest_host_str = self.config.get(host_str)
            ip = self.get_dest_ip_by_host(dest_host_str)
            port = self.get_dest_port_by_host(dest_host_str)
            # print '[USE][CONFIG] {0} => {1}:{2}'.format(host_str, ip, port)

        else:
            ip = socket.gethostbyname(self.get_dest_ip_by_host(host_str))
            port = self.get_dest_port_by_host(host_str)
            # print '[USE][DNS] {0} => {1}:{2}'.format(host_str, ip, port)
        return "{0}:{1}".format(ip, port)

    def get_dest_ip_by_host(self, host_str):
        """

        :param host_str:
        :return:
        """
        return host_str.strip().split(':')[0]

    def get_dest_port_by_host(self, host_str):
        """

        :param domain:
        :return:
        """
        _ = host_str.split(':')
        if len(_) == 1:
            return 80
        else:
            return int(_[1])

    @property
    def listen_port(self):
        """
        listen port
        :return:
        """
        return self._port or 9999

    def pipe_path(self, path):
        """

        :param path:
        :return:
        """
        if self.pipe_queue:
            _ = self.pipe_filter_fun(path)
            if _:
                self.pipe_queue.put(_)

    @property
    def listen_ip(self):
        """

        :return:
        """
        return '0.0.0.0'

    @property
    def static_root_path(self):
        """
        静态资源的映射
        :return:
        """
        import os
        if not self._static_root_path:
            self._static_root_path = os.path.abspath(os.getcwd())
        return self._static_root_path

    def run(self):
        """
        run the gevent Server
        http://www.gevent.org/servers.html
        :return:
        """
        from gevent.wsgi import WSGIServer
        self.app.debug = False
        from flask import make_response
        from functools import update_wrapper

        def nocache(f):
            def new_func(*args, **kwargs):
                resp = make_response(f(*args, **kwargs))
                resp.headers['Cache-Control'] = 'no-store, no-cache, must-revalidate, post-check=0, pre-check=0'
                return resp

            return update_wrapper(new_func, f)

        @proxy.route('/', defaults={'path': ''}, methods=METHOD_LIST)
        @proxy.route('/<path:path>', methods=METHOD_LIST)
        @nocache
        def _proxy_request(path):
            """
            1.  没有代理请求的时候

            2.  有代理请求的时候

            :param path:
            :return:
            """
            import os
            self.pipe_path(path)
            from urlparse import urlparse, urljoin

            if (not request.headers.get('PROXY')) and (request.headers.get('HOST', "")):
                static_path = os.path.join(self.static_root_path, path)
                # print "[SERVE]", static_path
                return send_from_directory(self.static_root_path, path)
            proxy_path = path
            headers = request.headers
            # proxy_netloc =
            scheme, hostname, port = self.get_target_netloc_from_headers(headers)
            # print "H: '%s' P: %d" % (hostname, port)
            # print "F: '%s'" % (proxy_path)
            # Whitelist a few headers to pass on
            request_headers = headers
            if request.query_string:
                path = "/%s?%s" % (proxy_path, request.query_string)
            else:
                path = "/" + proxy_path

            if request.method == "POST" or request.method == "PUT" or request.method == 'PATCH':
                form_data = list(self.iterform(request.form))
                form_data = urllib.urlencode(form_data)
                request_headers["Content-Length"] = len(form_data)
            else:
                form_data = None
            new_request_headers = dict(request_headers)  # self.update_request_headers(request_headers)
            # self.print_proxy_topology(
            #    headers.get('PROXY'),
            #    '{0}:{1}'.format(hostname, port),
            #    ''
            # )
            resp = self.proxy_request(request.method, scheme, path, hostname, port, new_request_headers, form_data)
            # Clean up response headers for forwarding
            d = {}
            crsf_headers = self.get_response_headers(new_request_headers)
            response_headers = Headers()
            for key, value in crsf_headers.items():
                response_headers[key] = value
            response_headers
            for key, value in resp.headers.items():
                # print "HEADER: '%s':'%s'" % (key, value),'Set-Cookie',
                d[key.lower()] = value
                if key in ["content-length", "connection", "content-type", 'Content-Encoding',
                           'Vary',
                           'Cache-Control', 'Expires', 'Transfer-Encoding']:
                    continue
                else:
                    response_headers.add(key, value)

            # If this is a redirect, munge the Location URL
            if "location" in response_headers:
                redirect = response_headers["location"]
                parsed = urlparse.urlparse(request.url)
                redirect_parsed = urlparse.urlparse(redirect)

                redirect_host = redirect_parsed.netloc
                if not redirect_host:
                    redirect_host = "%s:%d" % (hostname, port)

                redirect_path = redirect_parsed.path
                if redirect_parsed.query:
                    redirect_path += "?" + redirect_parsed.query

                munged_path = url_for(".proxy_request",
                                      host=redirect_host,
                                      file=redirect_path[1:])

                url = "%s://%s%s" % (parsed.scheme, parsed.netloc, munged_path)
                response_headers["location"] = url

            # Rewrite URLs in the content to point to our URL schemt.method == " instead.
            # Ugly, but seems to mostly work.
            contents = resp.text
            content_type = resp.headers.get('Content-Type', 'text/html')
            content_type = content_type.strip().split(';')[0]
            # print type(contents), resp.status_code, content_type
            # print response_headers
            flask_response = Response(response=contents,
                                      status=resp.status_code,
                                      headers=response_headers,
                                      content_type=content_type)
            for key, value in self.get_cookie_items_from_netloc(hostname):
                flask_response.set_cookie(key, value)

            return flask_response

        self.app.register_blueprint(proxy, url_prefix='')
        # with self.app.test_request_context():
        #    print url_for('proxy.proxy_request')
        # print '{2}: {0}:{1} .......... {3}'.format(self.listen_ip,
        #                                           self.listen_port,
        #                                           'listen'.upper(),
        #                                           self.static_root_path)
        self.ws = WSGIServer((self.listen_ip, self.listen_port), self.app)
        self.ws.serve_forever()
        return False
        #
        self.app.run(debug=False,
                     use_reloader=False,
                     host=self.listen_ip,
                     port=self.listen_port,
                     threaded=True
                     )

    def get_ip_port_from_netloc(self, netloc_str):
        """

        :param netloc_str:
        :return:
        """
        if netloc_str.find(':') > 0:
            ip, port = netloc_str.split(':')
            port = int(port)
        else:
            ip = netloc_str
            port = 80
        return ip, port

    def get_target_netloc_from_headers(self, headers):
        """
        1.  DNS 拦截模式
            1.  浏览器正常发请求
            2.  host 文件拦截请求到代理服务器. 根据请求带上的Header走
                AJAX 需要加 Header 指定目标代理地址,此处 DNS 走本地 HOST
            特征: 有 HOST, 有 PROXY
        2.  chrome 插件模式
            1.  浏览器发正常的请求,由代理插件转发到代理地址
            2.  插件再根据 HOST 字段走 DNS
            特征: 无 HEADER 有 HOST 字段
        3.  所有的请求直接发到代理服务器,根据 Header 绕过 DNS 解析
            特征: header 中有 PROXY
        :param headers:
        :return:
        """
        from urlparse import urlparse
        if headers.get('PROXY'):
            netloc_str = urlparse(headers.get('PROXY')).netloc
            scheme = urlparse(headers.get('PROXY')).scheme or 'http'
            print "[PROXY] {0}".format(netloc_str)
        else:
            netloc_str = urlparse(headers.get('HOST')).netloc
            scheme = urlparse(headers.get('HOST')).scheme or 'http'
            print "[PROXY] {0}".format(netloc_str)
        ip, port = self.get_ip_port_from_netloc(netloc_str)
        return scheme, ip, port

    def get_path_prefix_from_headers(self, headers):
        """

        :param headers:
        :return:
        """
        _ = ""
        for key, value in headers.items():
            if key.upper() == 'PROXY_PREFIX':
                if value.startswith('/'):
                    _ = value
                else:
                    _ = '/' + value
        return _

    def iterform(self, multidict):
        for key in multidict.keys():
            for value in multidict.getlist(key):
                yield (key.encode("utf8"), value.encode("utf8"))

    @property
    def session(self):
        """

        :return:
        """
        if not hasattr(self, '_session'):
            self._session = requests.Session()
            self._session.cookies = self.browser_cookie
            # self._session.config['keep_alive'] = False
            # self._session.lo
        return self._session

    def get_session_with_origin(self, origin):
        """

        :param origin:
        :return:
        """
        pass

    def proxy_request(self, method, scheme, url, dest_domain, dest_port, headers, data):
        """

        :param method:
        :param scheme:
        :param url:
        :param dest_domain:
        :param dest_port:
        :param headers:
        :param data:
        :return:

        https://github.com/requests/toolbelt/blob/master/requests_toolbelt/adapters/source.py#L42
        """
        from requests_toolbelt.adapters import source
        dest_tuple = (dest_domain, dest_port)
        # source_adapter = source.SourceAddressAdapter(dest_tuple)
        # self.session.mount(url, source_adapter)
        if dest_port != 80:
            _ = "{0}://{1}:{2}".format(scheme, dest_domain, dest_port)
        else:
            _ = "{0}://{1}".format(scheme, dest_domain, dest_port)
        request_url = urlparse.urljoin(_, url)
        headers['referer'] = request_url
        headers['Host'] = urlparse.urlparse(request_url).netloc
        headers[
            'User-Agent'] = 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_12_6) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/61.0.3163.100 Safari/537.36'
        headers['Connection'] = 'close'
        print '[REQUEST]', method, request_url, data
        # print headers
        cookies = {}
        for key, value in self.proxy_headers:
            headers[key] = value
        for key, value in self.proxy_cookies:
            cookies[key] = value
        if data:
            resp = self.session.request(method, request_url, data=data, headers=headers, cookies=cookies)
        else:
            resp = self.session.request(method, request_url, headers=headers, cookies=cookies)
        return resp

    def print_proxy_topology(self, sender, request_domain, request_real_ip_host):
        """

        :param sender:
        :param request_domain:
        :param request_real_ip_host:
        :return:
        """
        _ = """
        ----------- proxy ------------------------------
        -
        -  sender:{sender} --> Proxy Server -> request:{request_domain} -> {request_real_ip_host}
        -
        ------------------------------------------------
        """
        _ = _.format(sender=sender,
                     request_domain=request_domain,
                     request_real_ip_host=request_real_ip_host
                     ).strip()
        for line in _.split('\n'):
            print line.lstrip()

    def exit(self):
        """
        关闭 Socket
        :return:
        """
        if hasattr(self, 'ws'):
            self.ws.shutdown()
            # self.app.


def main():
    o = Garen(port=9988,
              config_fpath='/Volumes/dataDisk/github/Garen/tests/config/config.yml')
    o.daemon = True
    o.start()
    """
    中断不退出
    """
    import time
    while True:
        time.sleep(1)


if __name__ == "__main__":
    main()
