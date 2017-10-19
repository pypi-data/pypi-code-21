import json
from io import BytesIO

import pycurl

import re

from tld import get_tld

from netboy.util.loader import load


class Setup:
    # DEFAULT_USER_AGENT = 'Mozilla/5.0 (X11; Linux x86_64; compatible; bingbot/2.0; +http://www.bing.com/bingbot.htm; Baiduspider/2.0; +http://www.baidu.com/search/spider.html) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/46.0.2490.80() Safari/537.36'
    DEFAULT_USER_AGENT = 'Chrome'

    def __init__(self):
        self.databuf = BytesIO()
        self.headers = {'count': 0, 'content': [{}]}
        self.set_cookies = []

    def basic(self, curl, payload):
        def header_function(header_line):

            match = re.match("^Set-Cookie: (.*)$", header_line.decode('utf8','ignore'))

            if match:
                self.set_cookies.append(match.group(1))

            count = self.headers['count']
            header_line = header_line.decode('iso-8859-1')

            if ':' not in header_line and not header_line.startswith('HTTP'):
                # print(header_line)
                if '\r\n' in header_line:
                    self.headers['count'] += 1
                    self.headers['content'].append({})
                return

            # Break the header line into header name and value.
            if ':' in header_line:
                name, value = header_line.rstrip('\r\n').split(':', 1)
            else:
                name, value = header_line.rstrip('\r\n').split(' ', 1)

            # Remove whitespace that may be present.
            # Header lines include the trailing newline, and there may be whitespace
            # around the colon.
            name = name.strip()
            value = value.strip()

            # Header names are case insensitive.
            # Lowercase name here.
            name = name.lower()

            # Now we can actually record the header name and value.
            if name in self.headers['content'][count]:
                self.headers['content'][count][name].append(value)
            else:
                self.headers['content'][count][name] = [value]

        def write_function(buf):
            size = self.databuf.getbuffer().nbytes
            if size < 4096000:
                self.databuf.write(buf)
                return len(buf)
            return 0

        url = payload.get('effective_url') or payload.get('url')
        if not url.startswith('http'):
            url = 'http://'+url
        curl.setopt(pycurl.URL, url.encode('utf-8'))
        curl.setopt(pycurl.FOLLOWLOCATION, payload.get('followlocation', 1))
        curl.setopt(pycurl.MAXREDIRS, payload.get('maxredirs', 5))

        # c.setopt(pycurl.WRITEHEADER, header_buf)
        headerfunction = payload.get('headerfunction')
        if headerfunction is None:
            curl.setopt(pycurl.HEADERFUNCTION, header_function)
        else:
            curl.setopt(pycurl.HEADERFUNCTION, load(headerfunction))
        writefunction = payload.get('writefunction')
        if writefunction is None:
            curl.setopt(pycurl.WRITEFUNCTION, write_function)
        else:
            curl.setopt(pycurl.WRITEFUNCTION, load(writefunction))
        curl.setopt(pycurl.USERAGENT, payload.get('useragent', self.DEFAULT_USER_AGENT))
        curl.setopt(pycurl.SSL_VERIFYPEER, payload.get('ssl_verifypeer', 0))
        curl.setopt(pycurl.SSL_VERIFYHOST, payload.get('ssl_verifyhost', 0))
        curl.setopt(pycurl.NOSIGNAL, payload.get('nosignal', 1))
        curl.setopt(pycurl.CONNECTTIMEOUT, payload.get('connecttimeout', 8))
        curl.setopt(pycurl.TIMEOUT, payload.get('timeout', 16))
        # curl.setopt(pycurl.DNS_CACHE_TIMEOUT, payload.get('dns_cache_timeout', 360))
        # c.setopt(pycurl.DNS_USE_GLOBAL_CACHE, p.get('dns_use_global_cache', 1))

        proxy_type = payload.get('proxytype')
        proxy = payload.get('proxy')
        proxy_port = payload.get('proxyport')
        proxy_userpwd = payload.get('proxyuserpwd')
        if proxy:
            curl.setopt(pycurl.PROXY, proxy)
        if proxy_port:
            curl.setopt(pycurl.PROXYPORT, proxy_port)
        if proxy_userpwd:
            curl.setopt(pycurl.PROXYUSERPWD, proxy_userpwd)
        if proxy_type:
            if '4' in proxy_type:
                proxy_type = pycurl.PROXYTYPE_SOCKS4A
            elif '5' in proxy_type:
                proxy_type = pycurl.PROXYTYPE_SOCKS5_HOSTNAME
            else:
                proxy_type = pycurl.PROXYTYPE_HTTP
            curl.setopt(pycurl.PROXYTYPE, proxy_type)
        # if share:
        #     c.setopt(pycurl.SHARE, share)

        cookies = payload.get('cookies')
        if cookies:
            # print(cookies,'.......'*20)
            for cookie in cookies:
                res = get_tld(url, as_object=True)
                cookie_str = '\t'.join([res.tld, "FALSE", "/", "FALSE", "0", cookie[0], cookie[1]])
                # print(cookie_str,'?????')
                curl.setopt(pycurl.COOKIELIST, cookie_str)

    def method_get(self, curl, payload):
        self.basic(curl, payload)
        httpheader = payload.get('httpheader')
        if httpheader:
            curl.setopt(curl.HTTPHEADER, httpheader)
        return curl

    def method_post(self, curl, payload):
        self.basic(curl, payload)
        httpheader = payload.get('httpheader', ['Accept: application/json', "Content-type: application/json"])
        if httpheader:
            # curl.setopt(pycurl.HEADER, p.get('header', 1))
            curl.setopt(pycurl.HTTPHEADER, httpheader)
        post301 = getattr(pycurl, 'POST301', None)
        if post301 is not None:
            # Added in libcurl 7.17.1.
            curl.setopt(post301, True)
        curl.setopt(pycurl.POST, 1)
        postfields = payload.get('postfields')
        if postfields:
            postfields = json.dumps(postfields, indent=2, ensure_ascii=False)
            curl.setopt(pycurl.POSTFIELDS, postfields)
        return curl
