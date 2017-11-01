# -*- coding: utf-8 -*-
"""
Constant define
"""

__all__ = ['Constant', 'ConstantCaseError', 'ConstantError', 'ConstInstance']


class ConstantError(TypeError):
    pass


class ConstantCaseError(TypeError):
    pass


class Constant(object):
    """ 构造常量管理的类，一旦赋值不可更改 """

    def __setattr__(self, key, value):
        if key in self.__dict__:
            raise ConstantError("Can't change constant.%s" % key)

        if not key.isupper():
            raise ConstantCaseError('Constant name "%s" is not all uppercase' % key)

        self.__dict__[key] = value

    def __getattr__(self, item):
        try:
            return self.__dict__[item]
        except KeyError:
            return None


ConstInstance = Constant()

ConstInstance.COMMA_CHAR = ','
ConstInstance.UNDERLINE_CHAR = '_'
ConstInstance.BLANK_CHAR = ''

ConstInstance.LOGGER_TIP_TEXT = '=' * 40
