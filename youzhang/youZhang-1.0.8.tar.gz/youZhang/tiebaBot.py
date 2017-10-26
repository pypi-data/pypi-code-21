from config import *


def login_net():
    URL = "http://10.108.255.249/include/auth_action.php"

    data = {'username': username, 'password': password, 'action': 'login', 'ac_id': 1, 'user_ip': ip,
            'nas_ip': '', 'user_mac': '', 'save_me': 0, 'ajax': 1}
    baidu = requests.get("http://baidu.com")
    if 'http://10.108.255.249/' in baidu.text:
        print "yes no network"
        requests.post(URL, data)
    else:
        print baidu.text
    return 0


def ding_tie(tieID_barName_Dict):
    try:
        for key, value in tieID_barName_Dict.iteritems():
            res = reply(key, value, bduss[0])            
            if res == 0:
                print True
            else:
                print False
    except ValueError:
        login_net()
    return 0


if __name__ == '__main__':

    for item in range(times):
        ding_tie(tieID_barName_Dict)
        print '----%i st' % (item)
        time.sleep(interval)
