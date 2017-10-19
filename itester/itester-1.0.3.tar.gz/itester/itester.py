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
#                        2017/10/19  上午10:05


import os
import time
import json
import click
import requests
from common.html_report import htmlreporter
from common.termlogcolor import log
from common.tools import (
    assertDictContains,
    prepareStrToDict,
    prepareRequestsParam,
    testLoader,
    fromExcelGetAllCase,
    sendmail
)

def findAllFile(path):
    all_case = []
    for casefile in testLoader(path):
        # 多个case文件进行case 合并
        all_case = all_case + fromExcelGetAllCase(casefile, 'GET') + fromExcelGetAllCase(casefile, 'POST')
    return all_case


def checkCase(*args):
    case_err = False
    if args[3] not in ("POST", 'GET'):
        case_err = True
        log.error("接口的Method 必须是POST、GET，请检查测试用例： %s" % args[0])

    if len(args[4]) <= 0:
        case_err = True
        log.error("确认URL正确，请检查测试用例： %s" % args[0])

    return case_err


def runTests(name, desc, use_yn, method, url, headers, cookies, params, expect_value, func, proxies_proxy):
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
        error_lists = assertDictContains(expect_value, response.content, u'节点：', err_list=[])
    elif func == 'assert_in':
        error_lists = assertDictContains(json.loads(expect_value), response.json(), u'节点：' , err_list=[])

    return error_lists

@click.command()
@click.option('-c', '--casepath', default='./', help=u'case路径，默认当前路径')
@click.option('-m', '--mailto', help=u'收件人列表，使用逗号分割')
@click.option('-o', '--outputpath', default='./', help=u'测试报告输出路径，默认当前路径')
@click.option('-p', '--prefix', help=u'邮件内容中的url的前缀, 如不输入发送附件')
def main(casepath, mailto, outputpath, prefix):
    '''Excel - driven interface automation framework'''
    time_start = time.time()
    pass_no = fail_no = err_no = 0
    case_error = False
    case_html_output = []

    all_case = findAllFile(casepath)

    if all_case:
        for case in all_case:
            case_error = checkCase(*case)
            try:
                res_lists = []
                res_lists = runTests(*case)
                if res_lists:
                    fail_no += 1
                    res_flag = 0
                    log.error(u"用例：%s - 实际结果与预期结果不一致，测试失败，结果如下：" % case[1])
                    log.error(",".join(res_lists))
                else:
                    pass_no += 1
                    res_flag = 1
                    log.info(u"用例：%s - 实际结果与预期结果一致，测试通过" % case[1])
            except Exception as e:
                err_no += 1
                res_flag = 2
                res_lists.append(u"用例：%s - 执行异常，异常信息:" % case[1])
                log.error("执行异常，信息：%s " % str(e))
            finally:
                for idx1, val1 in enumerate(res_lists):
                    res_lists[idx1] = val1.replace('<', '&lt;').replace('>', '&gt;')

                res_lists = '<br>'.join(res_lists) if len(res_lists) else '测试通过'
                case_html_output.append([case[0], case[1], res_flag, res_lists])

    else:
        log.error('测试用例集合为空！')

    if case_error:
        log.error('测试用合法性检查失败，请检查~')
    else:
        time_end = time.time()
        time_cost = time_end - time_start
        log.info("测试完成，通过测试用例数：%s, 失败用例数：%s, 异常用例数：%s, 执行测试用例耗时：%s 秒" % (pass_no, fail_no, err_no, time_cost)  )

    if fail_no > 0 or err_no > 0:
        html_name = 'report%s.html' % str(int(time.time()))
        html_full_name = os.path.join(outputpath, html_name)
        html_report = htmlreporter(html_full_name, case_html_output)
        html_report.make_report()
        if prefix:
            sendmail(mailto.split(','), prefix + html_name)
        else:
            sendmail(mailto.split(','), html_full_name)

if __name__ == '__main__':
    main()
