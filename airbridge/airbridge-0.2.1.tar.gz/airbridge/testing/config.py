# -*- coding: utf-8 -*-
import os
from airbridge import get_engine_configs
from sqlalchemy import create_engine
from sqlalchemy.sql import text


engine_configs = get_engine_configs()

DEVICE_OS_BROWSER_UA = {
    'mobile__android__fb_cralwer': 'Mozilla/5.0 (Windows NT 6.1) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/49.0.2623.87 Safari/537.36; facebookexternalhit/1.1;',
    'mobile__android__default_browser': 'Mozilla/5.0 (Linux; U; Android 4.0; en-us; GT-I9300 Build/IMM76D) AppleWebKit/534.30 (KHTML, like Gecko) Version/4.0 Mobile Safari/534.30',
    'mobile__android__chrome': 'Mozilla/5.0 (Linux; Android 5.0; SM-G900P Build/LRX21T) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/48.0.2564.23 Mobile Safari/537.36',
    'mobile__ios__safari': 'Mozilla/5.0 (iPhone; CPU iPhone OS 9_1 like Mac OS X) AppleWebKit/601.1.46 (KHTML, like Gecko) Version/9.0 Mobile/13B143 Safari/601.1',
    'desktop__window__chrome': 'Mozilla/5.0 (Windows NT 6.1) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/49.0.2623.87 Safari/537.36',
    'tablet__ios__safari': 'Mozilla/5.0 (iPad; CPU iPhone OS 9_1 like Mac OS X) AppleWebKit/601.1.46 (KHTML, like Gecko) Version/9.0 Mobile/13B143 Safari/601.1',
}


class BaseConfig():

    def __init__(self):
        # Engines
        READ_DB = 'mysql://{}:{}@{}/udl?charset=utf8mb4'.format(engine_configs['read_db_host'],
                                                                engine_configs['read_db_pw'],
                                                                engine_configs['read_db'],)

        MAIN_DB = 'mysql://{}:{}@{}/udl?charset=utf8mb4'.format(engine_configs['main_db_host'],
                                                                engine_configs['main_db_pw'],
                                                                engine_configs['main_db'],)

        LOG_DB = 'mysql://{}:{}@{}/udl?charset=utf8mb4'.format(engine_configs['log_db_host'],
                                                               engine_configs['log_db_pw'],
                                                               engine_configs['log_db'],)
        self.engine = create_engine(MAIN_DB, convert_unicode=True)
        self.read_engine = create_engine(READ_DB, convert_unicode=True)
        self.log_engine = create_engine(LOG_DB, convert_unicode=True)

        # Hosts
        self.host = engine_configs['dev_abrge']
        self.short_host = engine_configs['dev_abrge']
        self.core_host = engine_configs['dev_core_airbridge']
        self.sdk_host = engine_configs['dev_sdk_airbridge']
        self.test_host = engine_configs['dev_test_airbridge']
        self.ads_host = engine_configs['dev_ads_airbridge']

        # Testing variables 
        self.headers = {'Authorization': engine_configs['jwt_token'], 'Content-Type': 'application/json'}

    def change_localhost_port(self, port):
        self.host = self.host.replace('5000', str(port))
        self.core_host = self.core_host.replace('5000', str(port))

    def set_to_android_default_browser(self):
        self.headers.update({'user-agent': DEVICE_OS_BROWSER_UA['mobile__android__default_browser']})

    def set_to_android_chrome(self):
        self.headers.update({'user-agent': DEVICE_OS_BROWSER_UA['mobile__android__chrome']})

    def set_to_ios_device(self):
        self.headers.update({'user-agent': DEVICE_OS_BROWSER_UA['mobile__ios__safari']})

    def set_to_desktop_device(self):
        self.headers.update({'user-agent': DEVICE_OS_BROWSER_UA['desktop__window__chrome']})

    def set_to_ipad_device(self):
        self.headers.update({'user-agent': DEVICE_OS_BROWSER_UA['tablet__ios__safari']})
