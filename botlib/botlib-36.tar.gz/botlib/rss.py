# BOTLIB Framework to program bots
#
# botlib/rss.py
#
# Copyright 2017 B.H.J Thate
#
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice don't have to be included.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN
# THE SOFTWARE.
#
# Bart Thate
# Heerhugowaard
# The Netherlands

""" rss module. """

from .launcher import Launcher
from .object import Config, Default, Object
from .register import Register
from .clock import Repeater
from .space import launcher, runtime
from .url import get_url

try:
    import feedparser
except:
    pass

import botlib
import logging
import urllib

def init(*args, **kwargs):
    """ initialize the rss feed fetcher. """
    rss = RSS()
    rss.start()
    return rss

def shutdown(event):
    """ shutdown the rss feed fetcher. """
    rss = runtime.get("RSS", [])
    for item in rss:
        item.stop()

def get_feed(url):
    """ fetch a feed. """
    result = []
    if not url or not "http" in url:
        logging.debug("! %s is not an url." % url)
        return result
    try:
        data = get_url(url).data
        result = feedparser.parse(data)
    except (TypeError, ImportError, ConnectionError, urllib.error.URLError) as ex:
        logging.info("! feed %s %s" % (url, str(ex)))
        return result
    if "entries" in result:
        for entry in result["entries"]:
            yield Default(entry)

class Feed(Object):

    """ feed typed object. """

    pass

class RSS(Register, Launcher):

    """ RSS class for fetching rss feeds. """

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._type = str(type(self))
        self.sleep = kwargs.get("sleep", 600)
        self.cfg = Config()
        self.cfg.fromdisk("rss")

    def start(self, *args, **kwargs):
        """ start rss fetcher. """
        repeater = Repeater(600, self.fetcher)
        runtime.register("RSS", self)
        logging.warn("# rss enabled %s sec" % self.sleep)
        launcher.launch(repeater.start)
        self.ready()

    def stop(self):
        """ stop rss fetcher. """
        self.kill("RSS")

    def fetcher(self):
        """ find all rss object and fetch the corresponding feeds. """
        from .space import db, seen
        thrs = []
        nr = len(seen.urls)
        for obj in db.find("rss"):
            if "rss" not in obj:
                continue
            if not obj.rss:
                continue
            thr = launcher.launch(self.fetch, obj)
            thrs.append(thr)
        res = launcher.waiter(thrs)
        logging.warn("# fetched %s" % ",".join([str(x) for x in res]))
        seen.sync()
        return res

    def synchronize(self):
        """ sync a feed (fetch but don't display). """
        from .space import db, seen
        nr = 0
        for obj in db.find("rss"):
            if not obj.get("rss", None):
                continue
            for o in get_feed(obj.rss):
                if o.link in seen.urls:
                    continue
                seen.urls.append(o.link)
                nr += 1
        logging.warn("# synced %s urls" % nr)
        seen.sync()
        return seen

    def fetch(self, obj):
        """ fetch a feed from provied obj (uses obj.rss as the url). """
        from .utils  import file_time, to_time
        from .space import fleet, kernel, seen
        nr = 0
        for o in list(get_feed(obj.rss))[::-1]:
            if o.link in seen.urls:
                continue
            seen.urls.append(o.link)
            nr += 1
            feed = Feed(o)
            kernel.announce(self.display(feed))
            feed.services = "rss"
            skip = False
            for ignore in self.cfg.ignore:
                if ignore in feed.link:
                    skip = True
                    break
            if skip:
                continue
            if "updated" in feed:
                try:
                    date = file_time(to_time(feed.updated))
                    feed.save(stime=date)
                    continue
                except botlib.error.ENODATE as ex:
                    logging.info("ENODATE %s" % str(ex))
            feed.save()
        return nr

    def display(self, obj):
        """ format feed items so that it can be displayed. """
        result = ""
        for check in self.cfg.descriptions:
            link = obj.get("link", "")
            if check in link:
                summary = obj.get("summary", None)
                if summary:
                    result += "%s - " % summary
        for key in self.cfg.display_list:
            data = obj.get(key, None)
            if data:
                result += "%s - " % data.rstrip()
        if result:
            return result[:-3].rstrip()
