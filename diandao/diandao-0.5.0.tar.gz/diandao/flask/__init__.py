# -*- coding: utf-8 -*-

from .globals import *
from flask import request, make_response
from sqlalchemy import event
from sqlalchemy.orm import mapper
from sqlalchemy.inspection import inspect
from diandao import isint_or, JSON
import base64
import random
import re
import time


def apply_app(app):
    stacker["app"] = app
    app.config.setdefault("CACHE_LIFE_TIME", 600)


class BaseInterface(object):
    """基础接口类"""
    # 绑定指定模型类, 可继承模型的类方法(@classmethod)
    __bindmodel__ = None

    def __getattr__(self, name):
        if self.__bindmodel__ is not None:
            return getattr(self.__bindmodel__, name, None)
        return None


class version_control:
    def __getattribute__(self, name):  # real signature unknown; restored from __doc__
        """ x.__getattribute__('name') <==> x.name """
        pass

    def __get__(self, obj, type=None):  # real signature unknown; restored from __doc__
        """ descr.__get__(obj[, type]) -> value """
        pass

    def __set__(self, obj, type=None):  # real signature unknown; restored from __doc__
        """ descr.__get__(obj[, type]) -> value """
        pass

    def __del__(self, obj, type=None):  # real signature unknown; restored from __doc__
        """ descr.__get__(obj[, type]) -> value """
        pass

    def __init__(self, function):  # real signature unknown; restored from __doc__
        pass

    __func__ = property(__get__, __set__, __del__)  # default


def version(ver):
    """版本号修饰"""
    return version_control

def operator_role():
    """请求头消息中获取操作者数据"""
    return  request.headers.get("Operator-Role", "")

def operator_id():
    """请求头消息中获取操作者数据"""
    return  request.headers.get("Operator-Id", 0)

def operator_name():
    """请求头消息中获取操作者数据"""
    return  request.headers.get("Operator-Name", 0)


def instant_defaults_listener(target, args, kwargs):
    """
    模型初始化时, 字段使用默认值
    """
    for key, column in inspect(target.__class__).columns.items():
        # if key in ["creatorid", "operatorid"]:
        #     # 请求头消息中获取操作者数据, 自动填入creatorid, operatorid字段
        #     operatorid = operator_id()
        #     if operatorid is not None:
        #         setattr(target, key, operatorid)
        #         continue
        # # operator role
        # if key in ["creator_role", "operator_role"]:
        #     # 请求头消息中获取操作者数据, 自动填入creatorid, operatorid字段
        #     role = operator_role()
        #     if operatorrole is not None:
        #         setattr(target, key, role)
        #         continue

        if column.default is not None:
            if callable(column.default.arg):
                setattr(target, key, column.default.arg(target))
            else:
                setattr(target, key, column.default.arg)

# 默认值初始化
event.listen(mapper, 'init', instant_defaults_listener)


def redirect(location, code=302, autocorrect=False):
    response = make_response()
    response.status_code = code
    response.autocorrect_location_header = autocorrect
    response.headers['Location'] = location
    return response


def response_json(data, **kwargs):
    """
    响应json数据
    :param data:
    :param kwargs:
    :return:
    """
    response = make_response()
    json = JSON.stringify(data, **kwargs)
    # ---------------
    # Cache-Control
    # ---------------
    # HTTP/1.1
    response.headers["Cache-Control"] = "no-cache, no-store, max-age=0, must-revalidate"
    # HTTP/1.0
    response.headers["Pragma"] = "no-cache"
    # Expires
    response.headers["Expires"] = time.strftime('%a, %d %b %Y %H:%M:%S GMT', time.gmtime())

    response.headers["Content-Type"] = "text/html; charset=utf-8"
    # jsvar 模式
    jsvar = request.args.get("jsvar", None)
    if jsvar:
        response.data = "<script>%s=%s</script>" % (jsvar, json)
        return response
    # script 标签回调
    scriptcallback = __strict_callback(request.args.get("scriptcallback", ""))
    if scriptcallback:
        response.data = "<script>%s(%s)</script>" % (scriptcallback, json)
        return response
    # jsonpcallback, 兼容参数callback
    jsonp = request.args.get("callback", "")
    jsonp = jsonp if jsonp else request.args.get("jsonpcallback", "")
    jsonp = __strict_callback(jsonp)
    if jsonp:
        response.headers["Content-Type"] = "application/javascript; charset=utf-8"
        response.data = "%s && %s(%s)" % (jsonp, jsonp, json)
    # 常规
    response.headers["Content-Type"] = "application/json; charset=utf-8"
    boundary = request.headers.get("Boundary-Wrap", "")
    if boundary.lower() == "no":
        boundary = ""
    if boundary.lower() == "passive":
        boundary == base64.b64encode("%s" % random.random())
    response.headers["Boundary"] = boundary
    response.data = "%s%s%s" % (boundary, json, boundary)
    return response


def __strict_callback(callback):
    pattern = re.compile("[^\w\._]")
    return callback if pattern.match(callback) else ""
