#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
__createTime__ = "2017/9/5 16:42"
__author__ = "WeiYanfeng"
__email__ = "weber.juche@gmail.com"
__version__ = "0.0.1"
        
~~~~~~~~~~~~~~~~~~~~~~~~
程序单元功能描述
从远程主机下载文件并删除。
参考 [SFTP — Paramiko documentation](http://docs.paramiko.org/en/2.2/api/sftp.html)
~~~~~~~~~~~~~~~~~~~~~~~~
# 依赖包 Package required
# pip install weberFuncs
# pip install paramiko
"""
import sys
from weberFuncs import PrintTimeMsg
import os
import time
import stat
import paramiko


class CSFtpDownloadDel:
    """
    从SSH主机主机下载文件文件，下载成功后，删除主机上的文件。
    即“下载移除”，达到将文件从SSH主机“移动”到本地的目的。
    """
    def __init__(self, dictHPUP, sExtTail=''):
        sHostPort = '%s:%s' % (dictHPUP.get('host', ''), dictHPUP.get('port', '0'))
        PrintTimeMsg('CSFtpDownloadDel.connect(%s)...' % sHostPort)
        try:
            self.ssh = paramiko.SSHClient()
            self.ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
            self.ssh.connect(hostname=dictHPUP.get('host', ''),
                             port=int(dictHPUP.get('port', '0')),
                             username=dictHPUP.get('user', ''),
                             password=dictHPUP.get('pass', ''))
        except Exception as e:
            PrintTimeMsg('CSFtpDownloadDel.connect.Error=(%s)' % str(e))
            sys.exit(-101)
        if not self.ssh:
            PrintTimeMsg('CSFtpDownloadDel.connect.ssh=(%s)' % self.ssh)
            sys.exit(-1)
        self.sExtTail = sExtTail
        PrintTimeMsg('CSFtpDownloadDel.sExtTail=%s=' % self.sExtTail)
        self.sftp = self.ssh.open_sftp()
        self.sHintFileName = ''
        self.listDirToMove = []  # 要下载删除的目录列表，内容是 (sRemoteDir, sLocalDir)

    def __del__(self):
        if hasattr(self, 'sftp'):
            self.sftp.close()
        if hasattr(self, 'ssh'):
            self.ssh.close()
        PrintTimeMsg('CSFtpDownloadDel.__del__')

    def sftpListDir(self, sDir):
        dirlist = self.sftp.listdir(sDir)
        PrintTimeMsg("sftpListDir(%s): %s" % (sDir, dirlist))
        lsDir = self.sftp.listdir_attr(sDir)
        for oDir in lsDir:
            PrintTimeMsg("sftpListDir(%s): %s=%s=(%s,%s)" % (sDir, oDir, oDir.st_mode,
                                                             oDir.st_atime, oDir.st_mtime))

    def callbackStatus(self, iTransfer, iTotal):
        PrintTimeMsg("  %s=(%s/%s)" % (self.sHintFileName, iTransfer, iTotal))

    def sftpDownDeleteFile(self, sFileName, sDirRemote, sDirLocal):
        # 从主机上下载移除一个文件
        sFN = sFileName
        tmA, tmM = 0, 0
        if isinstance(sFN, paramiko.SFTPAttributes):
            sFN = sFileName.filename
            tmA, tmM = sFileName.st_atime, sFileName.st_mtime
        if self.sExtTail:
            if not sFN.endswith(self.sExtTail):
                PrintTimeMsg("sftpDownDeleteFile.IGNORE.sFN=%s=" % sFN)
                return
        self.sHintFileName = 'get(%s/%s)' % (sDirRemote, sFN)
        sR = sDirRemote + '/' + sFN
        sL = sDirLocal + os.path.sep + sFN
        sT = sL + '.filepart'  # 临时文件
        PrintTimeMsg("sftpDownDeleteFile.sftp.%s..." % self.sHintFileName)
        try:
            tmBegin = time.time()
            self.sftp.get(sR, sT, self.callbackStatus)
            if os.path.exists(sL):  # 若目标文件已存在，则删除
                os.remove(sL)
            os.rename(sT, sL)
            if tmA:
                os.utime(sL, (tmA, tmM))
            self.sftp.remove(sR)  # 删除主机端的文件
        except Exception as e:
            PrintTimeMsg('sftpDownDeleteFile.sftp.get(%s,%s,%s).Error=(%s)' % (
                sFN, sDirRemote, sDirLocal, str(e)))
            sys.exit(-102)
        else:
            tmConsume = time.time() - tmBegin
            PrintTimeMsg("sftpDownDeleteFile.sftpDownDelete(%s)=OK,tmConsume=%.1fs!" % (
                sFN, tmConsume))
        finally:
            try:
                # PrintTimeMsg("sftpDownDeleteFile.sftpDownDelete(%s)=remove!" % sFileName)
                if os.path.exists(sT):
                    os.remove(sT)
            except OSError as e:
                PrintTimeMsg('sftpDownDeleteFile.remove(%s).Error=(%s)' % (sT, str(e)))
                sys.exit(-103)

    def sftpDownDeleteDir(self, sDirRemote, sDirLocal):
        # 从服务端下载移除一个目录，遇到子目录则纳入队列
        try:
            if not os.path.exists(sDirLocal):
                os.mkdir(sDirLocal)
        except OSError as e:
            PrintTimeMsg('sftpDownDeleteDir.mkdir(%s).Error=(%s)' % (sDirLocal, str(e)))
            sys.exit(-105)
        lsDir = self.sftp.listdir_attr(sDirRemote)
        PrintTimeMsg("sftpDownDeleteDir.listdir_attr(%s).len=%s=" % (sDirRemote, len(lsDir)))
        for oDir in lsDir:
            if stat.S_ISREG(oDir.st_mode):  # 一般文件
                # PrintTimeMsg("sftpListDir(%s): %s=%s=FILE" % (sDirRemote, oDir, oDir.st_mode))
                self.sftpDownDeleteFile(oDir, sDirRemote, sDirLocal)  # .filename
            elif stat.S_ISDIR(oDir.st_mode):  # 目录
                # PrintTimeMsg("sftpListDir(%s): %s=%s=DIR" % (sDirRemote, oDir, oDir.st_mode))
                sDir = oDir.filename
                sR = sDirRemote + '/' + sDir
                self.listDirToMove.append((sR, sDirLocal + os.path.sep + sDir))
                PrintTimeMsg("sftpDownDeleteDir.listDirToMove.append(%s)!" % sR)
            else:  # 其它
                PrintTimeMsg("sftpListDir(%s): %s=%s=OTHER" % (sDirRemote, oDir, oDir.st_mode))

    def StartDownDeleteDir(self, sDirRemote, sDirLocal):
        # 开始从服务端下载一个目录，并其所有子目录纳入队列
        self.listDirToMove = [(sDirRemote, sDirLocal)]
        while len(self.listDirToMove) > 0:
            (sR, sL) = self.listDirToMove.pop(0)
            self.sftpDownDeleteDir(sR, sL)


def mainCSFtpDownloadDel():
    dictHPUP = {
        'host': '127.0.0.1',
        'port': 22,
        'user': 'root',
        'pass': 'pass',
    }
    o = CSFtpDownloadDel(dictHPUP)
    o.sftpListDir(r'C:\WeiYF\run\testdata\tsOut')  # ok
    # o.sftpListDir('C:/WeiYF/run/testdata/tsOut')  # ok

# --------------------------------------
if __name__ == '__main__':
    mainCSFtpDownloadDel()
