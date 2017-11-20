#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
    agent.util.ftp
    ~~~~~~~~~~~~

    This module provide the ftp client.

    :copyright: (c) 2017 by Ma Fei.
"""
import sys
import os
from ftplib import FTP


class FTPClient(object):
    def __init__(self):
        self.ftp = None
        self.ip = '10.12.38.246'
        self.uname = 'elemeqa'
        self.pwd = 'eleme517517'
        self.port = 2121
        self.timeout = 60

    def init_env(self):
        if self.ftp is None:
            self.ftp = FTP()
            print '### connect ftp server: %s ...' % self.ip
            self.ftp.connect(self.ip, self.port, self.timeout)
            self.ftp.login(self.uname, self.pwd)
            print self.ftp.getwelcome()

    def clear_env(self):
        if self.ftp:
            self.ftp.close()
            print '### disconnect ftp server: %s!' % self.ip
            self.ftp = None

    def upload_dir(self, localdir='./', remotedir='./'):
        if not os.path.isdir(localdir):
            return
        self.ftp.cwd(remotedir)
        for file in os.listdir(localdir):
            src = os.path.join(localdir, file)
            if os.path.isfile(src):
                self.upload_file(src, file)
            elif os.path.isdir(src):
                try:
                    self.ftp.mkd(file)
                except Exception:
                    sys.stderr.write('the dir is exists %s' % file)
                self.upload_dir(src, file)
        self.ftp.cwd('..')

    def upload_file(self, localpath, remotepath='./'):
        if not os.path.isfile(localpath):
            return
        print '+++ upload %s to %s:%s' % (localpath, self.ip, remotepath)
        self.ftp.storbinary('STOR ' + remotepath, open(localpath, 'rb'))

    def upload(self, localdir, remotedir):
        print(localdir)
        print(remotedir)
        self.init_env()
        try:
            self.ftp.mkd(remotedir)
        except Exception as e:
            print(e.message)
        self.upload_dir(localdir, remotedir)
        self.clear_env()
