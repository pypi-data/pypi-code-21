#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
__createTime__ = "2017/8/24 16:29"
__author__ = "WeiYanfeng"
__email__ = "weber.juche@gmail.com"
__version__ = "0.0.1"
        
~~~~~~~~~~~~~~~~~~~~~~~~
程序单元功能描述
Program description
~~~~~~~~~~~~~~~~~~~~~~~~
# 依赖包 Package required
# pip install weberFuncs

"""
from .WyfPublicFuncs import IsPython3, PrintTimeMsg
import time

# def HttpGet(sUrl):
#     import urllib2
#     return urllib2.urlopen(sUrl).read()


def HttpGet(sUrl,iTimeOut=60):
    import urllib2
    try:
        response = urllib2.urlopen(sUrl, timeout=iTimeOut)
        return response.read()
    except Exception as e:
        PrintTimeMsg('HttpGet.Exception=%s' % str(e))
        raise Exception(e) # WeiYF.20160222 继续触发该异常
        # return ''
        # return urllib2.urlopen(sUrl,data=None, timeout=timeout).read()
        # return urllib2.urlopen(sUrl).read()


def HttpPostJson(sUrl,sData):
    import urllib2
    req = urllib2.Request(sUrl)
    req.add_header('Content-Type', 'application/json')
    req.add_header('encoding', 'utf-8')
    return urllib2.urlopen(req, sData).read()


def RequestsHttpGet(sUrl, jsonData={}, authTuple=(), timeout=60, sUserAgent=''):
    import requests
    headers = {
        # 'content-type': 'application/json',
        # 'encoding': 'utf-8',
        'Accept': '*/*',
        'Accept-Encoding': 'gzip, deflate',
        'Accept-Language': 'zh-CN,zh;q=0.8',
    }
    if sUserAgent:
        headers['User-Agent'] = sUserAgent
    r = requests.get(sUrl, params=jsonData, headers=headers, auth=authTuple, timeout=timeout)
    return r.status_code, r.text  # r.json()


def RequestsHttpPost(sUrl, jsonData, timeout=60, sUserAgent=''):
    import requests
    headers = {
        'content-type': 'application/json',
        'encoding': 'utf-8',
    }
    if sUserAgent:
        headers['User-Agent'] = sUserAgent
    r = requests.post(sUrl, data=jsonData, headers=headers, timeout=timeout)
    return r.status_code, r.text # r.json()


def RequestsHttpPostForm(sUrl, jsonData, timeout=60, sUserAgent=''):
    import requests
    headers = {
        'content-type': 'application/x-www-form-urlencoded',
        'encoding': 'utf-8',
    }
    if sUserAgent:
        headers['User-Agent'] = sUserAgent
    r = requests.post(sUrl, data=jsonData, headers=headers, timeout=timeout)
    return r.status_code, r.text  # r.json()


def RequestsHttpPostFormData(sUrl, jsonData, timeout=60, sUserAgent=''):
    import requests
    headers = {
        'content-type': 'multipart/form-data',
        'encoding': 'utf-8',
    }
    if sUserAgent:
        headers['User-Agent'] = sUserAgent
    r = requests.post(sUrl, data=jsonData, headers=headers, timeout=timeout)
    return r.status_code, r.text  # r.json()


def RequestsDownLoad(sUrl, sFileNameOut, jsonData={}, authTuple=(), timeout=60, sUserAgent=''):
    import requests
    headers = {
        # 'content-type': 'application/json',
        # 'encoding': 'utf-8',
        'Accept': '*/*',
        'Accept-Encoding': 'gzip, deflate',
        'Accept-Language': 'zh-CN,zh;q=0.8',
    }
    if sUserAgent:
        headers['User-Agent'] = sUserAgent
    tmBegin = time.time()
    r = requests.get(sUrl, params=jsonData, headers=headers, auth=authTuple, timeout=timeout)
    tmConsume = time.time() - tmBegin
    PrintTimeMsg('RequestsDownLoad(%s)=%s,tmConsume=%.1fs!' % (sUrl, r.status_code, tmConsume))
    if r.status_code == 200:
        with open(sFileNameOut, 'wb') as fd:
            for chunk in r.iter_content(chunk_size=512):
                fd.write(chunk)
    return r.status_code
