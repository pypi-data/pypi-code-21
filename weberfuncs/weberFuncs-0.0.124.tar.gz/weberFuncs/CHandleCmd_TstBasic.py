#! /usr/local/bin/python
#-*- coding:utf-8 -*-

"""
@author: weber.juche@gmail.com
@time: 2016/11/9 16:55

测试 CHandleCmd_BaseService

"""

from .CHandleCmd_BaseService import RegisterForHandleCmdService, CHandleCmd_BaseService

@RegisterForHandleCmdService()
class CHandleCmd_TstBasic(CHandleCmd_BaseService):

    # def cmd_ListCmd(self, CmdIStr):
    #     return CHandleCmd_BaseService.cmd_ListCmd(self,CmdIStr)

    def cmd_JustForTest3(self,p):
        # do some stuff
        print("cmd_JustForTest3",p)
        return "---------"+str(p)

    def cmd_JustForTest(self,p):
        # do some stuff
        print("cmd_JustForTest",p)
        return "---------"+str(p)

    def cmd_JustForTest2(self,p):
        # do some stuff
        print("cmd_JustForTest2",p)
        return "---------"+str(p)

    def cmd_Echo(self, lsParam):
        lsRet = lsParam
        lsRet.append(str(self.args))
        return lsRet

    def cmd_EchoDict(self, dictParam):
        dictKV = dictParam
        dictKV['@Status'] = "000"
        # CmdOStr = ["000"]
        # for k,v in dictKV.items():
        #     CmdOStr.append('%s %s' % (k,v))
        return dictKV#CmdOStr

def TestCmdHandleBase():
    m = CHandleCmd_TstBasic()
    m.DebugCallByName('BaseService.JustForTest', ('@','******'))
    m.DebugCallByName('TstBasic.JustForTest2', ('@','******'))
    m.DebugCallByName('BaseService.JustForTest3', ('@','******'))
    m.DebugCallByName('TstBasic.JustForTest3', ('@','******'))
    m.DebugCallByName('BaseService.ListCmd',['@',])
    m.DebugCallByName('BaseService.EchoCmd',('@',1,2,3,4))
    m.DebugCallByName('TstBasic.ListCmd', ['@',])

#-------------------------------
if __name__ == '__main__':
    TestCmdHandleBase()