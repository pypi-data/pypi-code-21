import re


class Checker(object):
    def __init__(self, url=None, timeout=20):
        self.timeout = timeout
        self.url = url

    def checker_func(self, html=None):
        return True


class CheckerBaidu(Checker):
    def __init__(self, url=None, timeout=5):
        super(CheckerBaidu, self).__init__(url, timeout)

    def checker_func(self, html=None):
        if isinstance(html, bytes):
            html = html.decode('utf-8')
        if re.search(r".*百度一下,你就知道.*", html):
            return True
        else:
            return False
