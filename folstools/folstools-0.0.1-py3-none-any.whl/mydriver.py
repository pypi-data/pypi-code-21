from selenium import webdriver
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC


class MyWebDriver(webdriver.Chrome):
    def __init__(self):
        super().__init__('./chromedriver')

    def by_xpath(self, xpath):
        return self.find_element_by_xpath(xpath)

    def by_id(self, _id):
        return self.find_element_by_id(_id)

    def by_name(self, name):
        return self.find_element_by_name(name)

    def wait(self, time, element_located):
        return (WebDriverWait(self, time).
                until(EC.presence_of_element_located(element_located)))
