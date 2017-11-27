import json
import re

import pycurl
from bs4 import UnicodeDammit

from netboy.util.makeup import Makeup
from netboy.util.soup import Soup


def safe_cn_charset(charset):
    CHARSET_LIST = ["utf8", "gb2312", "gbk", "big5", "gb18030"]
    charset = charset.lower()
    charset = charset.replace('-', '')
    charset = charset.replace('_', '')
    if charset.endswith('18030'):
        return 'gb18030'
    if charset.endswith('2312'):
        return 'gb2312'
    if charset in CHARSET_LIST:
        return charset
    return 'utf8'


class Result:
    def __init__(self, setup=None):
        self.setup = setup

    def response(self, payload, response, json_data=False):
        if not self.setup:
            return None
        charset = payload.get('charset')
        body = self.setup.databuf.getvalue()
        if charset:
            data = body.decode(charset, 'ignore')
        else:
            if len(body) == 0:
                data = ''
                charset = 'utf-8'
            elif 'content-type' in self.setup.headers:
                content_type = self.setup.headers['content-type'].lower()
                match = re.search('charset=([a-zA-Z\-_0-9]+)', content_type)
                if match:
                    charset = match.group(1)

                charset = safe_cn_charset(charset)
                data = body.decode(charset, 'ignore')

            else:
                utf8_data = body.decode('utf8', 'ignore')
                match = re.search('charset=([a-zA-Z\-_0-9]+)', utf8_data)
                if match:
                    charset = match.group(1)
                    charset = safe_cn_charset(charset)
                    data = body.decode(charset, 'ignore')
                else:
                    data, charset = Makeup.beautify(body)

                    # if charset is None:
                    #     dammit = UnicodeDammit(body, ["utf-8", "gb2312", "gbk", "big5", "gb18030"], smart_quotes_to="html")
                    #     data = dammit.unicode_markup
                    #     charset = dammit.original_encoding
                    # else:
                    #     data = body.decode(charset, 'ignore')
        # headers.remove({})
        self.setup.headers['content'] = [h for h in self.setup.headers['content'] if len(h) > 0]
        sp_lxml = Soup(data, 'lxml')
        sp_html = Soup(data, 'html.parser')
        response.update({
            'url': payload.get('url'),
            'title': sp_lxml.get_title(),
            'links': sp_lxml.get_links(),
            'links2': sp_lxml.get_links2(),
            'metas': sp_lxml.get_metas(),
            'images': sp_lxml.get_images(),
            'scripts': sp_lxml.get_scripts(),
            'text': sp_html.get_text(),
            'data': json.loads(data) if json_data else data,
            'headers': self.setup.headers,
            'charset': charset,
            'spider': 'pycurl',
            'payload': payload,
            'mode': payload.get('mode'),
            'cookies': self.setup.set_cookies
        })
        return response

    def result(self, curl, state='normal', resp=None):
        effective_url = curl.getinfo(pycurl.EFFECTIVE_URL)
        primary_ip = curl.getinfo(pycurl.PRIMARY_IP)
        primary_port = curl.getinfo(pycurl.PRIMARY_PORT)
        local_ip = curl.getinfo(pycurl.LOCAL_IP)
        local_port = curl.getinfo(pycurl.LOCAL_PORT)
        speed_download = curl.getinfo(pycurl.SPEED_DOWNLOAD)
        size_download = curl.getinfo(pycurl.SIZE_DOWNLOAD)
        redirect_time = curl.getinfo(pycurl.REDIRECT_TIME)
        redirect_count = curl.getinfo(pycurl.REDIRECT_COUNT)
        redirect_url = curl.getinfo(pycurl.REDIRECT_URL)
        http_code = curl.getinfo(pycurl.HTTP_CODE)
        response_code = curl.getinfo(pycurl.RESPONSE_CODE)
        total_time = curl.getinfo(pycurl.TOTAL_TIME)
        content_type = curl.getinfo(pycurl.CONTENT_TYPE)
        info_filetime = curl.getinfo(pycurl.INFO_FILETIME)
        http_connectcode = curl.getinfo(pycurl.HTTP_CONNECTCODE)
        connect_time = curl.getinfo(pycurl.CONNECT_TIME)
        namelookup_time = curl.getinfo(pycurl.NAMELOOKUP_TIME)
        starttransfer_time = curl.getinfo(pycurl.STARTTRANSFER_TIME)
        pretransfer_time = curl.getinfo(pycurl.PRETRANSFER_TIME)
        redirect_time = curl.getinfo(pycurl.REDIRECT_TIME)
        header_size = curl.getinfo(pycurl.HEADER_SIZE)
        request_size = curl.getinfo(pycurl.REQUEST_SIZE)
        ssl_verifyresult = curl.getinfo(pycurl.SSL_VERIFYRESULT)
        num_connects = curl.getinfo(pycurl.NUM_CONNECTS)
        content_length_download = curl.getinfo(pycurl.CONTENT_LENGTH_DOWNLOAD)
        cookielist = curl.getinfo(pycurl.INFO_COOKIELIST)

        httpauth_avail = curl.getinfo(pycurl.HTTPAUTH_AVAIL)
        proxyauth_avail = curl.getinfo(pycurl.PROXYAUTH_AVAIL)
        os_errno = curl.getinfo(pycurl.OS_ERRNO)
        ssl_engines = curl.getinfo(pycurl.SSL_ENGINES)
        lastsocket = curl.getinfo(pycurl.LASTSOCKET)
        ftp_entry_path = curl.getinfo(pycurl.FTP_ENTRY_PATH)

        ret = {
            'effective_url': effective_url,
            'primary_ip': primary_ip,
            'primary_port': primary_port,
            'local_ip': local_ip,
            'local_port': local_port,
            'speed_download': speed_download,
            'size_download': size_download,
            'redirect_time': redirect_time,
            'redirect_count': redirect_count,
            'redirect_url': redirect_url,
            'http_code': http_code,
            'response_code': response_code,
            'total_time': total_time,
            'content_type': content_type,
            'namelookup_time': namelookup_time,
            'info_filetime': info_filetime,
            'connect_time': connect_time,
            'http_connectcode': http_connectcode,
            'starttransfer_time': starttransfer_time,
            'pretransfer_time': pretransfer_time,
            'header_size': header_size,
            'request_size': request_size,
            'ssl_verifyresult': ssl_verifyresult,
            'num_connects': num_connects,
            'content_length_download': content_length_download,
            'cookielist': cookielist,
            'ssl_engines': ssl_engines,
            'httpauth_avail': httpauth_avail,
            'proxyauth_avail': proxyauth_avail,
            'os_errno': os_errno,
            'ssl_engines': ssl_engines,
            'lastsocket': lastsocket,
            'ftp_entry_path': ftp_entry_path,
            'spider': 'pycurl',
            'state': state,
            'error_code': None,
            'error_desc': None
        }
        if resp:
            ret.update(resp)
        return ret
