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
from nose.tools import assert_equal
from common.parameterized import parameterized
from common.tools import assertDictContains, prepareStrToDict, prepareRequestsParam, testLoader, fromExcelGetAllCase

TEST_GET_CASE = TEST_POST_CASE = []

basepath = os.path.dirname(os.path.abspath(__file__))

for casefile in testLoader(os.path.join(basepath, 'testcase')):
    # 多个case文件进行case 合并
    TEST_GET_CASE = TEST_GET_CASE + fromExcelGetAllCase(casefile, 'GET')
    TEST_POST_CASE = TEST_POST_CASE + fromExcelGetAllCase(casefile, 'POST')


class test_iterster():
    '''
    测试的主入口类
    '''
    @parameterized.expand(TEST_GET_CASE)
    def test_get(self, name, desc, use_yn, method, url, headers, cookies, params, expect_value, func, proxies_proxy):
        '''
        GET 方法的接口的测试
        :param name: case 名称
        :param desc: case的详细描述
        :param method: GET/POST
        :param url: 调用的接口
        :param headers: h1: v1\n h2: v2
        :param cookies: c1: v1\n c2: v2
        :param params: key1=value1&key2=value2
        :param expect_value: 预计返回值
        :param func:assert_equal - 预计返回值和实际返回值相等/assert_in - 实际返回值包含预计返回值
        :param proxies_proxy - 代理设置
        '''
        headers_dict = prepareStrToDict(headers)
        cookies_dict = prepareStrToDict(cookies)
        if params:
            params_dict = prepareRequestsParam(params)
        else:
            params_dict = {}

        proxies = {
            "http": proxies_proxy,
            "https": proxies_proxy,
        }

        if proxies_proxy:
            response = requests.get(url, headers=headers_dict, cookies=cookies_dict, params=params_dict,
                                    proxies=proxies)
        else:
            response = requests.get(url, headers=headers_dict, cookies=cookies_dict, params=params_dict)

        if func == 'assert_equal':
            assert_equal(expect_value, response.content)
        elif func == 'assert_in':
            error_lists = assertDictContains(json.loads(expect_value), response.json(), err_list=[])
            if len(error_lists) > 0:
                raise AssertionError(",".join(error_lists))
            else:
                return

    @parameterized.expand(TEST_POST_CASE)
    def test_post(self, name, desc, use_yn, method, url, headers, cookies, params, expect_value, func, proxies_proxy):
        '''
        POST 方法的接口的测试
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

        proxies = {
            "http": proxies_proxy,
            "https": proxies_proxy,
        }

        try:
            params_dict = prepareRequestsParam(params)
        except:
            params_dict = json.dumps(json.loads(params))
            headers_dict['content-type'] = 'application/json'

        if proxies_proxy:
            response = requests.post(url, headers=headers_dict, cookies=cookies_dict, data=params_dict, proxies=proxies)
        else:
            response = requests.post(url, headers=headers_dict, cookies=cookies_dict, data=params_dict)

        if func == 'assert_equal':
            assert_equal(json.loads(expect_value), response.json())
        elif func == 'assert_in':
            error_lists = assertDictContains(json.loads(expect_value), response.json(), err_list=[])
            if len(error_lists) > 0:
                raise AssertionError(",".join(error_lists))
            else:
                return


if __name__ == '__main__':
    nose.run()
