# coding=utf-8
import time
from Tkinter import *

import requests


def networkGUI():
    def login():
        username = link_contend.get()
        password = pass_contend.get()
        data = {'username': username, 'password': '{TEXT}' + password, 'n': 100, 'type': 1, 'drop': 0}
        baidu = requests.get("http://baidu.com")
        # print baidu.text
        if 'http://10.108.255.249/' in baidu.text:
            print "yes no network"
            r = requests.post("http://10.108.255.249/cgi-bin/do_login", data=data)
            print(r.text)
            print 'ok'
        return 0

    def dead_loop():

        login()
        while True:
            secs = time.time()
            now = time.strftime("%M", time.localtime(secs))
            print time.strftime("%y-%m-%d::%H:%M", time.localtime(secs))

            if 30 < int(now) < 40:
                print 'try to login'
                login()
                time.sleep(600)
            else:
                time.sleep(600)

    root = Tk()
    root.title('复旦校园网自动认证检测小助手')

    labe_txt = Label(root, text='用户名：')
    labe_txt.grid(row=0, column=0)
    entry_link = Entry(root, width=20)
    entry_link.grid(row=0, column=1, columnspan=2)
    link_contend = StringVar()
    entry_link.config(textvariable=link_contend)
    link_contend.set('12210240076')

    labe_txt = Label(root, text='密 码：')
    labe_txt.grid(row=1, column=0)
    entry_link = Entry(root, width=20)
    entry_link.grid(row=1, column=1, columnspan=2)
    pass_contend = StringVar()
    entry_link.config(textvariable=pass_contend)
    pass_contend.set('130629')

    start_button = Button(root, text='网络监测', command=dead_loop, width=30)
    start_button.grid(row=2, column=0, columnspan=3)

    info_entry = Text(root, width=20, height=3, )
    info_entry.grid(row=3, column=0, columnspan=3, rowspan=3)
    info_entry.tag_config('a', foreground='green')
    info_entry.config(font='helvetica 18')
    info_entry.insert(1.0,
                      '输入用户名和密码后点击网络检测，\n就会开始死循环，\n当网络掉线就会尝试自动登录By © mirlab\n',
                      'a')

    mainloop()
    return 0


if __name__ == '__main__':
    networkGUI()
