import multiprocessing
import threading
from twocaptcha import TwoCaptcha
from taskrunner import TaskRunner
from captchamanager.token import CaptchaToken

class CaptchaManager(object):
    def __init__(self, twocaptcha_api_key, site_key, page_url):
        self.two_captcha = TwoCaptcha(twocaptcha_api_key)
        self.site_key = site_key
        self.page_url = page_url
        self.captcha_queue = multiprocessing.Queue()

    def get_captcha_token(self):
        return self.two_captcha.solve_captcha(self.site_key, self.page_url)

    def __fill_captcha_queue(self):
        task_runner = TaskRunner()
        while True:
            token_value = task_runner.run_until_complete(target=self.get_captcha_token)
            self.captcha_queue.put(CaptchaToken(token_value))

    def start_captcha_queue(self, threads=1):
        for _ in range(threads):
            threading.Thread(target=self.__fill_captcha_queue).start()

    def wait_for_captcha_token(self):
        captcha_token = None
        while not captcha_token:
            token = self.captcha_queue.get()
            if token.is_valid():
                captcha_token = token.value
        return captcha_token
