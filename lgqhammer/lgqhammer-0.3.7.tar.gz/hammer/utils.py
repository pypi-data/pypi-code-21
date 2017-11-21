# -*- coding=utf-8 -*-

from configparser import ConfigParser


def get_full_url(url, param):
    p = ''
    for k, v in param.items():
        p = '%s&%s=%s' % (p, k, v)
    full = '%s?%s' % (url, p)
    return full


def full_url(url, param):
    return get_full_url(url, param)


def ini2json(file):
    cf = ConfigParser()
    cf.read(file)
    conf = {}
    for section in cf.sections():
        conf[section] = {}
        for name, value in cf.items(section):
            conf[section][name] = value

    return conf

#
# if __name__ == '__main__':
#     url = 'https://apphouse.58.com/api/list/hezu?&localname=bj&os=android&format=json&v=1&geotype=baidu&page=2'
#
#     param = {
#         'action':'getListInfo',
#         'curVer': '7.13.1',
#         'appId':'1'
#     }
#
#     print(full_url(url, param))
