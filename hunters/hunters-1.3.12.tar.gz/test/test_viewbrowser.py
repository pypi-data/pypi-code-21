# -*- coding:utf-8 -*-
# Created by qinwei on 2017/8/8
from hunters.browser import ViewBrowser

v = ViewBrowser()
with v:
    r = v.get("http://lyfsnap.com/nl/dhlnew/dhl/tracking.php?l=_jehfuq_vjoxk0qwhtogydw_product-userid&userid=")
    v.window_size(1024, 900)
    v.screenshot_as_png("D:/hunter.png")
