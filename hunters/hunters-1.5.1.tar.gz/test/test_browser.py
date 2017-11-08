# -*- coding:utf-8 -*-
# Created by qinwei on 2017/8/8
from urllib import parse

from hunters.core import MiniBrowser

t = MiniBrowser()
r = t.head("https://zhidao.baidu.com/", allow_redirects=True)
print(r.headers)
print(r.history)

# v = ViewBrowser()
# v._webdriver.get("https://zhidao.baidu.com")
# v._webdriver.implicitly_wait(3)
# print(v._webdriver.execute_script("return document.charset"))
url = "https://fex.bdstatic.com/hunter/alog/dp.csp.min.js?v=140804"
url = "https://baidu.com/"
# ParseResult(scheme='https', netloc='fex.bdstatic.com', path='/hunter/alog/dp.csp.min.js', params='', query='v=140804', fragment='')
m = parse.urlparse(url)
print(m.netloc + m.path)
