# -*- coding:utf-8 -*-
import inspect
import logging
import os
import queue
import re
import threading
from queue import Queue

from lxml.etree import ParserError
from requests import Response

from hunters.atomic import AtomicLong
from hunters.benchmark import BenchMark
from hunters.browser import MiniBrowser, Browser, BrowserConfig, UserAgent, ViewBrowser
from hunters.constant import Regex, AddUrlResultType
from hunters.exceptions import spider_exception_listener
from hunters.utils import get_real_url, remove_xml_encoding, dom

logger = logging.getLogger("spider")


def dynamic_params(func, params):
    """
    动态参数解析, 根据函数声明动态的识别并返回参数集
    Python传递参数要和声明一致, 除非参数声明有默认值, 如果传递一个非声明的参数会报错.
    这里会过滤掉, 只返回函数声明的参数列表(dict)
    """
    params_desc = inspect.getfullargspec(func)
    result = {}
    for name in params_desc[0]:  #: 在函数声明
        if name in params:  #: 并且在规定注入列表中
            result[name] = params.get(name)
    return result


class TaskMeta(object):
    """
    任务模式下的描述数据
    也是Spider运行时候的上下文,
    在手动调用add_url时, 为保持上下文关系, 应该继续传递下去, 否则在递归或者循环中失去了上下文联系
    """

    __attrs__ = [
        "task_id", "count", "max_count", "max_deep"
    ]

    def __init__(self, task_id="default", max_count=10, max_deep=3, count=0):
        self.mutex = threading.Lock()
        self.max_deep = max_deep
        self.max_count = max_count
        self.count = count

        #: 由于任务是多线程并发处理, 并且有的线程又会不断扫描页面生成新的URL插入队列.直到到达max_count不能再插入
        #: 而当前任务尚有很多URL是在队列中等待处理. 只有当前taskid所有产生的URL处理完才能作为任务结束.
        #: 外部系统只能通过任务剩余URL数量remain_count来作为整个任务结束的标志.
        self.remain_count = 0

        #: 当前深度
        self.deep = 0
        #: 任务ID
        self.task_id = task_id

    def to_dict(self):
        return {'max_deep': self.max_deep, 'max_count': self.max_count,
                'count': self.count, 'remain_count': self.remain_count,
                'deep': self.deep, 'task_id': self.task_id}

    @staticmethod
    def from_dict(dictdata):
        obj = {}
        for item in TaskMeta.__attrs__:
            obj[item] = dictdata.get(item)
        tm = TaskMeta(**obj)
        tm.remain_count = dictdata.get('remain_count', 0)
        tm.deep = dictdata.get("deep", 0)
        return tm

    def incr_url_count(self):
        with self.mutex:
            self.count += 1
            self.remain_count += 1

    def overlimit(self):
        #:  URL两个约束条件, URL数量上限, URL深度,
        return self.count >= self.max_count or self.deep > self.max_deep

    def extend_default_value(self, max_url, max_deep):
        """ 配置默认值, 如果task_meta原来没有配置, 就用给定的默认值 """
        self.max_count = self.max_count or max_url
        self.max_deep = self.max_deep or max_deep

    def finish_one(self):
        """ 标记完成一个 """
        with self.mutex:
            self.remain_count -= 1

    def is_lastone(self):
        """
        判断是否是最后一个
        这里还是封装一下好, 一般在output里面调用, 方便在output中对任务结束时做进一步处理, 不容易造成误解,
        到底是remain_count == 1, 还是==0 , 用户不需要关心逻辑
        除非他知道处理完output以后, remain_count才会 -1.
        """
        return self.remain_count == 1


class Spider(object):
    """
    基本爬虫核心
    爬虫主要实现主流程
    AddURL -> Filter(N个)-> QUEUE  -> getPage -> Output(N个) 这样的主过程
    """

    def __init__(self, browser_config=BrowserConfig(), queue=Queue()):
        self._url_count = AtomicLong()  # 当前URL数量
        self._default_task_meta = TaskMeta(max_count=10, max_deep=3)
        self._threadLocal = threading.local()
        self._browser_config = browser_config
        self._url_queue = queue  # URL队列
        self._all_filters = []  # 过滤器
        self._all_outputs = []  # 输出控制器
        self._threadPool = None
        self._wait_timeout = 10
        self._max_body_size = 500 * 1024  #: 最大返回大小500k
        self._request_timeout = 20  #: 20s 请求超时
        self._max_redirect = browser_config.max_redirects or 3

        if self._browser_config.browser_clazz is None:
            #: 获取类, 到时候多线程创建副本用
            self._browser_config.browser_clazz = MiniBrowser

    @property
    def queue(self):
        return self._url_queue

    def max_redirects(self, num):
        self._max_redirect = num
        return self

    def request_timeout(self, num):
        self._request_timeout = num
        return self

    def wait_timeout(self, num):
        self._wait_timeout = num
        return self

    def max_body_size(self, num):
        self._max_body_size = num
        return self

    def max_deep(self, deep):
        if isinstance(deep, int):
            self._default_task_meta.max_deep = deep
        return self

    def max_urls(self, num):
        if isinstance(num, int):
            self._default_task_meta.max_count = num
        return self

    def mobile(self, user_agent=UserAgent.IPHONE):
        """ 设置使用移动浏览器 """
        self._browser_config.user_agent = user_agent
        return self

    def enable_view(self, headless=True, image=True):
        """ 配置使用 Chrome 做默认浏览器"""
        self._browser_config.browser_clazz = ViewBrowser
        self._browser_config.image = image
        self._browser_config._headless = headless
        return self

    def browser(self):
        if not hasattr(self._threadLocal, "browser"):
            self._threadLocal.browser = self._browser_config.new_browser()
        return self._threadLocal.browser

    def add_url(self, url, base_url=None, deep=0, headers=None, task_meta=None, extra=None):
        """
        添加URL到抓取队列, 如果超过限制,不会添加

        :param url: 当前页面的解析出来的URL, 可能是相对路径, ../about , /a/m/info.html
        :param base_url: 当前页面的URL, (url)都是相对于base_url, 会自动转成绝对URL
        :param deep: 当前深度
        :param task_meta 用任务id区分url爬取任务. 可以实现对整体服务的重用, 比如每个task有独立的url(计数器, 深度),
                         跟总的计数器分开
        :param headers 当前url请求指定的header, 比如UA, 会用UA进行请求.
        :param extra: 额外参数
        :return: 0 达到Limit值,不能能添加
                 1 成功添加
                 -1 过滤器过滤失败.
                 -2 参数错误
        """
        absolute_url = get_real_url(base_url, url)

        #: 如果没有任务描述,使用默认的, 后续的output需要注意将任务描述一起传递, 维持任务状态
        task_meta = task_meta or self._default_task_meta
        task_meta.deep = deep

        # URL两个约束条件, URL数量上限, URL深度, 如果URL长度为空也取消
        if len(absolute_url) == 0:
            """空白URL"""
            return AddUrlResultType.URL_ERROR

        if task_meta.overlimit():
            warn_msg = "add url[%s] overlimit, ignore taskInfo: %s" % (absolute_url, task_meta.to_dict())
            logger.info(warn_msg)
            return AddUrlResultType.OVERLIMIT

        if headers is None:
            headers = {}

        if base_url is not None:
            headers.setdefault("Referer", base_url)

        url_params = self._param_to_dict(url=absolute_url, deep=deep, headers=headers, task_meta=task_meta,
                                         extra=extra)

        filter_result = self.do_filter(**url_params)

        if AddUrlResultType.OK != filter_result:
            return filter_result

        task_meta.incr_url_count()  #: 通过了过滤器, 对应任务的URL计数器递增1

        logger.debug("Add To Queue [%s], origin:[%s], base_url:[%s] count[%s]", absolute_url, url, base_url,
                     task_meta.count)

        self.each_url_handle(**url_params)

        return AddUrlResultType.OK

    @staticmethod
    def _param_to_dict(url, deep, headers, task_meta, extra):
        #: 这些参数可以在filter/output声明的时候用依赖注入方式注入, 只需要声明参数名称相同
        return {
            'url': url,
            'deep': deep,
            'headers': headers,
            'task_meta': task_meta,
            'extra': extra or dict()
        }

    def do_filter(self, url, deep, headers, task_meta, extra):
        bm = BenchMark("all-filter")

        params_ = self._param_to_dict(url, deep, headers, task_meta, extra)

        for filter_ in self._all_filters:
            if not filter_.match(deep):
                # 如果不是匹配的深度就跳过, 每个URL都根据配置进行过滤
                continue

            dy_param = dynamic_params(filter_.real_func, params_)

            if not filter_.invoke(**dy_param):
                logging.debug("Not Pass Filter=[{}], [{}]".format(filter_.real_func.__name__, url))
                return AddUrlResultType.FILTER_UN_PASS
            bm.mark("OK")

        return AddUrlResultType.OK

    def each_url_handle(self, url, deep, headers, task_meta, extra):
        url_params = self._param_to_dict(url, deep, headers, task_meta, extra)
        self.queue.put(url_params)

    def filter(self, start_deep=1):

        """ @app.filter定义过滤器, 只有过滤器返回true才会继续执行

        @:param start_deep:  支持配置起始深度过滤, 因为第一个URL是deep=0, 有可能也需要过滤, 可以对起始URL进行过滤
        """

        def decorator(func):
            self.add_filter(func, start_deep)
            return func

        return decorator

    def _check_body_size(self, response):
        """ 检测内容是否超标 """
        length = 0
        try:
            length = int(response.headers.get("content-length", 0))
            # 任何返回头可能不规范, 有的可能没有返回长度, 1099,1099
        except Exception as e:
            pass

        if 0 < self._max_body_size < length:
            logger.warning("url[{}], over size:[{}]".format(response.url, length))
            response.close()

    def get_page(self, url, headers=None):
        """ 根据URL 获取页面结果 """
        response = self.browser().get(url, headers=headers, timeout=self._request_timeout)

        self._check_body_size(response)

        response.ori_url = url  #: 记录一下原始URL, 因为有的URL重定向了. 当前页面获取的URL就是重定向后的

        return Tab(browser=self.browser(), response=response)  #: 返回一个标签页

    def output(self, content_type=r".*"):
        """ @app.output装饰器来添加输出控制器, 利用content_type指定只处理的类型 """

        def decorator(func):
            self.add_output(content_type, output=func)
            return func

        return decorator

    @staticmethod
    def _default_headers(headers):
        default_headers = {}
        default_headers.update(headers or {})
        return default_headers

    def _do_url_task_from_queue(self):

        if self._wait_timeout:
            item = self.queue.get(timeout=self._wait_timeout)
        else:
            item = self.queue.get()

        url_ = item.get('url')
        deep_ = item.get('deep', 0)
        task_meta = item.get("task_meta")  #: 必须存在
        extra_ = item.get('extra', None)  #: 额外传递的参数, 附属内容传递给filter或者output
        headers_ = item.get('headers', {})

        self.start_query(url_, deep_, headers_, task_meta, extra_)

    def start_query(self, url, deep, headers=None, task_meta=None, extra=None):
        """ 执行抓取动作, 返回结果经过output捕获 """
        bm = BenchMark("queue-item")

        default_headers = self._default_headers(headers)

        try:
            tab = self.do_url(url, deep, default_headers, task_meta, extra)

            self.do_output(tab, url=url, deep=deep, headers=headers, task_meta=task_meta, extra=extra)

        except Exception as e:  # 这里有可能网络请求抛出各种异常
            #: 有的是网页无法访问
            logger.error("GET PAGE, url[%s], msg[%s]", url, e)
            spider_exception_listener.handle_exception(e)
        finally:
            #: 从队列里取出来的URL,执行完成后, 在这个任务中标记完成了一个URL, 直到remain_count为0
            task_meta.finish_one()
            bm.mark("OK")

    def _loop_run(self):
        """ 循环从队获取URL进行处理, 多线程的情况下, 每个线程执行的方法 """
        # count = 0
        while True:
            """
            在一个死循环的作用域中, 变量不会马上回垃圾回收, 最好能封装一个方法形成局部作用域
            以便每次跳出循环都可以回收, 否则这个循环体内的方法内存会一直涨....无法GC
            因为Python可能认为, 在这个循环体中的变量都可能还会被使用, 只要这个作用域没有结束, 就不会立即回收
            """
            self._do_url_task_from_queue()

    def do_url(self, url_, deep, headers=None, task_meta=None, extra=None):
        """处理URL, 请求获取页面, 该方法可以在output中独立递归调用 """
        logger.info("GET PAGE[%s], deep[%s]", url_, deep)
        bg = BenchMark("getpage")
        tab = self.get_page(url_, headers=headers)  #: 这里可能抛出异常, 向上抛
        bg.mark("OK")

        if not tab.ok:
            # for 404
            logger.warning("[404], %s", url_)

        return tab

    def do_output(self, tab, url, deep, headers, task_meta, extra):
        #: 这里如果找不到content-type说明网络请求, 存在错误, 无返回等
        #: 定义个默认的错误内容头, 以便外部可以通过绑定error处理器, 统一通过特定output处理
        content_type = tab.headers.get('Content-Type', "error/unknown")

        bm = BenchMark("all-output")

        url_params = {  #: 这些参数可以在filter/output声明的时候用依赖注入方式注入, 只需要声明参数名称相同
            'tab': tab,
            'url': url,
            'deep': deep,
            'headers': headers,
            'task_meta': task_meta,
            'extra': extra
        }

        for output_handler_ in self._all_outputs:
            # 遍历所有的输出控制器, 如果符合控制器约束, 就执行控制器
            if output_handler_.match(content_type):
                dy_params = dynamic_params(output_handler_.real_func, url_params)
                output_handler_.invoke(**dy_params)

        try:
            tab._response.close()
        except Exception as e:
            # when 404
            pass
        bm.mark("OK")

    def __enter__(self):
        pass

    def __exit__(self, exc_type, exc_val, exc_tb):
        pass

    def add_filter(self, func, start_deep=1):
        """
        添加一个过滤器
        :param func:
        :param start_deep: 起作用的URL深度, 第一个URL为0
        :return:
        """
        if not callable(func):
            raise TypeError("Filter[{}] must be a function" % func)

        self._all_filters.append(Filter(func, start_deep=start_deep))
        return self

    def add_output(self, content_type, output):
        """
        添加一个输出控制器
        :param content_type:  正则表达式, 匹配的content-type类型
        :param output: 输出控制器方法
        :return:
        """
        if not callable(output):
            raise TypeError("Output[{}] must be a function" % output)
        self._all_outputs.append(OutputHandler(content_type, output))
        return self

    def _mutli_thread_run(self, num, wait=True):
        # 创建多线程执行, daemon使得后台进程在主线程结束后自动销毁
        # 这个方法可以被覆盖, 子类可以实现空转不停机. 具体看SpiderServer
        # Spider一开始是编程式的爬虫, 没有提供服务形式, 完整的编程功能是, 从main函数运行完直到结束
        # 服务形式的爬虫不停机运转. 队列不断接受请求.
        #
        self._threadPool = {}

        def wrap():
            try:
                self._loop_run()
            except queue.Empty as e:
                self.browser().quit()
            except Exception as e:
                logger.error("Thread[%s] run error %s " % (threading.currentThread().name, e))
                self._threadPool.pop(threading.currentThread().name)  #: 这个线程死掉了,
                self.browser().quit()
                spider_exception_listener.handle_exception(e)

        try:
            start_num = num - len(self._threadPool.keys())
            pending_threads = []
            for i in range(start_num):
                t = threading.Thread(target=wrap, args=(), daemon=False)
                self._threadPool[t.name] = t
                pending_threads.append(t)

            for t in pending_threads:
                logger.info("MuitlThreadRun[%s]" % t.name)
                t.start()

            if wait:
                # 如果存在等待, 等待子线程处理完成, 所有的子线程配合wait_timeout, 直到没有任务超时停止
                # 如果没有配置wait_timeout, 子线程就永远不会停止
                for t in pending_threads:
                    t.join()

            logger.info("=======================ALL DONE, COUNT[%s] =====================", self._url_count.value)

        except Exception as e:
            logger.exception(e)

    def run(self, num=1, wait=True):
        with self:
            self._mutli_thread_run(num, wait)
            # self._loop_run()


###########################################################
class Filter(object):
    """ 过滤器接口对象 """

    def __init__(self, func, start_deep=1):
        """

        :param func: 方法
        :param start_deep: 从哪个URL深度开启起作用, 一般第一个URL, deep=0
        """
        self.func = func
        self.start_deep = start_deep

    @property
    def real_func(self):
        return self.func

    def match(self, deep):
        return deep >= self.start_deep

    def invoke(self, *args, **kwargs):
        if callable(self.func):
            bx = BenchMark(self.func.__name__)
            try:
                return self.func(*args, **kwargs)
            except Exception as ex:
                spider_exception_listener.handle_exception(ex)
            finally:
                bx.mark("OK")
        return False

    def __call__(self, *args, **kwargs):
        #: 直接函数调用, 一般都在调试阶段, 有什么异常就抛出什么异常
        return self.func(*args, **kwargs)


###########################################################
class OutputHandler(object):
    """ 输出控制器 """

    def __init__(self, content_type, func):
        self.content_type = content_type
        self.re_content_type = re.compile(content_type)
        self.funcs = [func]

    @property
    def real_func(self):
        return self.funcs[0]

    def invoke(self, *args, **kwargs):
        b = BenchMark(self.real_func.__name__)
        try:
            #: 任何一个outputHandler抛出异常都会影响其他output handler执行, 直接抛异常, 否则很多问题无法察觉
            return self.real_func(*args, **kwargs)
        except Exception as ex:
            spider_exception_listener.handle_exception(ex)
        finally:
            b.mark("OK")

    def match(self, content_type):
        return self.re_content_type.search(content_type)

    def __call__(self, *args, **kwargs):
        #: 直接按照函数调用, 一般都在调试阶段, 有什么异常就抛出什么异常
        return self.real_func(*args, **kwargs)


###########################################################
class Tab(Browser, Response):
    """
    Tab是网页标签, 比较特殊的东西, 不知道取什么名字, 就叫tab(标签)类似浏览器标签
    有浏览器的特性(可以继续发起请求), 也有结果的特性(从页面获取值)
    """

    def __init__(self, browser, response):
        super(Response, self).__init__()
        super(Browser, self).__init__()
        self._browser = browser
        self._response = response
        self.local_store = browser.browser_config().local_store
        self.__dict__.update(response.__dict__)  #: 拷贝结果集的属性到tab
        self._dom = None

    def dom(self):
        # 解析结构化结构, DOM(方便CSS方式选择)
        # 这里会牺牲一定性能来保证API的简洁
        if self._dom is None and Regex.RE_TYPE_HTML.search(self.headers.get("Content-Type")):
            text = self.text or ""
            if "" == text.strip():
                text = "<html></html>"
            try:
                self._dom = dom(remove_xml_encoding(text))  # cssselect
            except ParserError as e:
                logger.error("DOMError, url[%s], msg[%s], content:[%s]", self.url, e, text)
                self._dom = dom("<html></html>")

        if self._dom is None:
            logger.warning("DOM NONE! %s %s", self.url, self.text)
            self._dom = dom("<html></html>")
        return self._dom

    @property
    def text(self):
        if hasattr(self, "headless"):
            return self._browser.text
        return self._response.text

    @property
    def title(self):
        if "html" in self.headers.get("content-type", ""):
            #: 只有当前访问页面是HTML的类型才尝试获取 title
            els = self.dom().cssselect('title')
            return els[0].text if els and len(els) > 0 else ""
        return ""

    def get_local_filename(self, url=None, dirname=""):
        """
        根据当前URL自动构造一个本地文件地址, 方便截图保存
        http://news.baidu.com/
        /data/hunter/news.baidu.com/-spider
        http://tieba.baidu.com/
        /data/hunter/tieba.baidu.com/-spider

        :param: url URL
        :param: dir 指定保存文件夹, 相对于local_store路径
        """
        urlObj = self.parse_url(url or self._response.url)
        path_ = urlObj.path.replace("/", "-")
        hostname = urlObj.netloc.replace(":", "-")  #: 可能包含localhost:83 不允许端口
        localfile = os.path.join(self.local_store, dirname, hostname, path_)
        localdir = os.path.dirname(localfile)
        if not os.path.exists(localdir):
            os.makedirs(localdir)

        if urlObj.path == "/" or urlObj.path == "":
            localfile = localfile + ".html"  # 有的只有域名, 没有后缀, 默认加一个后缀
        return localfile

    def save_from_url(self, url, dirname="", filename=None):
        """
        获取指定URL内容, 并按照URL名称保存到本地

        :param url: 当前URL, 可以是当前页面的相对路径, 自动转成绝对路径
        :param dirname: 指定一个文件夹目录
        :param filename: 指定文件名称, 注意!! 如果很多URL都用同一个名称, 结果可能只会保存到一份文件
        :return:
        """
        if filename:
            localfile = os.path.join(self.local_store, dir, filename)
        else:
            abs_url = get_real_url(self.url, url)  #: 转换URL为绝对URL
            localfile = self.get_local_filename(abs_url, dirname=dirname)
        r = self._browser.get(abs_url)
        with open(localfile, "wb") as file:
            file.write(r.content)
        return localfile

    def user_dir(self, path):
        return os.path.join(self.local_store, path)

    def scroll_by(self, x, y):
        self._browser.scroll_by(x, y)

    def execute_js(self, js_str):
        self._browser.execute_js(js_str)

    def get(self, url, **kwargs):
        self._browser.get(url, **kwargs)

    def window_size(self, width, height):
        self._browser.window_size(width, height)

    def close(self):
        self._browser.close()

    def screenshot_as_png(self, filename):
        self._browser.screenshot_as_png(filename)

    def quit(self):
        self._browser.quit()

    def wait(self, num):
        self._browser.wait(num)

    def __str__(self):
        return "<Tab[{}],[{}]>".format(self.url, self.status_code)
