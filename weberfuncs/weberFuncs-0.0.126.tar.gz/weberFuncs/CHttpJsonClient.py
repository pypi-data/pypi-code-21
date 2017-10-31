#! /usr/local/bin/python
#-*- coding:utf-8 -*-

"""
@author: weber.juche@gmail.com
@time: 2016/12/6 9:54

HTTP+GET/POST+JSON 客户端调用封装

"""
import sys
import json
from .WyfPublicFuncs import PrintTimeMsg, printCmdString
from .WyfHttpFuncs import RequestsHttpPost #,RequestsHttpGet


class CHttpJsonClient:

    # URL_HTTPPOST = 'http://127.0.0.1:5000/App/cmd'
    URL_HTTPPOST = 'http://127.0.0.1:5000/MatchEngine/cmd'

    def __init__(self, sUrl=URL_HTTPPOST):
        self.sUrl = sUrl
        PrintTimeMsg("CHttpJsonClient.sUrl=(%s)" % (self.sUrl) )

    def CallCmd(self, CmdIStr):
        printCmdString('CallCmd.CmdIStr',CmdIStr)
        retCode, retText = RequestsHttpPost(self.sUrl, json.dumps(CmdIStr) )
        if retCode==200:
            CmdOStr = json.loads(retText)
            printCmdString('CallCmd.CmdOStr',CmdOStr)
            return CmdOStr
        PrintTimeMsg("CallCmd.retCode=(%s),retText=(%s)" % (retCode,retText) )
        return ['ES',str(retCode),str(retText),'']

def testCHttpJsonClient():
    o = CHttpJsonClient()
    o.CallCmd(["ME.GetMatchParam","BTCCNY"])


#-------------------------------
if __name__ == '__main__':
    testCHttpJsonClient()