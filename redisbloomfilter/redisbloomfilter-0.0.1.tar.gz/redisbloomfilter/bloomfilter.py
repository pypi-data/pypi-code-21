# encoding=utf-8
# ---------------------------------------
# @Date    : 2017-10-24
# @Author  : zhangzehui
# @Version : python2/3
# ---------------------------------------

from __future__ import print_function
import sys
import redis
import hashlib

if sys.version_info < (3, 0):
    py_version = 2
elif sys.version_info >= (3, 0):
    py_version = 3
else:
    raise RuntimeError('At least Python 2.X or 3.X is required')


def str2md5(input_str):
    if input_str is None:
        raise ValueError('the filter str must be not none')
    if str(input_str).strip() == '':
        raise ValueError('thr filter str can not be empty')

    if py_version == 3:
        input_str = input_str.encode()

    m = hashlib.md5()
    m.update(input_str)
    return m.hexdigest()


class SimpleHash(object):
    def __init__(self, cap, seed):
        self.cap = cap
        self.seed = seed

    def hash(self, value):
        ret = 0
        for i in range(len(value)):
            ret += self.seed * ret + ord(value[i])
        return (self.cap - 1) & ret


class BloomFilter(object):
    def __init__(self, host='localhost', port=6379, db=1, block_num=1, key='bloomfilter'):
        """
        :param host: the host of Redis
        :param port: the port of Redis
        :param db: witch db in Redis
        :param block_num: one block_num for about 90,000,000; if you have more strings for filtering, increase it.
        :param key: the key's name in Redis
        """
        self.server = redis.Redis(host=host, port=port, db=db)
        self.bit_size = 1 << 31  # Redis的String类型最大容量为512M，现使用256M
        self.seeds = [5, 7, 11, 13, 31, 37, 61]
        self.key = key
        self.block_num = block_num
        self.hashfunc = []
        for seed in self.seeds:
            self.hashfunc.append(SimpleHash(self.bit_size, seed))

    def exists(self, input_str):
        if not input_str:
            return False
        input_str = str2md5(input_str)
        ret = True
        name = self.key + str(int(input_str[0:2], 16) % self.block_num)
        for f in self.hashfunc:
            loc = f.hash(input_str)
            ret = ret & self.server.getbit(name, loc)
        return ret

    def insert(self, input_str):
        input_str = str2md5(input_str)
        name = self.key + str(int(input_str[0:2], 16) % self.block_num)
        for f in self.hashfunc:
            loc = f.hash(input_str)
            self.server.setbit(name, loc, 1)


if __name__ == '__main__':
    urls = [
        'http://www.baidu.com',
        'http://www.qq.com',
        'http://www.163.com',
        'http://www.jd.com',
        'http://www.taobao.com',
        'http://www.sina.com.cn',
        'http://www.nba.com',
        'http://www.google.com'
    ]

    bf = BloomFilter(host='localhost', port=6379, db=1)

    for each in urls:
        exists = bf.exists(each)
        print('{} exists is {}'.format(each, exists))
        if not exists:
            bf.insert(each)
            print('{} insert success.'.format(each))
