# -*- coding: utf-8 -*-
# Exceptions

from umfpayservice import util

class UmfPayError(Exception):
    '''
    umfpayservice错误基类
    '''
    def __init__(self, message=None, http_body=None, http_status=None,
                 resp=None):
        util.logger.error(message)
        super(UmfPayError, self).__init__(message)

        self.http_body = http_body

        self.http_status = http_status
        self.resp = resp

class ParamsError(UmfPayError):
    '''
    参数错误：
    缺少参数、
    参数校验不通过等
    '''
    def __init__(self, message=None, params=None, http_body=None, http_status=None,
                 resp=None):
        super(ParamsError, self).__init__(message, http_body, http_status, resp)

        self.params = params

class SignatureError(UmfPayError):
    '''
    签名错误
    '''
    pass


class APIError(UmfPayError):
    '''
    接口错误：
    访问接口返回异常等
    '''
    pass

class RequestError(UmfPayError):
    '''
    请求错误
    python的请求框架报的错误
    '''
    pass

class ConfigError(UmfPayError):
    '''
    配置错误
    '''
    def __init__(self, message=None, config_key=None, config_value=None):
        super(ConfigError, self).__init__(message)

        self.config_key = config_key
        self.config_value = config_value