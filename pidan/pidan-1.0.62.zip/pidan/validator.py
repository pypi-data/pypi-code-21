# -*- coding: utf-8 -*-
import re
import time

def check_len(value,min,max):
    '检查字符串的长度是否在min-max之间'

    #将字符串转换成utf-8编码,一个中文算3个字符
    length = len(value)
    utf8_length = len(value.encode('utf-8'))
    length = (utf8_length - length)/2 + length
    if min <= length <= max:
        return True
    else:
        return False

def is_int(str):
    '''判断字符串是否为整数'''
    try:
        x=int(str)
        return isinstance(x,int) or isinstance(x,long)
    except ValueError:
        return False

def is_number(str):
    '''判断字符串是否为浮点数'''
    result = False
    try:
        result =  type(eval(str)) in (float,int,long)
    except:
        pass
    return result

def is_email(str):
    '检查给定的字符串是否是Email'

    #如果邮件长度不是4-50个字符，则认为不正确
    if not check_len(str,4,50):
        return False

    pattern = r"^\w+((-\w+)|(\.\w+))*\@[A-Za-z0-9]+((\.|-)[A-Za-z0-9]+)*\.[A-Za-z0-9]+$"
    m = re.match(pattern,str)
    return m is not None

def is_valid_url(str):
    '检查给定的字符串是否是有效的url'

    #如果邮件长度不是11-500个字符，则认为不正确
    if not check_len(str,11,500):
        return False

    pattern = "(http|https)\\://([a-zA-Z0-9\\.\\-]+(\\:[a-zA-"\
           + "Z0-9\\.&%\\$\\-]+)*@)?((25[0-5]|2[0-4][0-9]|[0-1]{1}[0-9]{"\
           + "2}|[1-9]{1}[0-9]{1}|[1-9])\\.(25[0-5]|2[0-4][0-9]|[0-1]{1}"\
           + "[0-9]{2}|[1-9]{1}[0-9]{1}|[1-9]|0)\\.(25[0-5]|2[0-4][0-9]|"\
           + "[0-1]{1}[0-9]{2}|[1-9]{1}[0-9]{1}|[1-9]|0)\\.(25[0-5]|2[0-"\
           + "4][0-9]|[0-1]{1}[0-9]{2}|[1-9]{1}[0-9]{1}|[0-9])|([a-zA-Z0"\
           + "-9\\-]+\\.)*[a-zA-Z0-9\\-]+\\.[a-zA-Z]{2,4})(\\:[0-9]+)?(/"\
           + "[^/][a-zA-Z0-9\\.\\,\\?\\'\\\\/\\+&%\\$\\=~_\\-@]*)*$"
    m = re.match(pattern,str)
    return m is not None

def is_valid_password(str,min=3,max=22):
    '判断是否是可用的密码'

    #检查密码的长度
    if not check_len(str,min,max):
        return False

    pattern = r"^[\@A-Za-z0-9\!\#\$\%\^\&\*\.\~]{{{min},{max}}}$".format(min=min,max=max)
    m = re.match(pattern,str)
    return m is not None

def is_valid_nickname(str):
    '判断是否是可用的昵称'
    if not check_len(str,4,14):
        return False

    pattern = ur"^[-_a-zA-Z0-9\u4e00-\u9fa5]+$"
    m = re.match(pattern,str)
    return m is not None

def is_valid_chinese_name(name):
    """
    判断给定的字符串是否是合法的中国人名
    按照国家规定，中国人的姓名应该在2-6个汉字
    :param name: 姓名
    :return: 验证成功返回True
    """
    pattern = ur"^[\u4e00-\u9fa5]{2,14}$"
    m = re.match(pattern,name)
    return m is not None

def is_contain_space(str):
    '''
    是否包含空格
    '''
    if ' ' in str:
        return True
    else:
        return False

def is_valid_date(str):
    '''判断是否是一个有效的日期字符串'''
    result = False
    try:
        t = time.strptime(str, "%Y-%m-%d")
        if t.tm_year > 1900:
            result = True
    except:
        result = False
    return result

def is_valid_mobile_phone(phone):
    '''判断是否是一个有效的手机号'''
    result = True
    if len(phone)!=11:
        result = False
    if not phone.startswith('1'):
        result = False
    return result


def is_valid_bank_card(card_number):
    """检查是否是有效的银行卡卡号"""
    def digits_of(n):
        return [int(d) for d in str(n)]

    result = False
    digits = digits_of(card_number)
    odd_digits = digits[-1::-2]
    even_digits = digits[-2::-2]
    checksum = 0
    checksum += sum(odd_digits)
    for d in even_digits:
        checksum += sum(digits_of(d * 2))
    t = checksum % 10
    if t ==0:
        result = True
    return result


if __name__ == "__main__":
    #print(is_email('iazxq@sohu.com333 hhdye'))
    print('is_valid_password=%s'%is_valid_password(u'ni!@#$%^^&*wq'))
    #print(is_valid_nickname('不吃皮蛋吃鸡蛋'))
    #print(is_valid_nickname('1111'))
    #print(check_len(u'ΤΧÉÆ',0,10000))
    #print(is_valid_date('2013-8-31'))
    print(is_valid_url('http://m.bandao.cn/touch/news/detail/2443450'))
    print(is_int('222222222222222222222222222222222222222'))
    print('is_mobile_phone:',is_valid_mobile_phone('513756048532'))
    print('is valid chinese name',is_valid_chinese_name(u'凌徐铁男等等你哈'))
    print('is_number=',is_number('12333333333333333333333333333333.00=1'))
    print('is_card=',is_valid_bank_card('4336680005399262'))