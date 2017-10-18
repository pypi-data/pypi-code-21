# -*- coding: utf-8 -*-
#字符串相关函数
import random
def fill_id(id,length):
    '''自动填充id到指定的长度'''
    idLength = len(str(id))
    if idLength>length:
        return str(id)
    else:
        return '0'*(length-idLength) + str(id)

def create_nonce_str(length=32):
    """产生随机字符串，不长于32位"""
    chars = "abcdefghijklmnopqrstuvwxyz0123456789"
    strs = []
    for x in range(length):
        strs.append(chars[random.randrange(0, len(chars))])
    return "".join(strs)