#! /usr/bin/env python
# coding: utf-8

import os
import ConfigParser
import hmac
import hashlib
import base64
import random
from urllib import quote
from datetime import datetime
import xml.dom.minidom
from JYAliYun import UTC_FORMAT, GMT_FORMAT, P_NAME, LONG_P_NAME

__author__ = 'ZhouHeng'

XMLNS = "http://www.gene.ac"


class ConvertObject(object):
    encoding = "utf-8"
    second_encoding = "gbk"

    @staticmethod
    def decode(s):
        if isinstance(s, str):
            try:
                return s.decode(ConvertObject.encoding)
            except UnicodeError:
                return s.decode(ConvertObject.second_encoding, "replace")
        if isinstance(s, (int, long)):
            return "%s" % s
        if isinstance(s, unicode):
            return s
        return unicode(s)

    @staticmethod
    def encode(s):
        if isinstance(s, unicode):
            return s.encode(ConvertObject.encoding)
        return s

    @staticmethod
    def dict_to_xml(tag_name, dict_data):
        tag_name = ConvertObject.decode(tag_name)
        doc = xml.dom.minidom.Document()
        root_node = doc.createElement(tag_name)
        root_node.setAttribute("xmlns", XMLNS)
        doc.appendChild(root_node)
        assert isinstance(dict_data, dict)
        for k, v in dict_data.items():
            key_node = doc.createElement(k)
            if isinstance(v, dict):
                for sub_k, sub_v in v.items():
                    sub_node = doc.createElement(sub_k)
                    sub_v = ConvertObject.decode(sub_v)
                    sub_node.appendChild(doc.createTextNode(sub_v))
                    key_node.appendChild(sub_node)
            else:
                v = ConvertObject.decode(v)
                key_node.appendChild(doc.createTextNode(v))
            root_node.appendChild(key_node)
        return doc.toxml("utf-8")


class ConfigManager(object):
    def __init__(self, **kwargs):
        self.section = kwargs.pop("section", None)
        if self.section is None:
            self.section = kwargs.pop("default_section", None)

        self.conf_path = kwargs.pop("conf_path", None)
        if self.conf_path is None:
            conf_dir = kwargs.pop("conf_dir", None)
            if isinstance(conf_dir, str) or isinstance(conf_dir, unicode):
                conf_name = kwargs.pop("conf_name", None)
                default_conf_name = kwargs.pop("default_conf_name", None)
                if conf_name is not None:
                    self.conf_path = os.path.join(conf_dir, conf_name)
                elif default_conf_name is not None:
                    self.conf_path = os.path.join(conf_dir, default_conf_name)
            else:
                if "product" in kwargs:
                    env_conf_path = get_environ("%s_conf_path" % kwargs["product"])
                else:
                    env_conf_path = get_environ("conf_path")
                self.conf_path = env_conf_path
        if self.conf_path is None or self.section is None:
            self.ready = False
        else:
            self.config = ConfigParser.ConfigParser()
            self.config.read(self.conf_path)
            self.ready = self.config.has_section(self.section)

    def _get(self, option, option_type=None, default=None):
        if self.ready is False:
            return default
        if self.config.has_option(self.section, option) is False:
            return default
        if option_type is None:
            self.config.get(self.section, option)
        if option_type == int:
            return self.config.getint(self.section, option)
        elif option_type == bool:
            return self.config.getboolean(self.section, option)
        elif option_type == float:
            return self.config.getfloat(self.section, option)
        return self.config.get(self.section, option)

    def get(self, option, default=None):
        return self._get(option, default=default)

    def getboolean(self, option, default=None):
        return self._get(option, bool, default=default)

    def getint(self, option, default):
        return self._get(option, int, default=default)

    def getfloat(self, option, default):
        return self._get(option, float, default=default)

    def has_option(self, option):
        if self.ready is False:
            return False
        return self.config.has_option(self.section, option)


def ali_headers(access_key_id, access_key_secret, request_method, content_md5, content_type, headers, resource,
                **kwargs):
    request_time = datetime.utcnow().strftime(GMT_FORMAT)
    x_headers = dict()
    product = kwargs.pop("product", "")
    x_headers_key = "x-%s" % product.lower()
    if isinstance(headers, dict):
        for k, v in dict(headers).items():
            if k.startswith(x_headers_key):
                x_headers[k] = v
    else:
        headers = dict()
    if content_type is not None and len(content_type) > 0:
        headers["Content-Type"] = content_type
    signature = ali_signature(access_key_secret, request_method, content_md5, content_type, request_time, x_headers,
                              resource, **kwargs)

    headers["Authorization"] = product.upper() + " %s:%s" % (access_key_id, signature)
    headers["Date"] = request_time
    return headers


def ali_signature(access_key_secret, request_method, content_md5, content_type, request_time, x_headers, resource,
                  **kwargs):
    if content_md5 is None:
        content_md5 = ""
    if content_type is None:
        content_type = ""
    x_headers_s = ""
    if x_headers is not None:
        if type(x_headers) == unicode:
            x_headers_s = x_headers
        elif type(x_headers) == dict:
            for key in sorted(x_headers.keys()):
                x_headers_s += key.lower() + ":" + x_headers[key] + "\n"
    msg = "%s\n%s\n%s\n%s\n%s%s" % (request_method, content_md5, content_type, request_time, x_headers_s, resource)
    if "print_sign_msg" in kwargs:
        print(msg)
    h = hmac.new(access_key_secret, msg, hashlib.sha1)
    signature = base64.b64encode(h.digest())
    return signature


def percent_encode(s):
    res = quote(s, '')
    res = res.replace("+", "%20")
    res = res.replace("*", "%2A")
    res = res.replace("%7E", "~")
    return res


def encode_param(params):
    param_str_list = []
    for item in sorted(params.keys()):
        s = percent_encode(item) + "=" + percent_encode(params[item])
        param_str_list.append(s)
    param_str = "&".join(param_str_list)
    return param_str


def _sign(http_method, params, access_secret):
    param_str = encode_param(params)
    string_sign = http_method + "&%2F&" + percent_encode(param_str)
    h = hmac.new(access_secret + "&", string_sign, hashlib.sha1)
    signature = base64.b64encode(h.digest())
    return signature


def get_params(access_key, access_secret, http_method, custom_params, **kwargs):
    sign_nonce = "%s" % random.randint(100000, 999999)
    time_stamp = datetime.utcnow().strftime(UTC_FORMAT)
    return_format = "JSON"
    version = kwargs.get("version", "2015-05-01")
    sign_method = kwargs.get("sign_method", "HMAC-SHA1")
    sign_version = kwargs.get("sign_version", "1.0")
    common_param = dict(Format=return_format, Version=version, AccessKeyId=access_key,
                        SignatureMethod=sign_method, SignatureVersion=sign_version,
                        SignatureNonce=sign_nonce, Timestamp=time_stamp)
    params = dict(custom_params)
    params.update(common_param)
    params["Signature"] = _sign(http_method, params, access_secret)
    return params


def get_environ(key):
    """
        ADD IN 0.1.14
    """
    key = unicode(key).upper()
    full_key = "%s_%s" % (P_NAME, key)
    v = os.environ.get(full_key)
    if v is not None:
        return v
    long_full_key = "%s_%s" % (LONG_P_NAME, key)
    lv = os.environ.get(long_full_key)
    if lv is not None:
        return lv
    return os.environ.get(key)

if __name__ == "__main__":
    config_man = ConfigManager(section="Account", product="MNS")
    print config_man.get("access_key_id")
