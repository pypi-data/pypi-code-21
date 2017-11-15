#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
    agent.util.file
    ~~~~~~~~~~~~

    This module provide the file tool.

    :copyright: (c) 2017 by Ma Fei.
"""
import os
import urllib2

from agent.util.sentry import Sentry

sentry = Sentry()


def get_download_url(url):
    """
    获取跳转后的真实下载链接
    :param url: 页面中的下载链接
    :return: 跳转后的真实下载链接
    """
    req = urllib2.Request(url)
    req.add_header('User-Agent', 'Mozilla/5.0 (Windows NT 6.1; WOW64; Trident/7.0; rv:11.0) like Gecko')
    response = urllib2.urlopen(req)
    dlurl = response.geturl()  # 跳转后的真实下载链接
    return dlurl


def download_file(dlurl):
    """
    从真实的下载链接下载文件
    :param dlurl: 真实的下载链接
    :return: 下载后的文件
    """
    req = urllib2.Request(dlurl)
    req.add_header('User-Agent', 'Mozilla/5.0 (Windows NT 6.1; WOW64; Trident/7.0; rv:11.0) like Gecko')
    response = urllib2.urlopen(req)
    return response.read()


def save_file(dlurl, dlfolder, filename):
    """
    把下载后的文件保存到下载目录
    :param filename:
    :param dlurl: 真实的下载链接
    :param dlfolder: 下载目录
    :return: None
    """
    if os.path.isdir(dlfolder):
        pass
    else:
        os.makedirs(dlfolder)
    os.chdir(dlfolder)  # 跳转到下载目录
    # filename = dlurl.split('/')[-1]  # 获取下载文件名
    dlfile = download_file(dlurl)
    with open(filename, 'wb') as f:
        f.write(dlfile)
        f.close()
    return None


def make_worker_dir(path):
    if os.path.isdir(path):
        pass
    else:
        os.makedirs(path)
    return path
