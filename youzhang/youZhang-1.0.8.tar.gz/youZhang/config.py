# coding=utf-8
import json
import math
import re
import sys
import time

import requests

reload(sys)
sys.setdefaultencoding('utf-8')
username = '12210240076'  # TODO change to yourself NO.
password = '130629'  # TODO change to yourself password.
ip = '10.141.251.16'  # TODO change to yourself ip address.
reply_text = 'hello'  # time.strftime('hour:%H-min:%M-sec:%S', time.localtime(time.time()))
SLEEP_TIME = 2*60  # s
interval = 4 * 60 * 60
times = 365 * 24 * 60 * 60 / interval
DRM, WHD = 30, 40
bar_dict = {'综艺大热门': DRM, '综艺玩很大': WHD}
tieID_barName_Dict = {5389464515: '国光帮帮忙',
                      5389454513: '综艺玩很大',
                      5389446284: '综艺大热门',
                      5389469177: '小明星大跟班',
                      5331475303: '综艺大热门',
                      5331459840: '综艺玩很大',
                      5329873471: '国光帮帮忙',
                      5344363983: '小明星大跟班',
                      }

bduss = [
    'UlQeERXOU5RQVpFYXNudXZYOFM4MW5hb21ia21BcmlKazY1MVpWZ2l1VlRHUmhhSVFBQUFBJCQAAAAAAAAAAAEAAABM80ucaWxvb2duAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAFOM8FlTjPBZV'
]


def str2dic(text):
    idic = {}
    ilist = text.split('&')
    for item in ilist:
        name, value = item.split('=', 1)
        idic[name] = value
    return idic


def reply(tid, bar,
          cookieBDUSS=''):
    if bar == '综艺大热门':
        fid = '4523035'
    elif bar == '综艺玩很大':
        fid = '13708832'
    elif bar == '吴宗宪':
        fid = '29577'
    elif bar == '国光帮帮忙':
        fid = '887007'
    elif bar == '小明星大跟班':
        fid = '22222029'
    elif bar == '天才冲冲冲':
        fid = '1443996'

    huitie_data_text = 'ie=utf-8&kw=' + bar + '&fid=' + fid + '&tid=4811894587&vcode_md5=&floor_num=1&rich_text=1&tbs=1234567&content=12345&files=[]&mouse_pwd=104,105,105,119,104,108,99,107,82,106,119,107,119,106,119,107,119,106,119,107,119,106,119,107,119,106,119,107,82,98,110,111,98,82,106,104,109,109,119,108,109,99,14764590727910&mouse_pwd_t=1476459072791&mouse_pwd_isclick=0&__type__=reply'
    huitie_data = str2dic(huitie_data_text)
    huitie_data['content'] = reply_text
    huitie_data['tid'] = tid

    c_cookies = {
        'BDUSS': cookieBDUSS}
    # 增加自动获取tbs,tbs必须带cookies获取,并且一段时间后会失效
    url = 'http://tieba.baidu.com/dc/common/tbs'
    r_tbs = requests.get(url, cookies=c_cookies)
    r_tbs = json.loads(r_tbs.text)
    huitie_data['tbs'] = r_tbs["tbs"]
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/49.0.2623.112 Safari/537.36',
        'Referer': 'http://tieba.baidu.com/p/5328239597'}

    huitie_data['mouse_pwd_t'] = str(math.floor(time.time() * 1000))
    huitie_data[
        'mouse_pwd'] = '2,2,12,24,5,3,2,4,61,5,24,4,24,5,24,4,24,5,24,4,24,5,24,4,24,5,24,4,61,5,13,0,12,12,4,61,5,13,6,4,24,5,4,12,4,' + \
                       huitie_data['mouse_pwd_t'] + '0'

    res = requests.post('http://tieba.baidu.com/f/commit/post/add', data=huitie_data, headers=headers,
                        cookies=c_cookies)
    pattern_check = re.compile('"no":(.*?),')
    check_num = int(re.findall(pattern_check, res.text)[0])
    time.sleep(SLEEP_TIME)
    return check_num
