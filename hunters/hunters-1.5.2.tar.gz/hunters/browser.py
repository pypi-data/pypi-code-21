# -*- coding:utf-8 -*-
# Created by qinwei on 2017/8/7

##############################################################################
import logging
import os
from http.cookiejar import split_header_words
from time import sleep
from urllib import parse

import requests
from requests import Response, ReadTimeout
from requests.exceptions import ChunkedEncodingError, TooManyRedirects, SSLError
from selenium import webdriver
from selenium.common.exceptions import WebDriverException
from urllib3.exceptions import ProtocolError

from hunters.benchmark import BenchMark
from hunters.constant import Regex, Const
from hunters.cookie import MemoryCookieStore
from hunters.utils import decode_html, StringUtil

logger = logging.getLogger("browser")


class UserAgent(Const):
    """常用UA"""
    CHROME = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/59.0.3071.115 Safari/537.36"
    IPHONE = "Mozilla/5.0 (iPhone; CPU iPhone OS 9_1 like Mac OS X) AppleWebKit/601.1.46 (KHTML, like Gecko) Version/9.0 Mobile/13B143 Safari/601.1"
    ANDROID = "Mozilla/5.0 (Linux; Android 6.0; Nexus 5 Build/MRA58N) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/59.0.3071.115 Mobile Safari/537.36"


class BrowserConfig(object):
    """
        统一浏览器配置项
    """
    LOCAL_STORE = "/data/hunter/"

    def __init__(self, browser_clazz=None, user_agent=None, browser_option=None
                 , webdriver_location=None, browser_bin_locaion=None, local_store=None, image=True,
                 headless=True, webdriver=None, cookie_store=MemoryCookieStore()):
        self.browser_clazz = browser_clazz

        self.user_agent = user_agent or UserAgent.CHROME

        self.browser_bin_locaion = browser_bin_locaion

        self._webdriver_location = webdriver_location

        self.local_store = local_store or BrowserConfig.LOCAL_STORE

        self.image = image

        self._headless = headless

        self._browser_option = browser_option

        #: 分布式Cookie/会话保持, 在分布式环境中, 每产生的URL都插入中央队列, 每个爬虫(可能多台机)从中央队列里取出来的内容
        #: 是无状态的, 如果需要维持爬虫的上下文关系, 需要保证有分布式的session维持cookie内容,
        #: 这个cookie可以集中存储.
        self.cookie_store = cookie_store

        self.max_redirects = 3

        self.__webdriver = webdriver  # 指定WebRiver也不能很好的并發了

    def webdriver_location(self):
        return self._webdriver_location or os.environ.get("WEBDRIVER", "") or r"D:\webdriver\chromedriver.exe"

    def browser_option(self):
        return self._browser_option or self.get_default_chrome_option()

    def new_browser(self):
        if self.browser_clazz is not None and not issubclass(self.browser_clazz, Browser):
            raise TypeError("the browser_type[%s] error, not subclass by `Browser`" % self.browser_clazz)
        return self.browser_clazz(self)

    def webdriver(self):
        self.__webdriver = webdriver.Chrome(executable_path=self.webdriver_location(),
                                            chrome_options=self.browser_option())
        return self.__webdriver

    def get_default_chrome_option(self):
        option = webdriver.ChromeOptions()
        option.add_argument('--allow-running-insecure-content')
        option.add_argument('--disable-web-security')
        if self._headless:  #: 其他平台看配置
            option.add_argument("--headless")
            option.add_argument("--disable-gpu")

        option.add_argument("--disable-background-networking")
        option.add_argument("--disable-client-side-phishing-detection")
        option.add_argument("--window-size=1024,860")  # 超过5000似乎无效了
        option.add_argument("--user-agent=" + self.user_agent)

        if not self.image:
            prefs = {"profile.managed_default_content_settings.images": 2}  # disable image
            option.add_experimental_option("prefs", prefs)

        # Google这个坑货, 更新了62版本以后就不能通过set_window_size了
        if self.browser_bin_locaion:
            option.binary_location = self.browser_bin_locaion
            # or r"C:\Users\ADMIN\AppData\Local\Google\Chrome SxS\Application\chrome.exe"
        return option


class Browser(object):
    """ Abstract API """

    def __enter__(self):
        pass

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.quit()

    def get(self, url, **kwargs):
        pass

    def post(self, url, data, json, **kwargs):
        pass

    def head(self, url, **kwargs):
        pass

    def screenshot_as_png(self, filename):
        pass

    def window_size(self, width, height):
        pass

    def scroll_by(self, x, y):
        pass

    def wait(self, num):
        pass

    def execute_js(self, js_str):
        pass

    def close(self):
        """ 关闭当前窗口, 通常如果是Selenium实现的, 可能关闭的是浏览器 """
        pass

    def quit(self):
        """ 完全关闭进程, 通常如果是Selenium, 关闭浏览器和webdriver """
        pass

    def browser_config(self):
        pass

    @staticmethod
    def parse_url(url):
        """
        ParseResult(scheme='https', netloc='fex.bdstatic.com', path='/hunter/alog/dp.csp.min.js', params='', query='v=140804', fragment='')
        :param url:
        :return:
        """
        return parse.urlparse(url)

    @staticmethod
    def get_host(url):
        return parse.urlparse(url).netloc


class MiniBrowser(Browser):
    """
    文本型/单请求/微浏览器实现,
    基于requests,
    requests, Cookie自动保持, URL跳转自动跟随, 自动解析文本decode, 都是浏览器必有特性
    decode比较弱, 自己重新实现了一个, 更能准确判断gbk和utf8
    """

    def __init__(self, browser_config=BrowserConfig()):
        # self.session.mount("data:", DataAdapter) TOTO
        self._browser_config = browser_config

    @property
    def session(self):
        # XXX 解决同一个session长期复用会导致内存一致涨的问题
        session = requests.session()
        session.headers['User-Agent'] = self._browser_config.user_agent
        session.max_redirects = self._browser_config.max_redirects
        return session

    @property
    def cookie_store(self):
        return self.browser_config().cookie_store

    def browser_config(self):
        return self._browser_config

    def __enter__(self):
        pass

    def __exit__(self, exc_type, exc_val, exc_tb):
        pass

    def close(self):
        pass

    def quit(self):
        pass

    def head(self, url, **kwargs):
        try:
            kwargs.setdefault("timeout", 2)  # head 请求如果2秒没啥返回, 说明拒绝head或者访问失败了
            assert url.startswith("http"), "HEAD only support http or https"
            return self.session.head(url, **kwargs)
        except Exception as e:
            logger.error("url[%s], msg[%s]" % (url, e))
            r = Response()
            r.headers = {}
            r.url = url
            r.status_code = 503  #: 服务无法访问
            return r

    def cookies_str(self, host):
        cookies_dict = self.cookies(host)
        result = ""

        for (k, v) in cookies_dict.items():
            result += "%s=%s; " % (StringUtil.replace_blank(k), StringUtil.replace_blank(v))

        return result

    def cookies(self, host):
        """从会话中拿出cookie"""
        return self.cookie_store.get(host) or {}

    def _mrg_cookies(self, host, cookies):
        """
        合并cookies
        :param cookies: list[tuple] or dict or "A=1; B=3"
        :return:
        """
        last_cookies = self.cookies(host)
        if isinstance(cookies, dict):
            last_cookies.update(cookies)
        else:
            if isinstance(cookies, str):
                #: split word ["A=1"] ==> [[(A, 1)]]
                cookies = split_header_words([cookies])[0]

            for item in cookies:
                last_cookies.update({item[0]: item[1]})

        self.cookie_store.set(host, last_cookies)
        return last_cookies

    def _set_header_cookie(self, host, **kwargs):

        headers = kwargs.get("headers", {})
        user_cookie = headers.get("Cookie")  #: 用户自己配置Cookie的情况下, 合并
        if user_cookie:
            self._mrg_cookies(host, user_cookie)
        headers.update({'Cookie': self.cookies_str(host)})
        kwargs.setdefault("headers", headers)
        return kwargs

    def _check_cookies(self, host, response, cookie_dict=None):
        if "Set-Cookie" in response.headers:
            self._mrg_cookies(host, cookie_dict)  #: 合并到会话级别, cookies中

    def get(self, url, **kwargs):
        b = BenchMark(__name__)
        try:
            # extract_cookies_to_jar(self.session.cookies, req, urllib3.HTTPResponse())
            host = self.get_host(url)
            kwargs = self._set_header_cookie(host, **kwargs)
            kwargs.setdefault("stream", True)  #: lazyLoad , 避免读取大文件
            with self.session as session:
                try:
                    r = session.get(url, **kwargs)
                except SSLError as err:  # 这里可能会报Https鉴权错误
                    kwargs.setdefault("verify", False)
                    r = session.get(url, **kwargs)
                    setattr(r, "SSLError", True)  # 配置一个标记说明存在鉴权, 让后续者鉴定错误
                    logger.error("SSLError, url[%s], err[%s]", url, err)

                self._check_cookies(host, r, session.cookies.items())

            return self.__detect_encoding(r)

        except TooManyRedirects as err:
            r = Response()
            r.status_code = 5302
            r.reason = "TooManyRedirects"
            r._content = b"TooManyRedirects"
            r.ori_url = url
            logging.warning("TooManyRedirects:[%s]" % url)
            return r
        except Exception as e:
            #: 如果是requests都无法访问, 说明连接不可用.
            r = Response()
            r.status_code = 5031  #: 连接不可达, r.ok 的判断是根据statucode 是否 == 0, 这里错误也返回一个response
            r.headers.setdefault("content-type", "error/ConnectionError")  #: 构造一个本地的错误头, 标识错误.
            r._content = bytes(str(e), "UTF8")  #: 将错误内容放进response
            logger.error("connect url:[%s] ,error[%s]" % (url, e))
            return r

        finally:
            b.mark("GET OK")

    def post(self, url, data=None, json=None, **kwargs):
        host = self.get_host(url)
        self._set_header_cookie(host, **kwargs)
        with self.session as session:
            r = self.session.post(url, data, json, **kwargs)
            self._check_cookies(host, r, session.cookies.items())
        return self.__detect_encoding(r)

    def screenshot_as_png(self, filename):
        logger.warning("IGNORE screenshot_as_png for textBrowser")

    def window_size(self, width, height):
        logger.warning("IGNORE window_size for textBrowser")

    def scroll_by(self, x, y):
        logger.warning("IGNORE scroll_by for textBrowser")

    def wait(self, num):
        logger.warning("IGNORE scroll_by for textBrowser")

    def execute_js(self, js_str):
        logger.warning("IGNORE execute_js for textBrowser")

    @staticmethod
    def __detect_encoding(response):
        """ 尝试检测页面编码 """
        #: 'text/html; charset=GB2312'
        #: 'application/json'
        content_type = response.headers.get("Content-Type", "error/no-content-type")
        if not Regex.RE_TYPE_PLAIN.search(content_type):
            #: 必须是文本类型才能检测, 二进制的忽略
            return response

        before_encoding = response.encoding  #: 'ISO-8859-1'
        detect_encoding = None

        #: 有的网站不按常理出牌, 返回content-type是charset=gbk,但是内容meta是utf8,比如QQ某个网站
        #: 但是调试发现浏览器有优先级, 如果返回头返回了编码, 以返回头为准, 否则看页面的meta[charset]值
        match = Regex.RE_CONTENT_TYPE_CHARSET.search(content_type)
        if match:
            detect_encoding = match.group(1)

        elif Regex.RE_TYPE_HTML.search(content_type):
            match = Regex.RE_MATA_CHARSET.search(response.text)
            if match:
                detect_encoding = match.group(1)  # 解决乱码问题

        #: 如果都没有编码信息, 就探测编码
        if detect_encoding is None and before_encoding in (None, 'ISO-8859-1'):  #: 'ISO-8859-1' 编码特别不准. 至少GBK, UTF-8也兼容他
            detect_encoding = response.apparent_encoding  #: 检测编码

        if detect_encoding is None:
            detect_encoding = "UTF-8"
        #: GB18030 (7W字) > GBK (2W字) > BIG5(繁体) > GB2312 (6K字)
        #: 如果检测出使用GB2312 , 有超出范围的罕见字符会有乱码, 改成兼容性更强的GBK
        if detect_encoding.upper() == "GB2312":
            detect_encoding = "GBK"

        response.encoding = detect_encoding
        logging.debug("DETECT ENCODING, url[%s], encoding[%s], before[%s]", response.url, response.encoding, before_encoding)
        return response


##################################### ViewBrowser ##################################################

class ViewBrowser(Browser):
    """Selenium 实现"""

    def __init__(self, browser_config=BrowserConfig()):

        self._browser_config = browser_config

        self._minibrowser = MiniBrowser(browser_config)  # 这里还需要一个文本浏览器配合, 比如JS, 图片等这类请求不需要ViewBrowser渲染

        self._webdriver = browser_config.webdriver()

        self.ok = False  # 兼容requsts.Respone
        self._text = None
        self.content = None
        self.raw = None
        self.page_source_cache = False

        self._window_width = 1024
        self._window_height = 800

    def __enter__(self):
        pass

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.quit()

    def browser_config(self):
        return self._browser_config

    @property
    def text(self):
        if self.page_source_cache and self._text:
            return self._text
        self._text = decode_html(self._webdriver.page_source)
        return self._text

    def get(self, url, **kwargs):
        b = BenchMark("view-browser-get")
        r = Response()
        try:
            #: 原本想预先用HEAD请求, 但是发现有的网站不支持head,比如qq, 为了兼容性, 直接用get
            #: 但是需要注意返回大小, 可以用range: bytes=0-500限制返回体大小
            r = self._minibrowser.get(url, **kwargs)
            #: 如果访问正常, 并且返回的是HTML格式, 才用Headless请求, 否则用Headless请求没有意义
            if r.ok and Regex.RE_TYPE_HTML.search(r.headers.get("content-type", "")):
                self._webdriver.get(url)  #: webdriver不支持直接配置请求头请求, 而是一开始就配置了.
                r.encoding = "UTF-8"  # 发现 page_source 自动解析了编码成UTF8了
                r.url = self._webdriver.current_url  #: 这里以浏览器为主, 可能JS重定向后的地址
                # r.status_code = 200 , 这里以requests的返回值为准, 200~400 ok== true
                self._text = None  # 清空当前页面信息, 等待后续调用重新取
                setattr(r, "headless", True)
                return ProxyResponse(browser=self, response=r)
        except Exception as e:
            #: 通常情况下, 链接是否可用, 是由minibrowser保证的. 如果minibrowser返回失败, 将不使用headless请求
            #: 如果这里还存在其他异常, 可能是致命的,可能chromedriver或者浏览器有请情况.
            #: 重新推出并杀死本线程重来吧~
            self.quit()
            logger.exception(e)
            raise e
        finally:
            b.mark("GET")
        return r

    def wait(self, num):
        # self._webdriver.implicitly_wait(num)
        sleep(num)
        return self

    def post(self, url, data, json, **kwargs):
        raise NotImplemented("ViewBrowser Not Support POST method")

    def close(self):
        self._webdriver.close()
        return self

    def scroll_by(self, x, y):
        """ 执行JS进行滚动条滚动, 触发某些异步加载的瀑布流加载 """
        return self.execute_js("window.scrollBy({}, {})".format(x, y))

    def head(self, url, **kwargs):
        return self._minibrowser.head(url, **kwargs)

    def execute_js(self, js_str):
        b = BenchMark("execute_js")
        try:
            self.page_source_cache = False  # 取消缓存
            return self._webdriver.execute_script(js_str)
        finally:
            b.mark("ok")

    def screenshot_as_png(self, filename):
        """ 截屏, 如果指定了文件, 输出到文件, 如果没有指定, 返回一个png的bytes """
        b = BenchMark("screenshot_as_png")
        try:
            if filename:
                filename = os.path.join(self._browser_config.local_store, filename)
                if filename.startswith(self._browser_config.local_store) and "../" not in filename:
                    self._webdriver.save_screenshot(filename)
                else:
                    raise PermissionError("deny to write outside %s" % self.local_store)

            return self._webdriver.get_screenshot_as_png()
        finally:
            b.mark("ok")

    def window_size(self, width, height):
        self._window_width = width
        self._window_height = height
        b = BenchMark("window_size")
        try:
            self._webdriver.set_window_size(width, height)
        except WebDriverException as e:
            logger.warning(e)
        finally:
            b.mark("window_size ok")
        return self

    def quit(self):
        self._webdriver.quit()
        return self


class ProxyResponse(object):
    """
    代理Response的某些方法
    """

    def __init__(self, browser, response):
        self.browser = browser
        self.response = response
        self.__dict__.update(response.__dict__)

    @property
    def text(self):
        return self.browser.text
