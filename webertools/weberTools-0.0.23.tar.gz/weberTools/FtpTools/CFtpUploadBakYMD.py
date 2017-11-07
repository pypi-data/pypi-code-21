#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
__createTime__ = "2017/10/20 15:57"
__author__ = "WeiYanfeng"
__email__ = "weber.juche@gmail.com"
__version__ = "0.0.1"
        
~~~~~~~~~~~~~~~~~~~~~~~~
程序单元功能描述
将本地文件推送到远程主机，并移到本地另外一目录下备份。
参考 [20.8. ftplib — FTP protocol client — Python 2.7.14 documentation](https://docs.python.org/2/library/ftplib.html)
主机数据目录增加 YYYY/MM/DD 格式。
~~~~~~~~~~~~~~~~~~~~~~~~
# 依赖包 Package required
# pip install weberFuncs
"""
import sys
from weberFuncs import PrintTimeMsg, PrintInline, GetTimeInteger, GetCurrentTime
# , GetFileSizeModTime
import os
import time
import stat
from ftplib import FTP


class CFtpUploadBakYMD:
    """
    上传本地文件到FTP主机，上传成功后，将本地文件移到另外一个目录备份。
    即“上传备份”，达到将文件上传到FTP主机的目的。
    """
    def __init__(self, dictHPUP, tupleYmdIndex=None, sExtTail=''):
        sHostPort = '%s:%s' % (dictHPUP.get('host', ''), dictHPUP.get('port', '0'))
        PrintTimeMsg('CFtpUploadBakYMD.connect(%s)...' % sHostPort)
        try:
            self.ftp = FTP()
            self.ftp.set_debuglevel(0)  # 2=显示详细信息;  0=关闭调试信息
            self.ftp.connect(dictHPUP.get('host', ''), int(dictHPUP.get('port', '0')))  # 连接
            self.ftp.login(dictHPUP.get('user', ''), dictHPUP.get('pass', ''))  # 登录，如果匿名登录则用空串代替即可
            PrintTimeMsg('CFtpUploadBakYMD(%s)WelcomeMsg=%s=' % (sHostPort, self.ftp.getwelcome()))
        except Exception as e:
            PrintTimeMsg('CFtpUploadBakYMD.connect.Error=(%s)' % str(e))
            sys.exit(-101)

        self.sExtTail = sExtTail
        PrintTimeMsg('CFtpUploadBakYMD.sExtTail=%s=' % self.sExtTail)
        self.tupleYmdIndex = tupleYmdIndex
        PrintTimeMsg('CFtpUploadBakYMD.tupleYmdIndex=(%s)' % self.tupleYmdIndex)
        self.iBlockSize = 1024
        self.sHintFileName = ''
        self.listDirToMove = []  # 要上传备份的目录列表，内容是 (sRemoteDir, sLocalDir)

    def __del__(self):
        if hasattr(self, 'ftp'):
            self.ftp.close()
        PrintTimeMsg('CFtpUploadBakYMD.__del__')

    def callbackStatus(self, block):
        # PrintTimeMsg("  %s=(%s)" % (self.sHintFileName, len(block)))
        if len(block) == self.iBlockSize:
            PrintInline('.')
        else:
            PrintInline('\n')

    def ftpUploadBakupFile(self, sFileName, sDirRemote, sDirLocal, sDirBakup, sYmd):
        # 从上传一个文件到主机，并移到本地备份目录下。目录结尾没有分隔符
        sFN = sFileName
        sSubR = ''
        sSubB = ''
        if sYmd:
            lsYMD = ['', sYmd[0:4], sYmd[4:6], sYmd[6:8]]
            sSubR = '/'.join(lsYMD)
            sSubB = os.path.sep.join(lsYMD)
        sR = sDirRemote + sSubR + '/' + sFN
        sT = sR + '.filepart'  # 临时文件
        sL = sDirLocal + os.path.sep + sFN
        sB = sDirBakup + sSubB + os.path.sep + sFN
        self.sHintFileName = 'put(%s)' % sR
        PrintTimeMsg("ftpUploadBakupFile(%s)..." % self.sHintFileName)
        try:
            tmBegin = time.time()
            file_handler = open(sL, 'rb')
            self.ftp.cwd(sDirRemote)
            self.ftp.storbinary('STOR %s' % sT, file_handler,
                                self.iBlockSize, self.callbackStatus)
            # self.ftp.put(sL, sT, self.callbackStatus)
            PrintTimeMsg('storbinary(%s)=OK!' % sFN)
            file_handler.close()

            self.ftp.rename(sT, sR)  # 主机文件更名
            PrintTimeMsg('ftp.rename(%s,%s)=OK!' % (sT, sR))
            # PrintTimeMsg('local.rename(%s,%s)...' % (sL, sB))
            try:
                os.rename(sL, sB)  # 本地文件更名
                PrintTimeMsg('local.rename(%s,%s)=OK!' % (sL, sB))
            except WindowsError as e: # 若打开文件未关闭，会出 WindowsError: [Error 32]
                PrintTimeMsg('local.rename(%s,%s)=%s!' % (sL, sB, str(e)))
                os.rename(sL, sB+'_'+GetCurrentTime())  # WeiYF.20171107 本地强制更名

        except Exception as e:
            PrintTimeMsg('ftpUploadBakupFile.put(%s,%s,%s).Error=(%s)' % (
                sFN, sDirRemote, sDirLocal, str(e)))
            sys.exit(-102)
        else:
            tmConsume = time.time() - tmBegin
            PrintTimeMsg("ftpUploadBakupFile(%s)=OK,tmConsume=%.1fs!" % (
                sFN, tmConsume))

    def ftpUploadBakupDir(self, sDirRemote, sDirLocal, sDirBakup):
        # 从本地上传到服务端并备份，遇到子目录则纳入队列
        def tryMkDirBoth(lsSub):
            if lsSub:
                lsSub.insert(0, '')
            sR = sDirRemote + '/'.join(lsSub)
            try:
                # self.sftp.stat(sR)
                self.ftp.mkd(sR)
            except Exception as e:
                # self.sftp.mkdir(sR)
                # PrintTimeMsg('ftp.mkdir(%s)=Error!Warning!' % (sR))
                pass
            sL = sDirBakup + os.path.sep.join(lsSub)
            if not os.path.exists(sL):
                os.mkdir(sL)
        tryMkDirBoth([])
        lsDir = os.listdir(sDirLocal)
        PrintTimeMsg("ftpUploadBakupDir.listdir(%s).len=%s=" % (sDirLocal, len(lsDir)))
        for sDir in lsDir:
            sL = sDirLocal + os.path.sep + sDir
            if os.path.isfile(sL):  # 一般文件
                if self.sExtTail:
                    if not sDir.endswith(self.sExtTail):
                        PrintTimeMsg("ftpUploadBakupDir.IGNORE.sFN=%s=" % sDir)
                        continue
                s = os.stat(sL)
                if GetTimeInteger() - int(s.st_mtime) >= 60*1:  # 仅上传1分钟前的
                    sFN = sDir
                    sYmd = ''
                    if self.tupleYmdIndex:
                        if len(self.tupleYmdIndex) == 1:
                            iIdx = self.tupleYmdIndex[0]
                            sYmd = sFN[iIdx:iIdx+8]
                        elif len(self.tupleYmdIndex) == 2:
                            lsV = sFN.split(self.tupleYmdIndex[0])
                            sYmd = lsV[int(self.tupleYmdIndex[1])][:8]
                        if len(sYmd) == 8:
                            sY = sYmd[0:4]
                            sM = sYmd[4:6]
                            sD = sYmd[6:8]
                            tryMkDirBoth([sY])
                            tryMkDirBoth([sY, sM])
                            tryMkDirBoth([sY, sM, sD])
                    self.ftpUploadBakupFile(sDir, sDirRemote, sDirLocal, sDirBakup, sYmd)
            elif os.path.isdir(sL):  # 目录
                self.listDirToMove.append((sDirRemote + '/' + sDir,
                                           sL, sDirBakup + os.path.sep + sDir))
                PrintTimeMsg("ftpUploadBakupDir.listDirToMove.append(%s)!" % sL)
            else:  # 其它
                PrintTimeMsg("ftpUploadBakupDir(%s): %s=OTHER" % (sDirLocal, sDir))

    def StartUploadBakupDir(self, sDirRemote, sDirLocal, sDirBakup):
        # 开始上传本地文件到服务端，并其所有子目录纳入队列
        self.listDirToMove = [(sDirRemote, sDirLocal, sDirBakup)]
        while len(self.listDirToMove) > 0:
            (sR, sL, sB) = self.listDirToMove.pop(0)
            self.ftpUploadBakupDir(sR, sL, sB)


def mainSFtpUploadBakYMD():
    dictHPUP = {
        'host': '10.205.17.140',
        'port': 21,
        'user': 'root',
        'pass': 'root',
    }
    o = CFtpUploadBakYMD(dictHPUP)
    sFileName = '1.ts'
    sDirRemote = '/tmp/123'
    sDirLocal = r'D:\WeberWork\ArchitectRoot\WeiYF\GitRoot\BitBucket\WeberSrcRootPrj\Python\Maywide\ImageRecognition\testdata\tmp'
    sDirBakup = r'D:\WeberWork\ArchitectRoot\WeiYF\GitRoot\BitBucket\WeberSrcRootPrj\Python\Maywide\ImageRecognition\testdata\bak'
    o.ftpUploadBakupFile(sFileName, sDirRemote, sDirLocal, sDirBakup, '20171020')
    # o.StartUploadBakupDir(sDirRemote, sDirLocal, sDirBakup)

# --------------------------------------
if __name__ == '__main__':
    mainSFtpUploadBakYMD()
