#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Date    : 2017-07-21 14:23:17
# @Author  : xuhaomin
# @Version : python3.6

import threading
import queue
import requests
import random
import json


def make_a_headers():
    headers = {
        'User-Agent': random.choice([
            "Mozilla/4.0 (compatible; MSIE 6.0; Windows NT 5.1; SV1; AcooBrowser; .NET CLR 1.1.4322; .NET CLR 2.0.50727)",
            "Mozilla/4.0 (compatible; MSIE 7.0; Windows NT 6.0; Acoo Browser; SLCC1; .NET CLR 2.0.50727; Media Center PC 5.0; .NET CLR 3.0.04506)",
            "Mozilla/4.0 (compatible; MSIE 7.0; AOL 9.5; AOLBuild 4337.35; Windows NT 5.1; .NET CLR 1.1.4322; .NET CLR 2.0.50727)",
            "Mozilla/5.0 (Windows; U; MSIE 9.0; Windows NT 9.0; en-US)",
            "Mozilla/5.0 (compatible; MSIE 9.0; Windows NT 6.1; Win64; x64; Trident/5.0; .NET CLR 3.5.30729; .NET CLR 3.0.30729; .NET CLR 2.0.50727; Media Center PC 6.0)",
            "Mozilla/5.0 (compatible; MSIE 8.0; Windows NT 6.0; Trident/4.0; WOW64; Trident/4.0; SLCC2; .NET CLR 2.0.50727; .NET CLR 3.5.30729; .NET CLR 3.0.30729; .NET CLR 1.0.3705; .NET CLR 1.1.4322)",
            "Mozilla/4.0 (compatible; MSIE 7.0b; Windows NT 5.2; .NET CLR 1.1.4322; .NET CLR 2.0.50727; InfoPath.2; .NET CLR 3.0.04506.30)",
            "Mozilla/5.0 (Windows; U; Windows NT 5.1; zh-CN) AppleWebKit/523.15 (KHTML, like Gecko, Safari/419.3) Arora/0.3 (Change: 287 c9dfb30)",
            "Mozilla/5.0 (X11; U; Linux; en-US) AppleWebKit/527+ (KHTML, like Gecko, Safari/419.3) Arora/0.6",
            "Mozilla/5.0 (Windows; U; Windows NT 5.1; en-US; rv:1.8.1.2pre) Gecko/20070215 K-Ninja/2.1.1",
            "Mozilla/5.0 (Windows; U; Windows NT 5.1; zh-CN; rv:1.9) Gecko/20080705 Firefox/3.0 Kapiko/3.0",
            "Mozilla/5.0 (X11; Linux i686; U;) Gecko/20070322 Kazehakase/0.4.5",
            "Mozilla/5.0 (X11; U; Linux i686; en-US; rv:1.9.0.8) Gecko Fedora/1.9.0.8-1.fc10 Kazehakase/0.5.6",
            "Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/535.11 (KHTML, like Gecko) Chrome/17.0.963.56 Safari/535.11",
            "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_7_3) AppleWebKit/535.20 (KHTML, like Gecko) Chrome/19.0.1036.7 Safari/535.20",
            "Opera/9.80 (Macintosh; Intel Mac OS X 10.6.8; U; fr) Presto/2.9.168 Version/11.52",
            "Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/536.11 (KHTML, like Gecko) Chrome/20.0.1132.11 TaoBrowser/2.0 Safari/536.11",
            "Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.1 (KHTML, like Gecko) Chrome/21.0.1180.71 Safari/537.1 LBBROWSER",
            "Mozilla/5.0 (compatible; MSIE 9.0; Windows NT 6.1; WOW64; Trident/5.0; SLCC2; .NET CLR 2.0.50727; .NET CLR 3.5.30729; .NET CLR 3.0.30729; Media Center PC 6.0; .NET4.0C; .NET4.0E; LBBROWSER)",
            "Mozilla/4.0 (compatible; MSIE 6.0; Windows NT 5.1; SV1; QQDownload 732; .NET4.0C; .NET4.0E; LBBROWSER)",
            "Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/535.11 (KHTML, like Gecko) Chrome/17.0.963.84 Safari/535.11 LBBROWSER",
            "Mozilla/4.0 (compatible; MSIE 7.0; Windows NT 6.1; WOW64; Trident/5.0; SLCC2; .NET CLR 2.0.50727; .NET CLR 3.5.30729; .NET CLR 3.0.30729; Media Center PC 6.0; .NET4.0C; .NET4.0E)",
            "Mozilla/5.0 (compatible; MSIE 9.0; Windows NT 6.1; WOW64; Trident/5.0; SLCC2; .NET CLR 2.0.50727; .NET CLR 3.5.30729; .NET CLR 3.0.30729; Media Center PC 6.0; .NET4.0C; .NET4.0E; QQBrowser/7.0.3698.400)",
            "Mozilla/4.0 (compatible; MSIE 6.0; Windows NT 5.1; SV1; QQDownload 732; .NET4.0C; .NET4.0E)",
            "Mozilla/4.0 (compatible; MSIE 7.0; Windows NT 5.1; Trident/4.0; SV1; QQDownload 732; .NET4.0C; .NET4.0E; 360SE)",
            "Mozilla/4.0 (compatible; MSIE 6.0; Windows NT 5.1; SV1; QQDownload 732; .NET4.0C; .NET4.0E)",
            "Mozilla/4.0 (compatible; MSIE 7.0; Windows NT 6.1; WOW64; Trident/5.0; SLCC2; .NET CLR 2.0.50727; .NET CLR 3.5.30729; .NET CLR 3.0.30729; Media Center PC 6.0; .NET4.0C; .NET4.0E)",
            "Mozilla/5.0 (Windows NT 5.1) AppleWebKit/537.1 (KHTML, like Gecko) Chrome/21.0.1180.89 Safari/537.1",
            "Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.1 (KHTML, like Gecko) Chrome/21.0.1180.89 Safari/537.1",
            "Mozilla/5.0 (iPad; U; CPU OS 4_2_1 like Mac OS X; zh-cn) AppleWebKit/533.17.9 (KHTML, like Gecko) Version/5.0.2 Mobile/8C148 Safari/6533.18.5",
            "Mozilla/5.0 (Windows NT 6.1; Win64; x64; rv:2.0b13pre) Gecko/20110307 Firefox/4.0b13pre",
            "Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:16.0) Gecko/20100101 Firefox/16.0",
            "Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.11 (KHTML, like Gecko) Chrome/23.0.1271.64 Safari/537.11",
            "Mozilla/5.0 (X11; U; Linux x86_64; zh-CN; rv:1.9.2.10) Gecko/20100922 Ubuntu/10.10 (maverick) Firefox/3.6.10"
        ]),
        'Referer': 'https://s.1688.com/selloffer/-B1A1BFEECDE2CCD720C5AE.html',
        "Host": 's.1688.com',
        "Accept-Language": "zh-CN,zh;q=0.8,en-US;q=0.5,en;q=0.3",
        "Accept-Encoding": "gzip, deflate, br",
        "Connection": "keep-alive",
    }
    return headers


def fill_queue(proxy_list, proxy_queue):

    for proxy in proxy_list:
        proxy_queue.put(proxy)
    proxy_queue.put('Q')


def check_and_return_proxy(proxy_queue, proxy_pool):
    url = 'https://log.mmstat.com/eg.js'
    while True:

        proxy = proxy_queue.get()
        if proxy == 'Q':
            proxy_queue.put('Q')
            break

        headers = make_a_headers()
        headers['Host'] = 'log.mmstat.com'
        headers['Referer'] = 'https://www.1688.com'
        s = requests.Session()
        try:
            s.get(url, headers=headers, proxies={
                'https': 'https://'+proxy}, timeout=2)
            cna = s.cookies.get('cna')
            proxy_pool[proxy] = {
                'cna': cna,
                'headers': make_a_headers()
            }
            # print(proxy_pool[proxy])
        except:
            continue


def check_ebay(proxy_queue, proxy_pool):
    url = 'http://www.ebay.com/'
    while True:
        proxy = proxy_queue.get()
        if proxy == 'Q':
            proxy_queue.put('Q')
            break
        headers = make_a_headers()
        headers['Host'] = 'www.ebay.com'
        headers['Referer'] = 'http://www.ebay.com'
        s = requests.Session()
        try:
            s.get(url, headers=headers, proxies={
                'http': 'http://'+proxy}, timeout=25)
            proxy_pool[proxy] = {}
        except Exception as e:
            print('proxy invaild {}'.format(proxy))
            continue


def check_baidu(proxy_queue, proxy_pool):
    url = 'http://www.baidu.com/'
    while True:
        proxy = proxy_queue.get()
        if proxy == 'Q':
            proxy_queue.put('Q')
            break
        headers = make_a_headers()
        headers['Host'] = 'www.baidu.com'
        s = requests.Session()
        try:
            s.get(url, headers=headers, proxies={
                'http': 'http://'+proxy}, timeout=25)
            proxy_pool[proxy] = {}
        except Exception as e:
            print('proxy invaild {}'.format(proxy))
            continue


def check_1688m(proxy_queue, proxy_pool):
    url = 'https://log.mmstat.com/eg.js'
    while True:

        proxy = proxy_queue.get()
        if proxy == 'Q':
            proxy_queue.put('Q')
            break
        headers = make_a_headers()
        headers['Host'] = 'log.mmstat.com'
        headers['Referer'] = 'https://www.1688.com'
        s = requests.Session()
        try:
            s.get(url, headers=headers, proxies={
                'https': 'https://'+proxy}, timeout=2)
            proxy_pool[proxy] = {}
        except Exception as e:
            continue


def get_proxy(proxy_url, check_fun=check_baidu):
    url = proxy_url
    resp = requests.get(url)
    proxy_list = json.loads(resp.text)['data']['proxy_list']

    proxy_queue = queue.Queue()
    proxy_pool = {}

    thread_list = []
    t1 = threading.Thread(target=fill_queue, args=(proxy_list, proxy_queue))
    thread_list.append(t1)

    for i in range(12):
        t = threading.Thread(target=check_fun,
                             args=(proxy_queue, proxy_pool))
        t.setDaemon(True)
        thread_list.append(t)

    for t in thread_list:
        t.start()

    for t in thread_list:
        t.join()

    return proxy_pool


def get_proxy_for_ebay(proxy_url):
    return get_proxy(proxy_url, check_ebay)


def get_proxy_for_1688m(proxy_url):
    return get_proxy(proxy_url, check_1688m)


def get_proxy_for_1688pc(proxy_url):
    return get_proxy(proxy_url, check_and_return_proxy)


if __name__ == '__main__':

    print(get_proxy_for_ebay())
