#-*- coding:utf-8 -*-

"""
@author: weber.juche@gmail.com
@time: 2017/1/10 10:31

    标签日志功能封装
    ~~~~~~~~~~~~~~~

"""
from .WyfPublicFuncs import PrintTimeMsg,GetSrcParentPath,GetCurrentTimeMSs

def GetSrcCurrentPath(srcfile):
    """
        取指定代码文件本级目录的绝对路径
    """
    import os
    import os.path
    if srcfile:
        sDir = os.path.dirname(os.path.realpath(srcfile))
        lsDir = sDir.split(os.sep)
        sDir = os.sep.join(lsDir)
        return sDir+os.sep
    else:
        PrintTimeMsg("Please use GetSrcParentPath(__file__)! Exit!")
        sys.exit(-1)

class CLogTagMsg():
    """
        标签日志，是指在普通日志之外，将某一类特殊日志通过标签汇集在一起。
    """

    def __init__(self, sReferFullPathFileName, sPrefixFN, sSuffixFN, bParentPath=False, sLogSubDir = 'log'):
        """
            :param sReferFullPathFileName: 所参考全路径文件名，一般给 __file__ 取当前源码路径
            :param sPrefixFN: 标签日志文件名的前缀
            :param bParentPath: 是否是参考路径的上一级路径，默认为 False
            :param sLogSubDir: 相对参考路径下的日志子路径，默认为 log
        """
        import os
        self.cPathSep = os.sep
        self.sReferFullPathFileName = sReferFullPathFileName
        self.sPrefixFN = sPrefixFN
        self.sSuffixFN = sSuffixFN
        self.bParentPath = bParentPath
        self.sLogSubDir = sLogSubDir
        if bParentPath:
            self.sLogPath = GetSrcParentPath(self.sReferFullPathFileName)
        else:
            self.sLogPath = GetSrcCurrentPath(self.sReferFullPathFileName)
        if self.sLogSubDir:
            self.sLogPath += self.sLogSubDir+self.cPathSep
        PrintTimeMsg('CLogTagMsg.sLogPath=%s=' % self.sLogPath) # 该路径带结尾分隔符
        PrintTimeMsg('CLogTagMsg.sFNameOut=%s=' % self.__getTagLogFName('TAG'))

    def __getTagLogFName(self,sTagFN):
        return "%s%s%s.%s" % (self.sLogPath, self.sPrefixFN, sTagFN, self.sSuffixFN)

    def log(self, sTagFN, sMsg, bPrintStdout=True):
        if bPrintStdout: PrintTimeMsg('[%s]%s!' % (sTagFN,sMsg))
        sFNameOut = self.__getTagLogFName(sTagFN)
        with open(sFNameOut,"a") as f: #追加模式输出
            sS = "[%s]%s\n" % (GetCurrentTimeMSs(),sMsg)
            f.write(sS)


def testCLogTagMsg():
    o = CLogTagMsg(__file__, 'wyf', 'log', False, '')
    o.log('test','InfoMsg')
    PrintTimeMsg('GetSrcCurrentPath='+GetSrcCurrentPath(__file__)) # 返回当前目录
    PrintTimeMsg('GetSrcCurrentPath='+GetSrcCurrentPath('.'))  # 返回上级目录
    PrintTimeMsg('GetSrcCurrentPath='+GetSrcCurrentPath('..')) # 返回上上级目录


#-------------------------------
if __name__ == '__main__':
    testCLogTagMsg()