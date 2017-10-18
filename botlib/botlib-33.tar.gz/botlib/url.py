# BOTLIB Framework to program bots
#
# botlib/url.py
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
# The above copyright notice and this permission notice shall be included in
# all copies or substantial portions of the Software.
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

""" functions that fetch data from url. """

from .object import Object

import logging
import urllib
import http
import html
import botlib
import sys
import re

def get_url(*args, **kwargs):
    """ fetch an url, return the reponse object. """
    url = urllib.parse.urlunparse(urllib.parse.urlparse(args[0]))
    req = urllib.request.Request(url, headers={"User-Agent": useragent()})
    resp = urllib.request.urlopen(req)
    resp.data = resp.read()
    logging.debug("%s %s %s" % (resp.status, resp.reason, url))
    return resp

def get_url2(url, myheaders={}, postdata={}, keyfile=None, certfile="", port=80):
    """ second version of get_url that uses http.client instead of urllib. """
    headers = {'Content-Type': 'application/x-www-form-urlencoded;charset=utf-8', 'Accept': 'text/plain; text/html; application/json', 'User-Agent': useragent()}
    headers.update(myheaders)
    urlparts = urllib.parse.urlparse(url)
    if "https" in url:
        connection = http.client.HTTPSConnection(urlparts[1]) # keyfile, certfile)
    else:
        connection = http.client.HTTPConnection(urlparts[1])
    connection.connect()
    connection.request("GET", urlparts[2], None, headers)
    resp = connection.getresponse()
    resp.data = resp.read()
    logging.debug("%s %s %s" % (resp.status, resp.reason, url))
    connection.close()
    return resp

def need_redirect(resp):
    """ check whether redirect is necessary. """
    if resp.status == 301 or resp.status == 302:
        url = resp.getheader("Location")
        return url

def useragent():
    """ return a useragent string. """
    return 'Mozilla/5.0 (X11; Linux x86_64) BOTLIB %s +https://bitbucket.org/bthate/botlib)' % botlib.__version__

def unescape(text):
    """ unescape html characters. """
    return html.parser.HTMLParser().unescape(text)

def extract_div(search, data):
    """ extract <div> record. """
    from bs4 import BeautifulSoup
    soup = BeautifulSoup(data)
    divs = soup('div')
    for div in divs:
        if div.get(search):
            return div

def get_encoding(data):
    """ return encoding of a web page, provide raw html as data. """
    if hasattr(data, 'info') and 'content-type' in data.info and 'charset' in data.info['content-type'].lower():
        charset = data.info['content-type'].lower().split('charset', 1)[1].strip()
        if charset[0] == '=':
            charset = charset[1:].strip()
            if ';' in charset:
                return charset.split(';')[0].strip()
            return charset
    if '<meta' in data.lower():
        metas = re.findall('<meta[^>]+>', data, re.I | re.M)
        if metas:
            for meta in metas:
                test_http_equiv = re.search(r'http-equiv\s*=\s*[\'"]([^\'"]+)[\'"]', meta, re.I)
                if test_http_equiv and test_http_equiv.group(1).lower() == 'content-type':
                    test_content = re.search(r'content\s*=\s*[\'"]([^\'"]+)[\'"]', meta, re.I)
                    if test_content:
                        test_charset = re.search(r'charset\s*=\s*([^\s\'"]+)', meta, re.I)
                        if test_charset:
                            return test_charset.group(1)
    try:
        import chardet
        test = chardet.detect(data)
        if 'encoding' in test:
            return test['encoding']
    except:
        pass
    return sys.getdefaultencoding()

def parse_url(*args, **kwargs):
    """ scheme://netloc/path?query:fragment. """
    url = args[0]
    _parsed = urllib.parse.urlsplit(url)
    target = _parsed[2].split("/")
    if "." in target[-1]:
        basepath = "/".join(target[:-1])
        file = target[-1]
    else:
        basepath = _parsed[2] ; file = None
    if basepath.endswith("/"):
        basepath = basepath[:-1]
    base = urllib.parse.urlunsplit((_parsed[0], _parsed[1], basepath, "", ""))
    root = urllib.parse.urlunsplit((_parsed[0], _parsed[1], "", "", ""))
    return (basepath, base, root, file)

def parse_urls(*args, **kwargs):
    """ parse a webpage to find urls mentioned in it. """
    import bs4
    url = args[0]
    try:
        content = args[1]
    except:
        content = get_url(url).data
    basepath, base, root, file = parse_url(url)
    s = bs4.BeautifulSoup(content, "lxml")
    urls = []
    tags = s('a')
    for tag in tags:
        href = tag.get("href")
        if href:
            href = href.split("#")[0]
            if not href:
                continue
            if ".." in href:
                continue
            if href.startswith("mailto"):
                continue
            if not "http" in href:
                if href.startswith("/"):
                    href = root + href
                else:
                    href = base + "/" + href
                if not root in href:
                    continue
            if href not in urls:
                urls.append(href)
    logging.debug("parsed %s urls" % len(urls))
    return urls

def strip_html(text):
    """ strip html code. """
    if text.startswith("http"):
        return text
    import bs4
    soup = bs4.BeautifulSoup(text, "lxml")
    res = ""
    for chunk in soup.findAll(text=True):
        if isinstance(chunk, bs4.CData): res += str(chunk.content[0]) + " "
        else: res += str(chunk) + " "
    return res

def get_feed(url):
    """ fetch a feed. """
    result = []
    if not url or not "http" in url:
        logging.debug("%s is not an url." % url)
        return result
    try:
        import feedparser
        result = feedparser.parse(get_url(url).data)
    except (ImportError, ConnectionError, urllib.error.URLError) as ex:
        logging.warn("# %s %s" % (url, str(ex)))
        return result
    if "entries" in result:
        for entry in result["entries"]:
            yield Object(entry)
