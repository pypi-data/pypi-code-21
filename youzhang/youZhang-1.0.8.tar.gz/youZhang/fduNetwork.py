import requests
import time
from config import *


def login_net():
    URL = "http://10.108.255.249/include/auth_action.php"

    data = {'username': username, 'password': password, 'action': 'login', 'ac_id': 1, 'user_ip': ip,
            'nas_ip': '', 'user_mac': '', 'save_me': 0, 'ajax': 1}
    baidu = requests.get("http://baidu.com")
    if 'http://10.108.255.249/' in baidu.text:
        print "yes no network"
        r = requests.post(URL, data)
        print (r.text)
    else:
        print baidu.text
    return 0


if __name__ == '__main__':
    while True:
        login_net()
        # sleep every 10 s
        time.sleep(10)
