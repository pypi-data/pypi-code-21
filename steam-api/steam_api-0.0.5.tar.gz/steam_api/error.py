# -*- coding: utf-8 -*-
# @Author  : vincent
# @File    : error.py
# @DATE    : 2017-11-07


# Base Exception
class APIException(Exception):
    """
        Base exception class , all exception inherit from it
    """
    # TODO: Logging  exceptions
    pass


# Request Parameter Problem
class ValidationError(APIException):
    """
    Base Validation exception class, all validation error inherit from it
    """
    pass


class ParameterRequiredError(ValidationError):
    """
    Missing required parameter exception
    """
    pass


class ParameterNotInEnumError(ValidationError):
    """
    Parameter only accept registered Enum
    """
    pass


# Request Problem
class SteamAPIFailure(APIException):
    """
        An API failure signifies a problem with your request 
    """
    pass


class SteamAPIFailureBadCall(SteamAPIFailure):
    pass


class SteamAPIFailureRequestLimit(SteamAPIFailure):
    pass


class SteamAPIFailureWrongMethod(SteamAPIFailure):
    pass


class SteamAPIFailureForbidden(SteamAPIFailure):
    pass


class SteamAPIFailureUnauthorized(SteamAPIFailure):
    pass


class SteamAPIFailureNotFound(SteamAPIFailure):
    pass


# Server Problem
class SteamAPIError(APIException):
    """
        An API error signifies a problem with the server
    """
    pass


class SteamAPIErrorServerInnerError(SteamAPIError):
    pass


class SteamAPIErrorServerTempNotAvailable(SteamAPIError):
    pass


# global handling function for response from Steam Web Api
def handle_error(response):
    """
    Standard Http Error Code handling
    :param response: 
    :return: 
    """

    if response.status_code // 100 == 4:
        if response.status_code == 404:
            raise SteamAPIFailureNotFound("未找到,请求的API不存在")
        elif response.status_code == 401:
            raise SteamAPIFailureUnauthorized("未经授权,访问被拒绝。重试无效。请验证您的 key= 参数")
        elif response.status_code == 403:
            raise SteamAPIFailureForbidden("禁止,访问被拒绝。重试无效。请验证您的 key= 参数")
        elif response.status_code == 405:
            raise SteamAPIFailureWrongMethod("不允许使用此方法,调用此 API 的 HTTP 方法错误")
        elif response.status_code == 429:
            raise SteamAPIFailureRequestLimit("过多请求,您受到速率限制")
        elif response.status_code == 400:
            raise SteamAPIFailureBadCall("错误请求,请确认所有必需参数都已发送")
        else:
            raise SteamAPIFailure("错误请求，请检查请求参数与环境")
    elif response.status_code // 100 == 5:
        if response.status_code == 500:
            raise SteamAPIErrorServerInnerError("内部服务器错误，发生了无法恢复的错误，请重试")
        elif response.status_code == 503:
            raise SteamAPIErrorServerTempNotAvailable("服务器暂时不可用，或过于繁忙而无法响应。请稍后重试")
        else:
            raise SteamAPIError("服务器错误，请稍后重试")
    else:
        return
