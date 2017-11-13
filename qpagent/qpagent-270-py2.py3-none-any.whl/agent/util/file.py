#!/usr/bin/env python
# -*- coding: utf-8 -*-
import os
import zipfile
import urllib2

from agent.util.sentry import Sentry

sentry = Sentry()


# 打包目录为zip文件（未压缩）
def make_zip(source_dir, output_filename):
    zipf = zipfile.ZipFile(output_filename, 'w')
    pre_len = len(os.path.dirname(source_dir))
    for parent, dirnames, filenames in os.walk(source_dir):
        for filename in filenames:
            pathfile = os.path.join(parent, filename)
            arcname = pathfile[pre_len:].strip(os.path.sep)  # 相对路径
            zipf.write(pathfile, arcname)
    zipf.close()


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
    try:
        if os.path.isdir(path):
            pass
        else:
            os.makedirs(path)
        return path
    except Exception:
        sentry.client.captureException()
