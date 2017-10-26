#!/usr/bin/env python
# -*- coding: UTF-8 -*-

import time
import re
import hashlib
import httplib
import urllib
import urllib2
import socket
import StringIO
import json
import gzip

import define
from CoralResultSet import CoralResultSet

class CoralDBClient(object):
    """
    CoralDB Client
    Usage:
    >>> client = CoralDBClient("coraldb://127.0.0.1:80")
    >>> client.login("test", "123456")
    """
    def __init__(self, address):
        # url = 'coraldb://test:123456@localhost:8086'
        p = re.compile(r"""^coraldb://(([^:]*)?(:[^@]*)?@)?([^:]+):(\d+)$""", re.IGNORECASE)
        m = p.match(address)
        if not m:
            raise Exception('illegal CoralDB address: ' + address)
        self.username = m.group(2)
        self.password = m.group(3)[1:] if m.group(3) else None
        if self.password:
            md5 = hashlib.md5()
            md5.update(self.password)
            self.password = md5.hexdigest()
        self._host = m.group(4)
        self._port = int(m.group(5))
        self._token = None
        self.timeout = 60
        self.compress = False

    def login(self, username=None, password=None):
        """
        login: 登陆
        :param username: 用户名
        :param password: 密码
        :return: None
        :exception: 登陆失败抛出异常
        """
        if username is not None:
            self.username = username
        if password is not None:
            md5 = hashlib.md5()
            md5.update(password)
            self.password = md5.hexdigest()
        params = {'u': self.username, 'p': self.password}
        rep = self.__request('login', params, login=True)
        if rep.get('ret_code') == 0:
            self._token = rep['token']
        return CoralResultSet()

    def changePwd(self, password):
        """
        changePwd: 修改密码
        :param password: 新密码
        :return: None
        :exception 失败报出异常
        """
        if password is None or password == "":
            raise Exception('new password can not be empty')
        params = {'p': self.password, 'newPwd': password, 'token': self._token}
        self.__request('changePwd', params)
        return CoralResultSet()

    def getTradingDays(self, beginDate=0, endDate=0, market=define.SH):
        """
        getTradingDays: 获取交易日序列
        :param beginDate: 开始日期，默认为系统支持的最早交易日，示例：20161205
        :param endDate: 结束日期，默认为系统支持的最晚交易日，示例：20161206
        :param market: 市场，默认为上海
        :return: 交易日列表
        """
        params = {'beginDate': beginDate, 'endDate': endDate, 'market': market}
        rep = self.__request('getTradingDays', params)
        return CoralResultSet(rep['columns'], rep['values'])

    def getStat(self, beginDate=0, endDate=0):
        """
        getStat: 获取数据统计信息
        :param beginDate: 开始日期，默认为系统中存在数据的最早日期，示例：20161205
        :param endDate: 结束日期，默认为系统中存在数据的最晚日期，示例：20161206
        :return: 结果集
        """
        params = {'beginDate': beginDate, 'endDate': endDate}
        rep = self.__request('getStat', params)
        return CoralResultSet(rep['columns'], rep['values'])

    def getCode(self, sector='', date=0, fields="*"):
        """
        getCode: 获取系统内置板块信息
        :param sector: 板块名称，多个名称用逗号分隔，默认获取所有板块
        :param date: 数据日期，默认为每只证券最新日期的数据，示例：20161205
        :param fields: 字段名，多个字段逗号分隔，默认为所有字段
        :return: 结果集
        """
        params = {'sector': sector, 'date': date, 'fields': fields}
        rep = self.__request('getCode', params)
        return CoralResultSet(rep['columns'], rep['values'])

    def getBar(self, code=[], beginDate=0, endDate=0, cycle=0, fields="*", beginTime=0, endTime=0, holo=False, holoInterval=0):
        """
        getBar: 获取行情数据
        :param code: 证券代码或证券代码列表
        :param beginDate: 开始日期，默认为今天，示例：20161205
        :param endDate: 结束日期，默认等于开始日期，示例：20161206
        :param cycle: 周期，默认为原始数据
        :param fields: 字段名，多个字段逗号分隔，默认为所有字段
        :param beginTime: 开始时间，默认为当天开始，示例：93000
        :param endTime: 结束时间，默认为当天结束，示例：150000
        :param holo: 是否查全息快照表，默认查Level2快照表
        :param holoInterval: 全息快照时间间隔，默认为1000毫秒
        :return: 结果集
        """
        if not code:
            raise Exception("code cannot be empty")
        code = ','.join(code if isinstance(code, list) else [code])
        params = {'code': code, 'beginDate': beginDate, 'endDate': endDate, 'cycle': cycle, 'fields': fields,
                  'beginTime': beginTime, 'endTime': endTime, 'holo': holo, 'holoInterval': holoInterval}
        rep = self.__request('getBar', params)
        return CoralResultSet(rep['columns'], rep['values'])

    def getOrder(self, code=[], beginDate=0, endDate=0, fields="*", beginTime=0, endTime=0):
        """
        getOrder: 获取逐笔委托数据
        :param code: 证券代码或证券代码列表
        :param beginDate: 开始日期，默认为今天，示例：20161205
        :param endDate: 结束日期，默认等于开始日期，示例：20161206
        :param fields: 字段名，多个字段逗号分隔，默认为所有字段
        :param beginTime: 开始时间，默认为当天开始，示例：93000
        :param endTime: 结束时间，默认为当天结束，示例：150000
        :return: 结果集
        """
        if not code:
            raise Exception("code cannot be empty")
        code = ','.join(code if isinstance(code, list) else [code])
        params = {'code': code, 'beginDate': beginDate, 'endDate': endDate, 'fields': fields,
                  'beginTime': beginTime, 'endTime': endTime}
        rep = self.__request('getOrder', params)
        return CoralResultSet(rep['columns'], rep['values'])

    def getKnock(self, code=[], beginDate=0, endDate=0, fields="*", beginTime=0, endTime=0):
        """
        getOrder: 获取逐笔委托数据
        :param code: 证券代码或证券代码列表
        :param beginDate: 开始日期，默认为今天，示例：20161205
        :param endDate: 结束日期，默认等于开始日期，示例：20161206
        :param fields: 字段名，多个字段逗号分隔，默认为所有字段
        :param beginTime: 开始时间，默认为当天开始，示例：93000
        :param endTime: 结束时间，默认为当天结束，示例：150000
        :return: 结果集
        """
        if not code:
            raise Exception("code cannot be empty")
        code = ','.join(code if isinstance(code, list) else [code])
        params = {'code': code, 'beginDate': beginDate, 'endDate': endDate, 'fields': fields,
                  'beginTime': beginTime, 'endTime': endTime}
        rep = self.__request('getKnock', params)
        return CoralResultSet(rep['columns'], rep['values'])

    def getNotice(self, code=[], beginDate=0, endDate=0, fields="*", keywords=""):
        """
        getNotice: 获取股票公告
        :param code: 证券代码或证券代码列表
        :param beginDate: 开始日期，默认为今天，示例：20161205
        :param endDate: 结束日期，默认等于开始日期，示例：20161206
        :param fields: 字段名，多个字段逗号分隔，默认为所有字段
        :param keywords: 关键词，多个关键词用空格分割
        :return: 
        """
        code = ','.join(code if isinstance(code, list) else [code])
        params = {'beginDate': beginDate, 'endDate': endDate, 'code': code, 'fields': fields, 'keywords': keywords}
        rep = self.__request('getNotice', params)
        return CoralResultSet(rep['columns'], rep['values'])

    def getOptionBaseInfo(self, code=[], beginDate=0, endDate=0, fields="*"):
        """
        getOptionBaseInfo: 获取期权基础信息
        :param code: 证券代码或证券代码列表
        :param beginDate: 开始日期，默认为今天，示例：20161205
        :param endDate: 结束日期，默认等于开始日期，示例：20161206
        :param fields: 字段名，多个字段逗号分隔，默认为所有字段
        :return: 
        """
        code = ','.join(code if isinstance(code, list) else [code])
        params = {'beginDate': beginDate, 'endDate': endDate, 'code': code, 'fields': fields}
        rep = self.__request('getOptionBaseInfo', params)
        return CoralResultSet(rep['columns'], rep['values'])

    def __request(self, path, params=None, data=None, login=False):
        """
        """
        if params is None:
            params = {}
        if self._token:
            params['token'] = self._token
        for k, v in params.iteritems():
            if isinstance(v, unicode):
                params[k] = v.encode('UTF-8')
        url = 'http://%s:%s/%s?%s' % (self._host, self._port, path, urllib.urlencode(params))
        headers = {'User-Agent': 'PyCoralDB/1.1'}
        if self.compress:
            headers['Accept-Encoding'] = 'gzip'
        # Try to send the request a maximum of three times.
        for i in xrange(0, 3):
            try:
                req = urllib2.Request(url, data=data, headers=headers)
                f = urllib2.urlopen(req, timeout=10 if login else self.timeout)
                html = f.read()
                encoding = f.info().get('Content-Encoding')
                if encoding == 'gzip':
                    buf = StringIO.StringIO(html)
                    zf = gzip.GzipFile(fileobj=buf)
                    html = zf.read()
                    zf.close()
                rep = json.loads(html)
                if rep.get('ret_code') != 0:
                    err = '%s failed: %s-%s' % (path, rep.get('ret_code'), rep.get('ret_msg'))
                    raise Exception(err.encode('UTF-8'))
                return rep
            except urllib2.URLError, e:
                if not login and e.reason == 'Unauthorized':
                    self.login()
                    if self._token:
                        params['token'] = self._token
                    url = 'http://%s:%s/%s?%s' % (self._host, self._port, path, urllib.urlencode(params))
                    login = True
                    continue
                elif e.reason == 'Too Many Requests':
                    time.sleep(10)
                    continue
                elif i < 2 and e.reason not in ['Forbidden', 'Bad Request']:
                    time.sleep(5)
                    continue
                else:
                    raise e
            except socket.timeout, e:
                if i >= 2:
                    raise e
            except socket.error, e:
                time.sleep(5)
                if i >= 2:
                    raise e
            except httplib.UnknownProtocol, e:
                time.sleep(5)
                if i >= 2:
                    raise e
        return None

if __name__ == '__main__':
    client = CoralDBClient('coraldb://127.0.0.1:5166')
    client.timeout = 5
    client.login("test", "123456")
    print client.getTradingDays()
