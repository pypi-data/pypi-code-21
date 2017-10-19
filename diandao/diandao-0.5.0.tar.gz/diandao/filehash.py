# -*- coding: utf-8 -*-
#
# 读取文件的hash值
# from diandao import filehash
# fmd5 = filehash.md5(myfile_path)
#

import hashlib

__buffsize = 64 * 1024


def __hash(method, *args):
    calc = getattr(hashlib, method.func_name)

    def _c(file):
        with open(file, 'rb') as f:
            sha1obj = calc()
            while True:
                data = f.read(__buffsize)
                if not data:
                    break
                sha1obj.update(data)
            hashstr = sha1obj.hexdigest()
            return hashstr
    return _c


@__hash
def sha1(file):
    pass


@__hash
def sha224(file):
    pass

@__hash
def sha256(file):
    pass

@__hash
def sha384(file):
    pass


@__hash
def sha512(file):
    pass


@__hash
def md5(file):
    pass