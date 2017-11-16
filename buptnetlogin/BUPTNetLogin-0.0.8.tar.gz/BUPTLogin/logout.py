# !/usr/bin/env python3
# -*- coding: utf-8 -*-
from urllib import request

from bs4 import BeautifulSoup

__author__ = 'ingbyr'
__email__ = 'admin@ingbyr.com'


def show_result(content):
    soup = BeautifulSoup(content, 'lxml')
    info = soup.title.string
    if u'信息返回窗' == info:
        print('>>> Logout successfully!')
    else:
        print('Error! Failed to logout.')


def logout():
    logout_url = 'http://10.3.8.211/F.htm'
    # send request
    req = request.Request(logout_url)
    req.add_header('User-Agent',
                   'Mozilla/6.0 (iPhone; CPU iPhone OS 8_0 like Mac OS X) AppleWebKit/536.26 (KHTML, like Gecko) Version/8.0 Mobile/10A5376e Safari/8536.25')
    with request.urlopen(req) as f:
        show_result(f.read())


if __name__ == '__main__':
    logout()
