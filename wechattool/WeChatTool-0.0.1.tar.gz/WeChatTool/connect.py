#!/usr/bin/evn python3
# encoding=utf-8

import os
import requests
import pickle
import logging
from datetime import datetime
from WeChatTool.exception import *

__all__ = ["WeChatAuth"]

logging.basicConfig(level=logging.INFO, format='%(asctime)s [%(levelname)s] %(funcName)s: %(message)s')


class WeChatAuth:
    def __init__(self, corpid, corp_secret):
        self.gettoken_url = 'https://qyapi.weixin.qq.com/cgi-bin/gettoken'
        self.corpid = corpid
        self.corpsecret = corp_secret
        self.gettoken_args = {
            'corpid': self.corpid,
            'corpsecret': self.corpsecret,
            'token_file': '/tmp/.{}.pick'.format(self.corpid)
        }

    def get_token_info(self):
        timestamp = int(datetime.timestamp(datetime.now()))
        if os.path.exists(self.gettoken_args['token_file']):
            with open(self.gettoken_args['token_file'], 'rb') as fb:
                token_info = pickle.load(fb, errors='ignore')
                logging.debug(token_info)
                pre_timestamp = int(token_info['timestamp'])
                expires_in = int(token_info.get('expires_in', 0))
                token = token_info['token']
                if timestamp - pre_timestamp < expires_in and len(token) >= 200:
                    logging.info('get token from cache file')
                    return token_info
        resp = requests.get(self.gettoken_url, params=self.gettoken_args, timeout=5)
        status_code = resp.status_code
        if status_code == 200:
            token = resp.json()['access_token']
            token_info = {
                'timestamp': timestamp,
                'token': token,
                'expires_in': resp.json()['expires_in']
            }
            with open(self.gettoken_args['token_file'], 'wb') as fb:
                logging.info('write token to cache file')
                pickle.dump(token_info, fb)
            logging.info('get token from server')
            return token_info
        logging.info('get token faild from server')
        raise CacheTokenError()
