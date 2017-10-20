#!/usr/local/bin/python
# -*- coding:utf-8 -*-
"""    
    2017/9/6  WeiYanfeng
    公共函数 包

~~~~~~~~~~~~~~~~~~~~~~~~
共函数 包
~~~~~~~~~~~~~~~~~~~~~~~~
# 依赖包 Package required
# pip install redis

"""
# WeiYF.20170605 经测试，Python3引用当前目录下的源码文件，文件名前要加`.`点号
# 同时这样的写法也可以在Python2.7下使用。
import sys
# sys.path.append('.')  # 经测试，这种写法在Python3下不行

from .SftpTools.CSFtpDownloadDel import CSFtpDownloadDel
from .SftpTools.CSFtpUploadBakup import CSFtpUploadBakup
from .SftpTools.CSFtpUploadBakYMD import CSFtpUploadBakYMD
from .FtpTools.CFtpUploadBakYMD import CFtpUploadBakYMD

