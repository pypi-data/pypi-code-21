#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Time    : 2017/7/21 下午3:45
# @Author  : Hou Rong
# @Site    :
# @File    : MongoUtils.py
# @Software: PyCharm
each_line_num = 2000


def mongo_find_iter(collections):
    # 获取最小，最大 id 以便遍历全部
    min_id = list(collections.find().sort('_id', 1).limit(1))[0]['_id']
    max_id = list(collections.find().sort('_id', -1).limit(1))[0]['_id']

    now_id = min_id

    # 返回第一项
    __line = collections.find_one({'_id': {'$gte': now_id}})
    now_id = __line['_id']
    yield __line
    if now_id == max_id:
        raise StopIteration()

    # 返回剩余部分
    while True:
        for __line in collections.find({'_id': {'$gt': now_id}}).sort('_id').limit(each_line_num):
            now_id = __line['_id']
            yield __line
            if now_id == max_id:
                # 采用异常跳出两级循环
                raise StopIteration()


if __name__ == '__main__':
    import pymongo

    client = pymongo.MongoClient(host='10.10.231.105')

    src_collections = client['FullSiteSpider']['HotelFullSite']

    count = 0
    for line in mongo_find_iter(src_collections):
        count += 1
        if count % 1000 == 0:
            print(count)
    print(count)
