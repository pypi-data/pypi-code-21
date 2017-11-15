# -*- coding: utf-8 -*-
"""
作者 : dfugo(chengang.net@gmail.com)
时间 ： 2016/3/14
身份证相关的类
"""
import re
import date

def is_valid_chinese_idcard(idcard,allow_15=False):
    if len(idcard)!=18:
        return False

    result = False
    str = idcard.upper()
    tmpsum = int(str[0])*7 + int(str[1])*9 + int(str[2])*10 + int(str[3])*5 + int(str[4])*8 \
            + int(str[5])*4 + int(str[6])*2 + int(str[7])*1 + int(str[8])*6 + int(str[9])*3 \
            + int(str[10])*7 + int(str[11])*9 + int(str[12])*10 + int(str[13])*5 \
            + int(str[14])*8 + int(str[15])*4 + int(str[16])*2
    remainder = tmpsum % 11
    maptable = {0: '1', 1: '0', 2: 'X', 3: '9', 4: '8', 5: '7', 6: '6', 7: '5', 8: '4', 9: '3', 10: '2'}
    if maptable[remainder] == str[17]:
        result = True
    return result


def is_valid_chinese_idcard_old(idcard,allow_15=True):
    idcard_length = len(idcard)
    if idcard_length!= 15 and idcard_length!=18:
        return False

    result = True
    msg = u''
    Errors=['验证通过!','身份证号码位数不对!','身份证号码出生日期超出范围或含有非法字符!','身份证号码校验错误!','身份证地区非法!']
    area={"11":"北京","12":"天津","13":"河北","14":"山西","15":"内蒙古","21":"辽宁","22":"吉林","23":"黑龙江","31":"上海","32":"江苏","33":"浙江","34":"安徽","35":"福建","36":"江西","37":"山东","41":"河南","42":"湖北","43":"湖南","44":"广东","45":"广西","46":"海南","50":"重庆","51":"四川","52":"贵州","53":"云南","54":"西藏","61":"陕西","62":"甘肃","63":"青海","64":"宁夏","65":"新疆","71":"台湾","81":"香港","82":"澳门","91":"国外"}
    idcard=str(idcard).upper()
    idcard=idcard.strip()
    idcard_list=list(idcard)

    #地区校验
    if(not area[(idcard)[0:2]]):
        msg =  Errors[4]
        result = False

    #15位身份号码检测
    if(len(idcard)==15 and allow_15):
        if((int(idcard[6:8])+1900) % 4 == 0 or((int(idcard[6:8])+1900) % 100 == 0 and (int(idcard[6:8])+1900) % 4 == 0 )):
            ereg=re.compile('[1-9][0-9]{5}[0-9]{2}((01|03|05|07|08|10|12)(0[1-9]|[1-2][0-9]|3[0-1])|(04|06|09|11)(0[1-9]|[1-2][0-9]|30)|02(0[1-9]|[1-2][0-9]))[0-9]{3}$')#//测试出生日期的合法性
        else:
            ereg=re.compile('[1-9][0-9]{5}[0-9]{2}((01|03|05|07|08|10|12)(0[1-9]|[1-2][0-9]|3[0-1])|(04|06|09|11)(0[1-9]|[1-2][0-9]|30)|02(0[1-9]|1[0-9]|2[0-8]))[0-9]{3}$')#//测试出生日期的合法性
        if(re.match(ereg,idcard)):
            msg = Errors[0]
        else:
            msg = Errors[2]
            result = False

    #18位身份号码检测
    elif(len(idcard)==18):
        #出生日期的合法性检查
        #闰年月日:((01|03|05|07|08|10|12)(0[1-9]|[1-2][0-9]|3[0-1])|(04|06|09|11)(0[1-9]|[1-2][0-9]|30)|02(0[1-9]|[1-2][0-9]))
        #平年月日:((01|03|05|07|08|10|12)(0[1-9]|[1-2][0-9]|3[0-1])|(04|06|09|11)(0[1-9]|[1-2][0-9]|30)|02(0[1-9]|1[0-9]|2[0-8]))
        if(int(idcard[6:10]) % 4 == 0 or (int(idcard[6:10]) % 100 == 0 and int(idcard[6:10])%4 == 0 )):
            ereg=re.compile('[1-9][0-9]{5}19[0-9]{2}((01|03|05|07|08|10|12)(0[1-9]|[1-2][0-9]|3[0-1])|(04|06|09|11)(0[1-9]|[1-2][0-9]|30)|02(0[1-9]|[1-2][0-9]))[0-9]{3}[0-9Xx]$')#//闰年出生日期的合法性正则表达式
        else:
            ereg=re.compile('[1-9][0-9]{5}19[0-9]{2}((01|03|05|07|08|10|12)(0[1-9]|[1-2][0-9]|3[0-1])|(04|06|09|11)(0[1-9]|[1-2][0-9]|30)|02(0[1-9]|1[0-9]|2[0-8]))[0-9]{3}[0-9Xx]$')#//平年出生日期的合法性正则表达式
        #//测试出生日期的合法性
        if(re.match(ereg,idcard)):
            #//计算校验位
            S = (int(idcard_list[0]) + int(idcard_list[10])) * 7 + (int(idcard_list[1]) + int(idcard_list[11])) * 9 + (int(idcard_list[2]) + int(idcard_list[12])) * 10 + (int(idcard_list[3]) + int(idcard_list[13])) * 5 + (int(idcard_list[4]) + int(idcard_list[14])) * 8 + (int(idcard_list[5]) + int(idcard_list[15])) * 4 + (int(idcard_list[6]) + int(idcard_list[16])) * 2 + int(idcard_list[7]) * 1 + int(idcard_list[8]) * 6 + int(idcard_list[9]) * 3
            Y = S % 11
            M = "F"
            JYM = "10X98765432"
            M = JYM[Y]#判断校验位
            if(M == idcard_list[17]):#检测ID的校验位
                msg = Errors[0]
            else:
                msg = Errors[3]
                result = False
        else:
            msg = Errors[2]
            result = False
    else:
        msg = Errors[1]
        result = False
    print(msg)
    return result

def get_birthday_from_chinese_idcard(idcard):
    """
    根据中国身份证号获得出生日期
    :param idcard: 身份证
    :return: 返回日期格式的生日，若身份证号码错误，则返回None
    """
    result = None
    if not is_valid_chinese_idcard(idcard,allow_15=True):
        return None

    if len(idcard) == 15:
        result = date.str_to_date('19{year}-{month}-{day}'.format(year=idcard[6:8],month=idcard[8:10],day=idcard[10:12]))
        if not result:
            result = None
        return result

    if len(idcard) == 18:
        result = date.str_to_date('{year}-{month}-{day}'.format(year=idcard[6:10],month=idcard[10:12],day=idcard[12:14]))
        if not result:
            result = None
        return result

    return result

def get_gender_from_chinese_idcard(idcard):
    """
    根据中国身份证号码返回其性别
    :param idcard: 身份证号码
    :return: 返回性别 '男' 或者 '女'，验证失败返回None
    """
    result = None
    if not is_valid_chinese_idcard(idcard,allow_15=True):
        return None

    if len(idcard) == 15:
        result = u'男' if int(idcard[-1]) % 2 == 1 else u'女'
        return result

    if len(idcard) == 18:
        result = u'男' if int(idcard[-2]) % 2 == 1 else u'女'
        return result
    return result


def is_valid_passport(idcard):
    """
    验证是否是有效的护照号码
    :param idcard: 护照号
    :return: 验证通过返回True
    """
    try:
        if len(idcard)<8:
            return  False
        if len(idcard)>20:
            return False
        pattern = ur'^[-_a-zA-Z0-9]+$'
        m = re.match(pattern, idcard)
        return m is not None
    except:
        return False


if __name__ == '__main__':
    print(is_valid_chinese_idcard('370202200509012201'))

    print(is_valid_passport(idcard='212312321'))