#!/usr/bin/python
# -*- coding: utf-8 -*-

ERROR_ITEMS = {
    426: u'请求过于频繁',
    408: u'请求超时',
    405: u'请求方式错误',
    500: u'服务器错误',
    404: u'路径错误',
    502: u'网关错误'
}


class XClientError(Exception):
    def __init__(self, code):
        self.code = code
        self.msg = ERROR_ITEMS[code]

    def __str__(self):
        return u'the request is fail.error msg {}, status code: {}'.format(self.msg, self.code)



