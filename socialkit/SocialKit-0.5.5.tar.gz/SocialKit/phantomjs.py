from selenium.webdriver.common.proxy import *
from selenium import webdriver
from selenium.webdriver.common.desired_capabilities import DesiredCapabilities
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait
from selenium.common.exceptions import TimeoutException


from .log import show
from .agents import AGS
from random import choice
import sys, os
import socket


user_root = os.environ['HOME']
SocialKit_root = os.path.join(user_root, '.SocialKit')
SocialKit_cache_max_size = 1048576

if not  os.path.exists(SocialKit_root):
    os.mkdir(SocialKit_root)

cookies_path = os.path.join(SocialKit_root, 'cookie.txt')

storage_path = os.path.join(SocialKit_root, 'cache')
if not  os.path.exists(storage_path):
    os.mkdir(storage_path)

phantomjs_path = os.popen("which phantomjs").read().strip()
if not phantomjs_path:
    show("install phantomjs first!!")
    sys.exit(1)



def test_proxy(proxy):
    t,s,p = proxy.split(":")
    s = s[2:]
    p = int(p)
    try:
        socket.socket(socket.AF_INET, socket.SOCK_STREAM).connect((s,p))
    except Exception as e:
        show(e)
        return False
    return True

class ProxyNotConnectError(Exception):
    pass

class WebDriver:
    """
    @proxy:  
        format like:
            'socks5://127.0.0.1:1080'
            'http://127.0.0.1:1080'

    """
    def __init__(self, proxy=False, load_img=False, random_agent=False,agent=None,**options):
        if proxy:
            if not test_proxy(proxy):
                raise ProxyNotConnectError(proxy + " not connected")

        dcap = dict(DesiredCapabilities.PHANTOMJS)
        if random_agent:
            dcap["phantomjs.page.settings.userAgent"] = (choice(AGS))
        else:
            dcap["phantomjs.page.settings.userAgent"] = 'Opera/9.61 (Windows NT 5.1; U; zh-cn) Presto/2.1.1'
            if agent:
                dcap["phantomjs.page.settings.userAgent"] = agent

        # dcap['phantomjs.page.settings.resourceTimeout'] = '5000'
        load_image = 'true' if load_img else 'false' 
        timeout = options.get('timeout')

        web_service_args = [
            '--load-images=' + load_image,
        ]

        if proxy:
            proxy_t, proxy_c = proxy.split("//")
            proxy_t = proxy_t[:-1]
            show(proxy_c, proxy_t)
            web_service_args += [
                '--proxy=' + proxy_c,
                '--proxy-type=' + proxy_t,
                '--local-storage-path=' + storage_path,
                '--cookies-file=' + cookies_path,
                '--local-storage-quota=' + str(SocialKit_cache_max_size),
                '--ignore-ssl-errors=true', 
                '--ssl-protocol=any',
            ]

        self.phantom = webdriver.PhantomJS(phantomjs_path,service_args=web_service_args, desired_capabilities=dcap)
        self.phantom.set_window_size(2000, 1500)
        if timeout:
            self.phantom.set_page_load_timeout(int(timeout))

        self.dcap = dcap

    def type_msg(self, id, msg, by='id'):
        fun = getattr(self.phantom, "find_element_by_" + by)
        fun(id).clear()
        fun(id).send_keys(msg)

    def get(self, url, timeout=120, wait_for=None):

        if timeout:
            self.phantom.set_page_load_timeout(int(timeout))
        try:
            self.phantom.get(url)
            if wait_for:
                element_present = EC.presence_of_element_located((By.ID, wait_for))
                WebDriverWait(self.phantom, timeout).until(element_present)    
            
        except TimeoutException:
            # self.phantom.execute_script("windows.stop();")
            error='can not load site: ' + url
            show(error, c='red', log=True, k='error')


    @property
    def page(self):
        return self.phantom.page_source

    def __getitem__(self, k):
        return getattr(self.phantom, k)

    def __call__(self, func, *args, **karsg):
        return getattr(self.phantom, func)(*args, **karsg)

# window = driver.manage().window()
# 
# window.setSize((1024, 2048))
