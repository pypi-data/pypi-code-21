# -*- coding:utf-8 -*-
# Created by qinwei on 2017/8/9
#
# 一些常量的定义
#
import re


class MetaConst(type):
    """
    创建常量类的元类
    """

    def __getattr__(cls, key):
        return cls[key]

    def __setattr__(cls, key, value):
        raise TypeError("constant[{}] can't not be assign".format(key))


class Const(object, metaclass=MetaConst):
    """
    常量的基类, 需要声明常量的都可以继承这个.
    """

    def __new__(cls, *args, **kwargs):
        raise TypeError("")

    def __getattr__(self, name):
        return self[name]

    def __setattr__(self, name, value):
        raise TypeError("constant [{}] can't not be assign".format(name))


class AddUrlResultType(Const):
    OK = 1
    OVERLIMIT = 0
    FILTER_UN_PASS = -1
    URL_ERROR = -2


class Regex(Const):
    """
    所有用到正则表达式尽量这里进行统一管理, 方便针对每个正则进行排查测试, 统一复用
    """

    RE_TYPE_PLAIN = re.compile(r"text|html|javascript|json|plain|xml", re.I)

    RE_TYPE_HTML = re.compile(r"html", re.I)

    RE_TYPE_JS = re.compile(r"javascript", re.I)

    RE_TYPE_JSON = re.compile(r"json", re.I)

    # content type HTMl内容里如果发现html, 需要自动解析, requests content-type把charset过滤了.
    # 正常的Content-Type: text/html; charset=utf8
    # 取出来的是 text/html
    RE_MATA_CHARSET = re.compile(r"""<meta.*?charset=["']?([^/>\s;"']+)""", re.I)

    RE_CONTENT_TYPE_CHARSET = re.compile(r"""charset=(.*)""", re.I)

    #: 去掉URL后面的#所有内容
    RE_URL_COMMENT = re.compile(r"#.*")

    """
    一次性获取各种链接类型
    <script src=""
    <a href=""
    <iframe src=""
    <meta http-equiv="refresh" content="0;url=http://www.baidu.com/">
    location.href=""
    window.open()
    测试发现把JS里的变量声明都匹配了(var src=""). 不管. 原则: 宁可错伤, 也不能少获取
    """
    RE_LINK = re.compile(r"""(?:href|url|src|open)\s*[=\\(]\s*["']?([^\s\\)>'"]+)""", re.I)

    #: 常见二进制文件后缀, 如果URL后缀包含如下, 可以不考虑加入抓取队列, 这里只是简单过一下, 可以过掉大部分连接了
    RE_RAW_LINK = re.compile(r"""\.(png|gif|jpg|jpeg|doc|zip|rar|bin|gz|tar|docx|xls|xlsx|swf|woff|eot|ttf|svg)$""", re.I)

    #: 非视图文件, 不需要View渲染的
    RE_JS_CSS_LINK = re.compile(r"\.(js|css|json)$")