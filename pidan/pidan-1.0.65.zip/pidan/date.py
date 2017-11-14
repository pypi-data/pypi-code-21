# -*- coding: utf-8 -*-
#日期相关的函数

import datetime,time
import converter
import traceback

def format_date(date_time):
    '格式化日期输出'
    result = ''
    if isinstance(date_time,datetime.datetime):
        result = date_time.strftime('%Y-%m-%d')
    return result


def format_date_time(date_time):
    '格式化日期、时间输出'
    result = ''
    if isinstance(date_time, datetime.datetime):
        result= date_time.strftime('%Y-%m-%d %H:%M:%S')
    return result


def get_first_day_of_this_year():
    '''得到今天第一天的日期，比如：2016-01-01
        返回类型是datetime
    '''
    return str_to_date('%s-01-01'%datetime.datetime.now().year)

def get_day_of_year(value=None):
    """
    返回指定的日期是当年的第几天
    :param value: 日期,可以为字符串也可以为日期格式
    :return: 第几天
    """
    if not value:
        value = datetime.datetime.now()
    if isinstance(value,str):
        value = str_to_date(value)
    year = value.year
    days = (value - str_to_date('%s-01-01'%year)).days + 1
    return days

def str_to_date(value):
    '字符串转换成日期格式'
    try:
        #如果传入的参数本身就是日期格式,则直接返回
        if isinstance(value,datetime.datetime):
            return value
        value = str(value)
        format="%Y-%m-%d"
        result = datetime.datetime.strptime(value,format)
        return result
    except:
        return ''

def get_date(date_time):
    '''将日期时间格式化为只有日期'''
    return str_to_date(format_date(date_time))

def str_to_datetime(str_datetime):
    '字符串转换成日期格式'
    try:
        #如果传入的参数本身就是日期格式,则直接返回
        if isinstance(str_datetime,datetime.datetime):
            return str_datetime

        str_datetime = str(str_datetime)
        format = "%Y-%m-%d %H:%M:%S"

        # 处理只有分，没有秒的情况
        datetime_section_list = str_datetime.split()
        if len(datetime_section_list) == 2:
            if len(datetime_section_list[1].split(':')) == 2:
                format = "%Y-%m-%d %H:%M"
        result = datetime.datetime.strptime(str_datetime,format)
        return result
    except:
        return ''


def get_age(born,compare_date=''):
    '''根据出生日期的时间，得到年龄'''
    if not isinstance(born,datetime.datetime):
        return 0
    try:
        today = datetime.date.today()
        if compare_date:
            today = str_to_date(compare_date).date()

        born = born.date()
        try:
            birthday = born.replace(year=today.year)
        except ValueError:  # raised when birth date is February 29 and the current year is not a leap year
            birthday = born.replace(year=today.year, day=born.day - 1)
        if birthday > today:
            return today.year - born.year - 1
        else:
            return today.year - born.year
    except:
        print(traceback.format_exc())
        return 0


def get_birthday_from_age(age):
    '''根据年龄获得出生日期'''
    result = datetime.datetime.now()
    try:
        today = datetime.datetime.now()
        birthday = today.replace(year=today.year-age)
        result = birthday
    except:
        pass
    return result

def get_date_range_from_age_range(from_age,to_age):
    '''根据年龄范围获得日期范围'''
    today = datetime.date.today()
    from_date = today.replace(year=today.year-from_age)
    to_date = today.replace(year=today.year-to_age)
    return to_date,from_date

def get_age_range(data):
    '''将字符串的年龄范围转换成元祖输出
        data格式：>3 、<3 、1-3 三种形式
    '''
    age_from,age_to = 0,0
    if data[0] == '>':
        age_from = int(data[1:])+1
    elif data[0] == '<':
        age_to = int(data[1:])-1
    else:
        age_range_list = converter.str_to_int_arry(data,'-')
        age_from = age_range_list[0]
        age_to = age_range_list[1]
    return age_from,age_to


def timestamp_to_datetime(value):
    format = '%Y-%m-%d %H:%M:%S'
    # value为传入的值为时间戳(整形)，如：1332888820
    value = time.localtime(value)
    ## 经过localtime转换后变成
    ## time.struct_time(tm_year=2012, tm_mon=3, tm_mday=28, tm_hour=6, tm_min=53, tm_sec=40, tm_wday=2, tm_yday=88, tm_isdst=0)
    # 最后再经过strftime函数转换为正常日期格式。
    dt = time.strftime(format, value)
    return dt

def datetime_to_timestamp(dt):
    '''日期转换成unix时间戳'''
    s = time.mktime(dt.timetuple())
    return int(s)

if __name__ == '__main__':
    t='2016-02-29 12:04'
    print(get_day_of_year('2017-3-27'))
