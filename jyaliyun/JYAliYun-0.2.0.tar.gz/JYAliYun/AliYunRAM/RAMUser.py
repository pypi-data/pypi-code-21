#! /usr/bin/env python
# coding: utf-8

from JYAliYun.AliYunObject import ObjectManager
from JYAliYun.Tools import jy_requests
from JYAliYun.Tools import get_params

__author__ = 'meisanggou'


class RAMUserManager(ObjectManager):
    PRODUCT = "RAM"
    address = "https://ram.aliyuncs.com"

    def list_users(self):
        action = "ListUsers"
        http_method = "GET"
        custom_params = dict(Action=action)
        params = get_params(self.access_key_id, self.access_key_secret, http_method, custom_params)
        resp = jy_requests.request(http_method, self.address, params=params)
        return resp

    def get_user(self, user_name):
        action = "GetUser"
        http_method = "GET"
        custom_params = dict(Action=action, UserName=user_name)
        params = get_params(self.access_key_id, self.access_key_secret, http_method, custom_params)
        resp = jy_requests.request(http_method, self.address, params=params)
        return resp

    def create_user(self, user_name, **kwargs):
        action = "CreateUser"
        http_method = "GET"
        custom_params = dict(Action=action, UserName=user_name)
        allow_keys = {"display_name": "DisplayName", "mobile_phone": "MobilePhone", "email": "Email",
                      "comments": "Comments"}
        for key in allow_keys.keys():
            if key in kwargs:
                custom_params[allow_keys[key]] = kwargs[key]
        params = get_params(self.access_key_id, self.access_key_secret, http_method, custom_params)
        resp = jy_requests.request(http_method, self.address, params=params)
        return resp

    def delete_user(self, user_name):
        action = "DeleteUser"
        http_method = "GET"
        custom_params = dict(Action=action, UserName=user_name)
        params = get_params(self.access_key_id, self.access_key_secret, http_method, custom_params)
        resp = jy_requests.request(http_method, self.address, params=params)
        return resp
