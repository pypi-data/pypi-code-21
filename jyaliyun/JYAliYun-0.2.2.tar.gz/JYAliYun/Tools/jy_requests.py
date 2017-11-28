#! /usr/bin/env python
# coding: utf-8

import requests

__author__ = 'meisanggou'


class JYResponse(object):
    def __init__(self):
        self.status_code = 0
        self.text = ""
        self.headers = dict()
        self.error = ""
        self.data = None

    def update(self, resp):
        if resp.headers.get("Content-Type", "").find("application/json") >= 0:
            self.data = resp.json()
        self.status_code = resp.status_code
        self.text = resp.text
        self.headers = resp.headers


def request(method, url, **kwargs):
    no_exception = kwargs.pop("no_exception", False)
    if "timeout" not in kwargs:
        kwargs["timeout"] = 5
    r_d = JYResponse()
    if no_exception is True:
        try:
            resp = requests.request(method, url, **kwargs)
            r_d.update(resp)
            return r_d
        except requests.RequestException as e:
            r_d.error = e
            r_d.status_code = -1
            return r_d
    resp = requests.request(method, url, **kwargs)
    r_d.update(resp)
    return r_d


def head(url, **kwargs):
    return request("HEAD", url, **kwargs)


def get(url, params=None, **kwargs):
    return request("GET", url, params=params, **kwargs)


def post(url, data=None, json=None, **kwargs):
    return request("POST", url, data=data, json=json, **kwargs)


def put(url, data=None, **kwargs):
    return request("PUT", url, data=data, **kwargs)


def delete(url, **kwargs):
    return request("DELETE", url, **kwargs)
