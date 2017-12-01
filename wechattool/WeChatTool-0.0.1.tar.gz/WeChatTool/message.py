#!/usr/bin/evn python3
# encoding=utf-8

import requests
import json
import logging
from WeChatTool.connect import WeChatAuth
from WeChatTool.exception import *

__all__ = ["WeChatMsgSender"]

logging.basicConfig(level=logging.INFO, format='%(asctime)s [%(levelname)s] %(funcName)s: %(message)s')


class WeChatMsgSender:
    def __init__(self, corpid, corp_secret):
        self.sendmsg_url = 'https://qyapi.weixin.qq.com/cgi-bin/message/send?'
        self.auth = WeChatAuth(corpid, corp_secret)
        self.token_info = self.auth.get_token_info()

    def send_text_msg(self, **kwargs):
        users = kwargs.get('users', [])
        if not users:
            raise ParameterError()
        send_args = {
            "touser": '|'.join(user for user in users),
            "toparty": kwargs.get('toparty', None),
            "agentid": kwargs.get('agentid', None),
            "msgtype": "text",
            "text": {
                "content": kwargs.get('content')
            },
            "safe": 0
        }
        resp = requests.post('{0}access_token={1}'.format(self.sendmsg_url, self.token_info['token']),
                             data=json.dumps(send_args))
        if resp.json()['errcode'] != 0:
            raise Exception('send msg failed')
        logging.info('send msg to [{}] successed'.format(send_args["touser"]))
        return {'code': 0, 'msg': 'send message ok'}
