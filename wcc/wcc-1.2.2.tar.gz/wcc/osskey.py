# -*- coding: utf-8 -*-

"""
wcc.utils
----------

工具函数模块。
"""
import os.path
import base64
import time

class Osskey():
    @staticmethod
    def getKey():
        access_key_id = "TFRBSXUyN3FSQk1xRk41TkA="
        #access_key_id = os.getenv('OSS_WCC_ACCESS_KEY_ID','null')
        if access_key_id == "null":
            return None
        return Osskey.decode(access_key_id)
    @staticmethod
    def getSecret():
        access_key_secret = "Mk95b205R2x4ZkRGNXZnM0JVWXlWRzQ1bFpMaUVyQA=="
        #access_key_secret = os.getenv('OSS_WCC_ACCESS_KEY_SECRET','null')
        if access_key_secret == "null":
            return None
        return Osskey.decode(access_key_secret)

    @staticmethod
    def encode(strval):
        """对一个str变量进行简单变换后,经过base64编码返回str类型
            Base64编码，64指A-Z、a-z、0-9、+和/这64个字符，还有“=”号不属于编码字符，而是填充字符。
        返回值是base64格式
        """
        try:
            strval = strval + "@"
            bytval = strval.encode(encoding="utf-8")
            bytval = base64.b64encode(bytval)
        except Exception as err:
            return None
        return bytval.decode()
    @staticmethod
    def decode(strval):
        """把一个字符串解码
        返回值是str类型/None
        """
        try:
            bytval = strval.encode(encoding="utf-8")
            bytval = base64.b64decode(bytval)
            strval = bytval.decode()
            strval = strval[:-1]
        except Exception as err:
            return None
        return strval
