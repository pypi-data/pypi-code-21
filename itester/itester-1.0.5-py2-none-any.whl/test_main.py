#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
#    Meng xiangguo <mxgnene01@gmail.com>
#
#              _____               ______
#     ____====  ]OO|_n_n__][.      |    |]
#    [________]_|__|________)<     |MENG|
#     oo    oo  'oo OOOO-| oo\_   ~o~~~o~'
# +--+--+--+--+--+--+--+--+--+--+--+--+--+
#                        2017/10/16  下午5:47

import os
import nose
import json
import requests
from common.parameterized import parameterized
from common.tools import assertDictContains, prepareStrToDict, prepareRequestsParam, findAllFile, encodeutf8

path = os.getenv('ITESTER_CASE_PATH', os.path.join(os.path.dirname(os.path.abspath(__file__)), '../testcase'))
TEST_CASES = findAllFile(path)

class test_iterster():
    '''
    测试的主入口类
    '''
    @parameterized.expand(TEST_CASES)
    def test_runcase(self, name, desc, use_yn, method, url, headers, cookies, params, expect_value, func, proxies_proxy):
        '''
        接口的测试 - 主方法
        :param name: case 名称
        :param desc: case的详细描述
        :param method: GET/POST
        :param url: 调用的接口
        :param headers: h1: v1\n h2: v2
        :param cookies: c1: v1\n c2: v2
        :param param: key1=value1&key2=value2
        :param expect_value: 预计返回值
        :param func:assert_equal - 预计返回值和实际返回值相等/assert_in - 实际返回值包含预计返回值
        :param proxies_proxy - 代理设置
        '''
        headers_dict = prepareStrToDict(headers)
        cookies_dict = prepareStrToDict(cookies)
        if params:
            try:
                params_dict = prepareRequestsParam(params)
            except:
                # params 为json格式
                params_dict = json.dumps(json.loads(params))
                headers_dict['content-type'] = 'application/json'
        else:
            params_dict = {}

        proxies = {
            "http": proxies_proxy,
            "https": proxies_proxy,
        }

        if method == "GET":
            if proxies_proxy:
                response = requests.get(url, headers=headers_dict, cookies=cookies_dict, params=params_dict, proxies=proxies)
            else:
                response = requests.get(url, headers=headers_dict, cookies=cookies_dict, params=params_dict)
        elif method == "POST":
            if proxies_proxy:
                response = requests.post(url, headers=headers_dict, cookies=cookies_dict, data=params_dict, proxies=proxies)
            else:
                response = requests.post(url, headers=headers_dict, cookies=cookies_dict, data=params_dict)

        if func == 'assert_equal':
            error_lists = assertDictContains(expect_value, response.content, u'node：', err_list=[])
        elif func == 'assert_in':
            error_lists = assertDictContains(json.loads(expect_value), response.json(), u'node：', err_list=[])

        if len(error_lists) > 0:
            raise AssertionError("%s error" % name)
        else:
            return


if __name__ == '__main__':
    nose.run()
