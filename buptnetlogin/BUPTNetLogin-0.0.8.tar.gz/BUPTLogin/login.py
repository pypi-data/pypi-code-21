# !/usr/bin/env python3
# -*- coding: utf-8 -*-

import os
import signal
import sys
from urllib import request, parse
from configparser import ConfigParser
from bs4 import BeautifulSoup

__author__ = 'ingbyr'
__email__ = 'admin@ingbyr.com'


class BUPTLogin:
    def __init__(self):
        self.url = 'http://10.3.8.211'
        self.clf_path = os.path.join(os.path.expanduser('~'), 'bnl.ini')
        self.cfg = ConfigParser()
        self.load_config()

    # load the config file
    def load_config(self):
        if not os.path.exists(self.clf_path):
            with open(self.clf_path, 'w') as f:
                f.write('[tool]\nsave_user = False\n\n[user]\naccount =\npassword =\n\n')
        self.cfg.read(self.clf_path)

        if len(sys.argv) == 3:
            self.set_user(sys.argv[1], sys.argv[2])
            print('>>> start login account: {}'.format(sys.argv[1]))
            self.start_login()
        elif len(sys.argv) > 1:
            raise SystemExit('Usage: bnl or bnl [username] [password]')

        self.is_save = self.cfg.getboolean('tool', 'save_user')
        if self.is_save:
            self.set_user(self.cfg.get('user', 'account'),
                          self.cfg.get('user', 'password'))
        else:
            self.login_failed()

    # set the account and password
    def set_user(self, account, password):
        self.account = account
        self.password = password

    # login to BUPT network
    def start_login(self):
        postData = parse.urlencode([
            ('DDDDD', self.account),
            ('upass', self.password),
            ('savePWD', 0),
            ('0MKKey', '')
        ])
        # send request
        req = request.Request(self.url)
        req.add_header('User-Agent',
                       'Mozilla/6.0 (iPhone; CPU iPhone OS 8_0 like Mac OS X) AppleWebKit/536.26 (KHTML, like Gecko) Version/8.0 Mobile/10A5376e Safari/8536.25')
        with request.urlopen(req, data=postData.encode('utf-8')) as f:
            self.show_result(f.read())

    # parse the response html
    def show_result(self, htmlDoc):
        soup = BeautifulSoup(htmlDoc, 'lxml')
        if soup.title.string == u'信息返回窗':
            print('>>> Login failed, please input account and password again!')
            self.login_failed()
            self.start_login()
        if soup.title.string == u'登录成功窗':
            # when login successfully, save the user
            print('>>> Login successfully')
            self.save_user(self.account, self.password)
            self.show_use_data()

    # when login failed
    def login_failed(self):
        account = input('>>> Account: ')
        password = input('>>> Password: ')
        self.set_user(account, password)

    # reopen the website to get information
    def show_use_data(self):
        req = request.Request(self.url)
        with request.urlopen(req) as f:
            html_doc = f.read()
        stat_page = BeautifulSoup(html_doc, 'lxml')
        stat = stat_page.head.script.string.encode('gb18030')
        fee = int(stat[55:65])
        flow = int(stat[30:40])
        flow0 = flow % 1024
        flow1 = flow - flow0
        flow0 = flow0 * 1000
        flow0 = flow0 - flow0 % 1024
        fee1 = fee - fee % 100
        flow3 = '.'
        print('>>> Used internet traffic : {0}{1}{2} MByte'.format(int(flow1 / 1024), flow3, int(flow0 / 1024)))
        print('>>> Balance : {} RMB'.format(fee1 / 10000))
        print('Have a nice day! by ingbyr')
        raise SystemExit()

    # when login successfully save the user auto
    def save_user(self, account, password):
        self.cfg.set('user', 'account', account)
        self.cfg.set('user', 'password', password)
        self.cfg.set('tool', 'save_user', 'True')
        self.cfg.write(open(self.clf_path, 'r+'))


# handle ctrl+c
def sigint_handler(signum, frame):
    print('\nHave a nice day! by ingbyr')
    sys.exit(1)


# func entrance
def do_login():
    signal.signal(signal.SIGINT, sigint_handler)
    m_login = BUPTLogin()
    m_login.start_login()


if __name__ == '__main__':
    do_login()
