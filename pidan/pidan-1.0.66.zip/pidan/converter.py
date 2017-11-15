# -*- coding: utf-8 -*-
#转换相关的函数

def array_to_str(value,split_str='/'):
    '数组转换成字符串，使用split_str隔开'
    result = ''
    if value:
        result = split_str.join(map(lambda x:unicode(x),value))
    return result

def str_to_arry(value,split_str='/'):
    '''字符串转换成数组，通过split_str进行分割'''
    result = list()
    if value:
        result = value.split(split_str)
    return result

def str_to_int_arry(value,split_str='/'):
    '''字符串转换成整数数组，使用split_str进行分割'''
    result = list()
    try:
        str_list = str_to_arry(value,split_str=split_str)
        for item in str_list:
            result.append(int(item))
    except:
        pass
    return result


def xml_to_dict(xml_data,encoding='utf-8'):
    '''xml转换成字典'''
    import xml2dict
    return xml2dict.parse(xml_data,encoding=encoding)


def dict_to_json(dic):
    '''字典转换成json'''
    import json
    json.dumps()

if __name__ == '__main__':
    data='''<?xml version="1.0" encoding="utf-8" ?>

<returnsms>

    <returnstatus>Success</returnstatus>

    <message>鎿嶄綔鎴愬姛</message>

    <remainpoint>19</remainpoint>

    <taskID>1506261713544320</taskID>

    <successCounts>1</successCounts>

</returnsms>
    '''
    dic = xml_to_dict(data)
    print(dic.get('returnsms',{}).get('returnstatus',''))