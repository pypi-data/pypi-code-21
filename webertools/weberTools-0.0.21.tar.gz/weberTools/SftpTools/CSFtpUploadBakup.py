#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
__createTime__ = "2017/9/8 16:42"
__author__ = "WeiYanfeng"
__email__ = "weber.juche@gmail.com"
__version__ = "0.0.1"
        
~~~~~~~~~~~~~~~~~~~~~~~~
程序单元功能描述
将本地文件推送到远程主机，并移到本地另外一目录下备份。
参考 [SFTP — Paramiko documentation](http://docs.paramiko.org/en/2.2/api/sftp.html)
~~~~~~~~~~~~~~~~~~~~~~~~
# 依赖包 Package required
# pip install weberFuncs
# pip install paramiko
"""
import sys
from weberFuncs import PrintTimeMsg, GetTimeInteger  # , GetFileSizeModTime
import os
import time
import stat
import paramiko


class CSFtpUploadBakup:
    """
    上传本地文件到SSH主机，上传成功后，将本地文件移到另外一个目录备份。
    即“上传备份”，达到将文件上传到SSH主机的目的。
    """
    def __init__(self, dictHPUP):
        sHostPort = '%s:%s' % (dictHPUP.get('host', ''), dictHPUP.get('port', '0'))
        PrintTimeMsg('CSFtpCopyToHost.connect(%s)...' % sHostPort)
        try:
            self.ssh = paramiko.SSHClient()
            self.ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
            self.ssh.connect(hostname=dictHPUP.get('host', ''),
                             port=int(dictHPUP.get('port', '0')),
                             username=dictHPUP.get('user', ''),
                             password=dictHPUP.get('pass', ''))
        except Exception as e:
            PrintTimeMsg('CSFtpCopyToHost.connect.Error=(%s)' % str(e))
            sys.exit(-101)
        if not self.ssh:
            PrintTimeMsg('CSFtpCopyToHost.connect.ssh=(%s)' % self.ssh)
            sys.exit(-1)
        self.sftp = self.ssh.open_sftp()
        self.sHintFileName = ''
        self.listDirToMove = []  # 要上传备份的目录列表，内容是 (sRemoteDir, sLocalDir)

    def __del__(self):
        if hasattr(self, 'sftp'):
            self.sftp.close()
        if hasattr(self, 'ssh'):
            self.ssh.close()
        PrintTimeMsg('CSFtpCopyToHost.__del__')

    def callbackStatus(self, iTransfer, iTotal):
        PrintTimeMsg("  %s=(%s/%s)" % (self.sHintFileName, iTransfer, iTotal))

    def sftpUploadBakupFile(self, sFileName, sDirRemote, sDirLocal, sDirBakup):
        # 从上传一个文件到主机，并移到本地备份目录下。目录结尾没有分隔符
        sFN = sFileName
        self.sHintFileName = 'put(%s/%s)' % (sDirRemote, sFN)
        sR = sDirRemote + '/' + sFN
        sT = sR + '.filepart'  # 临时文件
        sL = sDirLocal + os.path.sep + sFN
        sB = sDirBakup + os.path.sep + sFN
        PrintTimeMsg("sftpUploadBakupFile(%s)..." % self.sHintFileName)
        try:
            tmBegin = time.time()
            self.sftp.put(sL, sT, self.callbackStatus)
            self.sftp.rename(sT, sR)  # 主机文件更名
            os.rename(sL, sB)  # 本地文件更名
        except Exception as e:
            PrintTimeMsg('sftpUploadBakupFile.put(%s,%s,%s).Error=(%s)' % (
                sFN, sDirRemote, sDirLocal, str(e)))
            sys.exit(-102)
        else:
            tmConsume = time.time() - tmBegin
            PrintTimeMsg("sftpUploadBakupFile(%s)=OK,tmConsume=%.1fs!" % (
                sFN, tmConsume))

    def sftpUploadBakupDir(self, sDirRemote, sDirLocal, sDirBakup):
        # 从本地上传到服务端并备份，遇到子目录则纳入队列
        try:
            self.sftp.stat(sDirRemote)
        except IOError as e:
            self.sftp.mkdir(sDirRemote)
        if not os.path.exists(sDirBakup):
            os.mkdir(sDirBakup)
        lsDir = os.listdir(sDirLocal)
        PrintTimeMsg("sftpUploadBakupDir.listdir(%s).len=%s=" % (sDirLocal, len(lsDir)))
        for sDir in lsDir:
            sL = sDirLocal + os.path.sep + sDir
            if os.path.isfile(sL):  # 一般文件
                s = os.stat(sL)
                if GetTimeInteger() - int(s.st_mtime) >= 60*5:  # 仅上传5分钟前的
                    self.sftpUploadBakupFile(sDir, sDirRemote, sDirLocal, sDirBakup)
            elif os.path.isdir(sL):  # 目录
                self.listDirToMove.append((sDirRemote + '/' + sDir,
                                           sL, sDirBakup + os.path.sep + sDir))
                PrintTimeMsg("sftpUploadBakupDir.listDirToMove.append(%s)!" % sL)
            else:  # 其它
                PrintTimeMsg("sftpUploadBakupDir(%s): %s=OTHER" % (sDirLocal, sDir))

    def StartUploadBakupDir(self, sDirRemote, sDirLocal, sDirBakup):
        # 开始上传本地文件到服务端，并其所有子目录纳入队列
        self.listDirToMove = [(sDirRemote, sDirLocal, sDirBakup)]
        while len(self.listDirToMove) > 0:
            (sR, sL, sB) = self.listDirToMove.pop(0)
            self.sftpUploadBakupDir(sR, sL, sB)


def mainCSFtpUploadBakup():
    dictHPUP = {
        # 'host': '127.0.0.1',
        'host': '180.200.2.36',
        'port': 22,
        'user': 'root',
        'pass': '123456',
    }
    o = CSFtpUploadBakup(dictHPUP)
    sFileName = '1.ts'
    sDirRemote = '/tmp/1'
    sDirLocal = r'D:\WeberWork\ArchitectRoot\WeiYF\GitRoot\BitBucket\WeberSrcRootPrj\Python\Maywide\ImageRecognition\testdata\tmp'
    sDirBakup = r'D:\WeberWork\ArchitectRoot\WeiYF\GitRoot\BitBucket\WeberSrcRootPrj\Python\Maywide\ImageRecognition\testdata\bak'
    # o.sftpUploadBakupFile(sFileName, sDirRemote, sDirLocal, sDirBakup)
    o.StartUploadBakupDir(sDirRemote, sDirLocal, sDirBakup)

# --------------------------------------
if __name__ == '__main__':
    mainCSFtpUploadBakup()
