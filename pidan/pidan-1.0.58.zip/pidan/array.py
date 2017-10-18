# -*- coding: utf-8 -*-
#列表数组相关的函数


def strip_duplicate_from_list(ls):
    '''从列表中去除重复数据'''
    return sorted(set(ls),key=ls.index)

def get_intersection(a,b):
    """
    获取两个数组的交集
    :param a: 数组a
    :param b: 数组b
    :return: 返回交集
    """
    return list(set(a).intersection(set(b)))

def get_difference(a,b):
    """
    获取两个数组的差集，不区分数组a和b的长度
    :param a: 数组a
    :param b: 数组b
    :return: 返回差集
    """
    if len(a) > len(b):
        a,b=b,a
    return list(set(b).difference(set(a)))

def get_union(a,b):
    """
    获取两个数组的并集
    :param a: 数组a
    :param b: 数组b
    :return: 返回并集
    """
    return  list(set(a).union(set(b)))


if __name__ == '__main__':
    print(get_intersection([1,2,3,5],[5,6,7,8,9]))
    print(get_difference([1,2,3,4,5],[1,2,3]))
    print(get_union([1,2,3],[4,5,6]))
