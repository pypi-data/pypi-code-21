import os
import platform
import time
import requests
import urllib3
from .exceptions import EmbedException
from selenium import webdriver
from pyvirtualdisplay import Display
from selenium.common.exceptions import TimeoutException
from selenium.common.exceptions import NoSuchElementException

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


class Request:
    url = None

    def __init__(self, url):
        self.url = url

    def get_headers(self):
        try:
            return self.response(requests.head(self.url, allow_redirects=True, verify=False, timeout=30))
        except requests.exceptions.SSLError as e:
            raise EmbedException(495, str(e))
        except requests.exceptions.RequestException as e:
            raise EmbedException(400, str(e))

    def selenium(self):
        try:
            if self.is_headless_supported():
                chrome_options = webdriver.ChromeOptions()
                chrome_options.add_argument('--no-sandbox')
                display = Display(visible=0, size=(1024, 768))
                display.start()
                driver = webdriver.Chrome(
                    # service_log_path=os.path.join(BASE_DIR, '..', 'logs/ghostdriver.log'),
                    chrome_options=chrome_options
                )
            else:
                driver = webdriver.Chrome(executable_path='/usr/local/bin/chromedriver')

            driver.get(self.url)
            time.sleep(2)
            html_data = driver.execute_script("return document.documentElement.innerHTML;")
            url = driver.current_url
            driver.quit()

            if self.is_headless_supported():
                display.stop()

            return Response(url, 200 if html_data != '' else 204, {}, html_data)
        except TimeoutException as e:
            raise EmbedException(408, e.msg)
        except NoSuchElementException as e:
            raise EmbedException(400, e.msg)

    def request_advance(self):
        try:
            session = requests.Session()
            cookies = dict(cookies_are='working')
            response = session.get(
                self.url, allow_redirects=True, cookies=cookies, verify=False, timeout=30,
                headers={
                    'User-Agent': 'facebookexternalhit/1.1 (+http://www.facebook.com/externalhit_uatext.php)',
                    # 'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko)',
                    'Connection': 'keep-alive'
                }
            )

            if 'Set-Cookie' in response.headers and 'ckcheck' in response.headers['Set-Cookie']:
                response = session.get(self.url)

            if response.encoding == 'ISO-8859-1':
                response.encoding = response.apparent_encoding

            return self.response(response)
        except requests.exceptions.SSLError as e:
            raise EmbedException(495, str(e))
        except requests.exceptions.RequestException as e:
            raise EmbedException(400, str(e))

    def request_normal(self):
        return self.response(requests.get(self.url, headers={
            'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko)'
        }))

    @staticmethod
    def is_headless_supported():
        not_supported = ['darwin']
        return platform.system().lower() not in not_supported

    @staticmethod
    def response(response):
        return Response(
            response.url, response.status_code, response.headers, response.text, response.reason
        )


class Response(object):
    _allowed_types = [
        'text/html',
        'text/plain'
    ]
    url = None
    status_code = None
    headers = {}
    content = None
    message = None

    def __init__(self, url, code, headers, content, message=None):
        self.url = url
        self.status_code = code
        self.headers = headers
        self.content = content
        self.message = message

    def get_content_type(self):
        if 'content-type' in self.headers:
            return self.headers['content-type'].split(';')[0]

    def is_content_type_valid(self):
        if self.get_content_type() not in self._allowed_types:
            return False

        return True

    def __bool__(self):
        if self.status_code != 200:
            return False

        return True
