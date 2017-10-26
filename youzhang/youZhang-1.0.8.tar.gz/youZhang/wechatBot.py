# coding=utf-8
import json
import os
import pycurl
import random
import re
import urllib2
import wave

import requests
from pydub import AudioSegment
from wxpy import *

KEY = ['29ccde937cd544afbd45667b4be9805e',
       '1feb7394fdc8404c95241fd927cbc21b',
       '407c1ce36b47446487672d57ac159ead',
       'd4f2b40188884b799cc35556737b43ae',
       'c43ac060a4ec4588809aa1fcc15cca82']
# KEY = '52075fb8edc7463ab304cf80a2b5ffe0'  # 图灵机器人key值,这里也可以是其他供应商机器人的key值,比如微软小冰.
GROUP_NAME = u'咻来了'
ADD_WELCOME = u'我自动接受了你的好友请求,点击邀请连接进群吧,关键词（大热门）（大跟班）（玩很大）（国光帮）（台综）（更新）'
ERROR_RESPONSE = u'机器故障，已收到: '
BOT_REPLY = u'机器人答复：'
bot = Bot()


def get_token():
    # 百度语音
    apiKey = "p05mO42EfykyqzQYgB9I3LQG"
    secretKey = "4575d1c08697fd17dff37662f6ed4e71"
    auth_url = "https://openapi.baidu.com/oauth/2.0/token?grant_type=client_credentials&client_id=" + apiKey + "&client_secret=" + secretKey
    res = urllib2.urlopen(auth_url)
    json_data = res.read()
    return json.loads(json_data)['access_token']


def dump_res(buf):
    buf = str(buf)
    pattern = re.compile(r'\["(.*?)"\]')
    global item
    item = re.findall(pattern, buf)


def speech2text(wav_path):
    token = get_token()
    fp = wave.open(wav_path, 'r')
    nf = fp.getnframes()
    f_len = nf * 2
    audio_data = fp.readframes(nf)
    cuid = "123456"  # my xiaomi phone MAC
    srv_url = 'http://vop.baidu.com/server_api' + '?cuid=' + cuid + '&token=' + token
    http_header = [
        'Content-Type: audio/pcm; rate=8000',
        'Content-Length: %d' % f_len
    ]

    c = pycurl.Curl()
    c.setopt(pycurl.URL, str(srv_url))  # curl doesn't support unicode
    c.setopt(c.HTTPHEADER, http_header)  # must be list, not dict
    c.setopt(c.POST, 1)
    c.setopt(c.CONNECTTIMEOUT, 30)
    c.setopt(c.TIMEOUT, 30)
    c.setopt(c.WRITEFUNCTION, dump_res)
    c.setopt(c.POSTFIELDS, audio_data)
    c.setopt(c.POSTFIELDSIZE, f_len)
    c.perform()
    return item[0].decode('utf-8')


def get_tuling(msg):
    # 构造了要发送给图灵服务器的数据
    apiUrl = 'http://www.tuling123.com/openapi/api'  # 图灵API
    key_item = random.randint(0, 4)
    data = {
        'key': KEY[key_item],
        'info': msg,
        'userid': '123456gbk',

    }
    # 字典出现异常的情况下会抛出异常,为了防止中断程序,这里使用了try-except异常模块
    try:
        r = requests.post(apiUrl, data=data).json()
        return r.get('text')
    except:
        return  # 将会返回一个None


def get_response(msg):
    dict_key_value = {
        'ggb': 'https://pan.baidu.com/s/1c142UVe',
        'drm': 'https://pan.baidu.com/s/1c2dELqS',
        'whd': 'https://pan.baidu.com/s/1qYLVC3y',
        'dgb': 'https://pan.baidu.com/s/1bEGvBC',
        u'抽奖': u'抽奖',
        u'大热门': 'http://mp.weixin.qq.com/mp/homepage?__biz=MzA3NzE5Nzg2OQ==&hid=13&sn=fbc5f275125ea022fad1ed818531171c#wechat_redirect',
        u'大跟班': 'http://mp.weixin.qq.com/mp/homepage?__biz=MzA3NzE5Nzg2OQ==&hid=14&sn=2e33a037fb8eefc90c1aa4c968403d15#wechat_redirect',
        u'小明星': 'http://mp.weixin.qq.com/mp/homepage?__biz=MzA3NzE5Nzg2OQ==&hid=14&sn=2e33a037fb8eefc90c1aa4c968403d15#wechat_redirect',
        u'玩很大': 'http://mp.weixin.qq.com/mp/homepage?__biz=MzA3NzE5Nzg2OQ==&hid=12&sn=08f00a7780e744eff4c550bb3b3b044b#wechat_redirect',
        u'国光帮': 'http://mp.weixin.qq.com/mp/homepage?__biz=MzA3NzE5Nzg2OQ==&hid=14&sn=2e33a037fb8eefc90c1aa4c968403d15#wechat_redirect',
        u'台综': 'http://mp.weixin.qq.com/mp/homepage?__biz=MzA3NzE5Nzg2OQ==&hid=8&sn=ea810e9cdbf79449169bda274d56fcab#wechat_redirect',
        u'公众号': 'https://mp.weixin.qq.com/mp/profile_ext?action=home&__biz=MzA3NzE5Nzg2OQ==#wechat_redirect',
        u'更新': 'http://mp.weixin.qq.com/mp/homepage?__biz=MzA3NzE5Nzg2OQ==&hid=9&sn=dbdc744f19da46dd31bea1978dc604b3#wechat_redirect',
        u'全集': 'http://mp.weixin.qq.com/mp/homepage?__biz=MzA3NzE5Nzg2OQ==&hid=8&sn=ea810e9cdbf79449169bda274d56fcab#wechat_redirect', }
    for key, value in dict_key_value.iteritems():
        if key in msg:
            response = value
            break
        else:
            response = get_tuling(msg)
    if response == u'抽奖':
        response = str(random.randint(1, 100))

    return response


@bot.register()
def print_others(msg):
    msg.sender.mark_as_read()
    group = bot.search(GROUP_NAME)[0]
    flag_switch = msg.type
    print msg
    if flag_switch == 'Friends':
        new_friend = msg.card.accept()
        new_friend.send(ADD_WELCOME)
        group.add_members(new_friend, True)
    elif flag_switch == 'Text':
        user_text = msg.text
        reply = get_response(user_text)
        if reply == None:
            reply = ERROR_RESPONSE + user_text
        if msg.is_at:
            group.send(BOT_REPLY + reply + '@' + msg.member.name)
    #     elif msg.sender.name == GROUP_NAME:
    #         msg.sender.send(BOT_REPLY + reply)
    #     else:
    #         msg.sender.send(BOT_REPLY + reply)
    # elif flag_switch == 'Recording':
    #     recordingFile = msg.file_name
    #     msg.get_file(recordingFile)
    #     msg.sender.send_file(recordingFile)
    #     audio = AudioSegment.from_mp3(recordingFile)
    #     os.remove(recordingFile)
    #     audio.export(recordingFile[:-3] + 'wav', 'wav')
    #     recordingFile = recordingFile[:-3] + 'wav'
    #     textS = speech2text(recordingFile)
    #     os.remove(recordingFile)
    #     responseS = get_response(textS)
    #     msg.sender.send('say:' + textS + BOT_REPLY + responseS)


embed()
