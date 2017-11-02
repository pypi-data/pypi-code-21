import requests
from bs4 import BeautifulSoup
from selenium import webdriver
from prettytable import PrettyTable
from progressbar import ProgressBar, Percentage, Bar
from selenium.webdriver.common.desired_capabilities import DesiredCapabilities

from uec.methods import Methods


class User(object):

    _login_url = 'https://campusweb.office.uec.ac.jp/campusweb/'

    def __init__(self, username, password):
        # login
        self.username = username
        self.password = password
        self._bar = ProgressBar(widgets=[Percentage(), Bar()], maxval=100).start()
        self._bar.update(10)

        self.get = Methods(self._login(), self._bar)

    def _login(self):
        self._bar.update(20)

        # desired capabilities
        desired_capabilities = DesiredCapabilities.CHROME

        # open url
        self._bar.update(30)
        driver = webdriver.PhantomJS(desired_capabilities=desired_capabilities)
        driver.get(self._login_url)

        # get username and password input box
        self._bar.update(40)
        username_box = driver.find_element_by_id('username')
        password_box = driver.find_element_by_id('password')

        # send username and password
        self._bar.update(50)
        username_box.send_keys(self.username)
        password_box.send_keys(self.password)

        # commit
        self._bar.update(60)
        driver.find_element_by_name('_eventId_proceed').click()

        return driver

    @staticmethod
    def get_canceled_lecture_list(flag):
        # no lecture urls
        url_0 = 'http://kyoumu.office.uec.ac.jp/kyuukou/kyuukou.html'
        url_1 = 'http://kyoumu.office.uec.ac.jp/kyuukou/kyuukou2.html'

        # get html
        response = None
        if flag == 0:
            response = requests.get(url_0)
        elif flag == 1:
            response = requests.get(url_1)
        response.encoding = response.apparent_encoding

        # get data
        soup = BeautifulSoup(response.text, 'lxml')
        tds = soup.find_all('td', {'align': 'CENTER'})

        # store data to array
        data = []
        for i in range(0, 5):
            data.append([])
            for j in range(i, len(tds), 5):
                data[i].append(tds[j].text)

        # create table and print
        table = PrettyTable()
        for i in range(1, 5):
            table.add_column(data[i][0], data[i][1:])
        print(table)
