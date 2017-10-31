# -*- coding:utf-8 -*-
# Created by qinwei on 2017/8/4
import logging

import requests
from lxml.html import fromstring

from hunters.browser import UserAgent, ViewBrowser, BrowserConfig
from hunters.constant import Regex
from hunters.defaults import DefaultFilter
from hunters.spider import AutoSpider


def fetch():
    s = requests.session()
    s.headers['User-Agent'] = UserAgent.CHROME
    str = s.get("http://m.blog.csdn.net/tanzuozhev/article/details/50442243").text
    root = fromstring(str)
    print(fromstring("&#x01ce").text_content())


# for item in root.cssselect('script'):
#     print(item.get('src'))
#     html.escape(item.text or "")
#     print(item.text)
# for el in root.cssselect('a'):
#     print(el.attrib.get('href'))

# fetch()
# m = inspect.signature(url_gender)
# print(len(m.parameters))
FORMAT = "%(asctime)s [%(levelname)s] [%(name)s] %(threadName)s %(module)s[%(lineno)d]-%(message)s"

logging.basicConfig(level=logging.INFO, format=FORMAT)

logger = logging.getLogger("TEST")
view = BrowserConfig(browser_clazz=ViewBrowser)
app = AutoSpider(browser_config=view)


def test_charset():
    str__ = """
    <meta http-equiv="content-type" content="text/html;charset=gbk" />
    """
    match = Regex.RE_MATA_CHARSET.search(str__)
    print(match.group(1))


filter = DefaultFilter()

app.add_filter(filter.url_raw_filter)


@app.output(content_type=r"html")
def output_handler(tab, deep):
    titles = tab.dom().cssselect('title')
    if len(titles) > 0:
        print(tab.url, tab.encoding, titles[0].text, deep)


# @app.output(content_type=r"html")
def screen_shot(tab, deep):
    print("SAVE => %s" % tab.get_local_filename())
    # tab.window_size(1024, 4000)
    tab.screenshot_as_png(tab.get_local_filename() + "-screen.png")


app \
    .max_urls(50) \
    .max_deep(4) \
    .add_url("https://hao.360.cn/") \
    .run(4)
#
# br = app._browser;
# r = br.get("http://python.jobbole.com/81683/xxxx")
# print(r.ok)
