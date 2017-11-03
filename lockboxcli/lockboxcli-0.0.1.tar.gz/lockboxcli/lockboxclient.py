#!/usr/bin/env python

from future.standard_library import install_aliases
install_aliases()


import json
import jwt # pip install PyJWT
import requests
import time
import os
import re
import urllib3
from urllib3._collections import HTTPHeaderDict



use_environment_variables = None

try:
    from django.conf import settings
except ImportError:
    use_environment_variables = True


class LockboxClient:
    x_initialization_vector = None
    x_api_key = None
    x_decryption_key = None
    lockbox_host = None
    key = None
    secret = None
    new_secret = None
    template = None
    generated_config = None
    environment = None
    base_url = None
    headers = None

    def __init__(self, environment):
        self.x_initialization_vector = os.environ['X_INITIALIZATION_VECTOR']
        self.x_api_key = os.environ['X_API_KEY']
        self.x_decryption_key = os.environ['X_DECRYPTION_KEY']
        self.lockbox_host = os.environ['LOCKBOX_HOST']
        self.template = os.environ['SMP_SETUP_DIR'] + '/../../../etc/master_template.conf-debug'
        self.generated_config = os.environ['SMP_SETUP_DIR'] + '/generated-from-lockbox-master.conf-debug'
        self.base_url = "https://" + self.lockbox_host + "/" + environment
        self.add_url = "https://" + self.lockbox_host + "/add/" + environment
        self.delete_url = "https://" + self.lockbox_host + "/delete/" + environment
        self.set_headers()


    def show_config(self):
        print('--- lockbox config ---')
        print(self.x_initialization_vector)
        print(self.x_api_key)
        print(self.x_decryption_key)
        print(self.lockbox_host)
        print(self.template)
        print(self.generated_config)
        print(self.base_url)
        print('--- lockbox config ---')

    def set_headers(self):
        self.headers = {
            "Content-Type": "application/json; charset=utf-8",
            "x-initialization-vector": self.x_initialization_vector,
            "x-api-key": self.x_api_key,
            "x-decryption-key": self.x_decryption_key,
            "Accept": "application/json"
        }

    # r = requests.post(self.base_url, auth=('userid', 'password'),
    def generate_config(self):
        with open(self.template,'rb') as payload:
            r = requests.post(self.base_url, data=payload, verify=False, headers=self.headers)
        return r

    def get_keys(self):
        key_list = []
        with open(self.template) as input_file:
            for i, line in enumerate(input_file):
                m = re.search('\${.*}', line)
                try:
                    key_list.append(m.group(0).replace('$','').replace('{','').replace('}',''))
                except:
                    foo = None
        return key_list

    def get_secret(self, key):
        # is it in key_list?
        key_list = self.get_keys()
        if key in key_list:
            # print("key found!")
            r = requests.get(self.base_url + '/' + key, verify=False, headers=self.headers)
            return r.text
        return None

    def update_secret(self, key, secret):
        old_secret = str(self.get_secret(key))
        payload = "{\"secret\":\"" + old_secret + "\"}"
        # delete old secret
        r = requests.post(self.delete_url + '/' + key, data=payload, verify=False, headers=self.headers)
        # update key with new secret
        payload = "{\"secret\":\"" + secret + "\"}"
        r = requests.post(self.add_url + '/' + key, data=payload, verify=False, headers=self.headers)
        return r.text

