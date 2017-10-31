#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
__createTime__ = "2017/7/12 14:53"
__author__ = "WeiYanfeng"
__email__ = "weber.juche@gmail.com"
__version__ = "0.0.1"
        
~~~~~~~~~~~~~~~~~~~~~~~~
程序单元功能描述
封装算法相关函数
~~~~~~~~~~~~~~~~~~~~~~~~
# 依赖包 Package required
# pip install PyCrypto   # 该库安装需要 VCForPython27.msi

"""
from .WyfPublicFuncs import IsPython3, PrintTimeMsg, printHexString


def ToHexString(bytesArray, bSpace=False):
    """
    Convert a byte string to it's hex string representation e.g. for output.
    将字节数组转为十六进制串
    """
    sSep = ' ' if bSpace else ''
    if IsPython3():
        lsBytes = ["%.2X" % x for x in bytesArray.encode('utf-8')]
    else:
        lsBytes = ["%.2X" % ord(x) for x in bytesArray]
    return sSep.join(lsBytes).strip()


def FmHexString(hsString, bSpace=False):
    """
    Convert a string hex byte values into a byte string. The Hex Byte values may
    or may not be space separated.
    将十六进制串转为字节数组
    """
    if IsPython3():
        return bytes.fromhex(hsString).decode('utf-8')
    else:
        s = hsString.replace(" ", "") if bSpace else hsString
        return s.decode("hex")


def testHexString():
    # hsV1 = ToHexString(bytes('Hello世界ABCD!'))
    hsV1 = ToHexString('Hello世界ABCD!')
    PrintTimeMsg('hsV1=%s=' % hsV1)
    sV1 = FmHexString(hsV1)
    PrintTimeMsg('sV1=%s=' % sV1)

# ----------------------------
gsAesIV = b'0000000000000000'  # AES CBC 算法IV默认值


def AesCbcHexEncryt(sKey16, hsText):
    """
    采集AES算法的CBC模式的16字节秘钥加密十六进制串
    :param sKey16: 16字节秘钥
    :param hsText: 要加密的数据（十六进制格式）
    :return: 加密结果（十六进制格式）
    """
    global gsAesIV
    from Crypto.Cipher import AES
    iKeyLen = len(sKey16)  # 16
    if iKeyLen != 16:
        PrintTimeMsg('AesCbcHexEncryt.sKey16=%s,iKeyLen=%s=Error' % (sKey16, iKeyLen))
        return ''
    sText = FmHexString(hsText, True)
    # PrintTimeMsg('AesCbcHexEncryt.sKey=%s,sText=%s=' % (sKey, sText))
    printHexString('AesCbcHexDecryt.sText=', sText)
    cryptor = AES.new(sKey16, AES.MODE_CBC, gsAesIV)  # , sKey16)

    def pad(s):
        BS = AES.block_size
        return s + (BS - len(s) % BS) * chr(BS - len(s) % BS)
    sCipherOut = cryptor.encrypt(pad(sText))
    return ToHexString(sCipherOut, True)


def AesCbcHexDecryt(sKey16, hsText):
    """
    采集AES算法的CBC模式的16字节秘钥解密十六进制串
    :param sKey16: 16字节秘钥
    :param hsText: 要解密的数据（十六进制格式）
    :return: 解密结果（十六进制格式）
    """
    global gsAesIV
    from Crypto.Cipher import AES
    iKeyLen = len(sKey16)  # 16
    if iKeyLen != 16:
        PrintTimeMsg('AesCbcHexDecryt.sKey16=%s,iKeyLen=%s=Error' % (sKey16, iKeyLen))
        return ''
    sText = FmHexString(hsText, True)
    # PrintTimeMsg('AesCbcHexEncryt.sKey=%s,sText=%s=' % (sKey, sText))
    printHexString('AesCbcHexDecryt.sText=', sText)
    cryptor = AES.new(sKey16, AES.MODE_CBC, gsAesIV)  #, sKey16)
    sCipherOut = cryptor.decrypt(sText)
    # printHexString('AesCbcHexEncryt.sCipherOut', sCipherOut)

    def unpad(s): return s[0:-ord(s[-1])]  # PEP8不建议 unpad = lambda s: s[0:-ord(s[-1])]
    return ToHexString(unpad(sCipherOut))


def mainCryptoFuncs():
    import base64
    # testHexString()
    sOut = AesCbcHexDecryt('1234567890ABCDEF', 'B1 FA 16 AD 2E 79 B4 4D 81 24 81 76 3D FA 2C 9A 63 D9 31 7D DF 5C 9D D6 58 96 CD 84 1D 31 62 54 ')
    PrintTimeMsg('AesCbcHexDecryt.sOut=%s=' % sOut)
    PrintTimeMsg('AesCbcHexDecryt.sOut=%s=' % FmHexString(sOut))
    sOut = FmHexString(AesCbcHexDecryt('Sr8!8MI!N!2G5MVo', ToHexString(base64.b64decode('6ujvAe4Tfa6bXQrkZ7/XOQ=='))))
    PrintTimeMsg('AesCbcHexDecryt.sOut=%s=' % sOut)

    sOut = AesCbcHexEncryt('1234567890ABCDEF', ToHexString('ABCDEFsix@abcd.com'))
    PrintTimeMsg('AesCbcHexEncryt.sOut=%s=' % sOut)
    sOut = AesCbcHexEncryt('Sr8!8MI!N!2G5MVo', ToHexString('pVW4U*FlS'))
    PrintTimeMsg('AesCbcHexEncryt.sOut=%s=' % sOut)


# --------------------------------------
if __name__ == '__main__':
    mainCryptoFuncs()
