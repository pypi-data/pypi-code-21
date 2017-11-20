from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions
from selenium.webdriver.support.ui import WebDriverWait

from cobweb.adapters.http import HttpAdapter


class DynamicHttpAdapter(HttpAdapter):

    PhantomJSDriver = webdriver.PhantomJS
    ChromeDriver = webdriver.Chrome
    FirefoxDriver = webdriver.Firefox
    SafariDriver = webdriver.Safari

    def __init__(self, webdriver=PhantomJSDriver, sample_id="root", **kwargs):
        super(DynamicHttpAdapter, self).__init__(**kwargs)

        self.sample_id = sample_id
        self.driver = webdriver

    def __enter__(self):
        self.driver()

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.driver.close()

    def invoke(self, url):
        return self.send(url)

    def send(self, url):
        url = self.prepare_request(url)
        self.driver().get(url)
        wait = WebDriverWait(self.driver, 10)
        wait.until(expected_conditions.visibility_of_element_located((By.TAG_NAME, "body")))
        return self.process_response(self.driver)

    def prepare_request(self, url: str):
        return url

    def process_response(self, response):
        data = BeautifulSoup(response.page_source, "html.parser")
        cookies = response.get_cookies()
        return {"data": data, "cookies": cookies}
