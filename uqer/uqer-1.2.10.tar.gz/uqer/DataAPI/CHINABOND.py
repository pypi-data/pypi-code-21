# -*- coding: UTF-8 -*-
from . import api_base
try:
    from StringIO import StringIO
except:
    from io import StringIO
import pandas as pd
import sys
from datetime import datetime
from .api_base import get_cache_key, get_data_from_cache, put_data_in_cache, pretty_traceback
import inspect
try:
    unicode
except:
    unicode = str

__doc__="中国债券信息网"
def YieldCurveGet(CurveName, Tenor, CurveType = "", BeginDate = "", EndDate = "", field = "", pandas = "1"):
    """
    输入中债收益率曲线名称、曲线类型、待偿期限，可查询到中债在这些条件下的收益率
    
    :param CurveName: 收益率曲线名称，输入如中债收益率曲线名称“中国固定利率国债收益率曲线”,可同时输入多个收益率曲线名称,可以是列表
    :param Tenor: 待偿期限，以年为单位，如1个月，输入"0.08",,可同时输入多个待偿期限,可以是列表
    :param CurveType: 收益率曲线类型，可选：到期、即期、远期的即期、远期的到期，默认为"到期",可空
    :param BeginDate: 数据起始日期，默认今天，输入格式“YYYYMMDD”,可空
    :param EndDate: 数据起始日期，默认今天，输入格式“YYYYMMDD”,可空
    :param field: 所需字段,可以是列表,可空
    :param pandas: 1表示返回 pandas data frame，0表示返回csv,可空
    :return: :raise e: API查询的结果，是CSV或者被转成pandas data frame；若查询API失败，返回空data frame； 若解析失败，则抛出异常
    """
        
    pretty_traceback()
    frame = inspect.currentframe()
    func_name, cache_key = get_cache_key(frame)
    cache_result = get_data_from_cache(func_name, cache_key)
    if cache_result is not None:
        return cache_result
    split_index = None
    split_param = None
    httpClient = api_base.__getConn__()    
    requestString = []
    requestString.append('/api/bond/getYieldCurve.csv?ispandas=1&') 
    requestString.append("CurveName=")
    if hasattr(CurveName,'__iter__') and not isinstance(CurveName, str):
        if len(CurveName) > 100 and split_param is None:
            split_index = len(requestString)
            split_param = CurveName
            requestString.append(None)
        else:
            requestString.append(','.join(CurveName))
    else:
        requestString.append(CurveName)
    requestString.append("&Tenor=")
    if hasattr(Tenor,'__iter__') and not isinstance(Tenor, str):
        if len(Tenor) > 100 and split_param is None:
            split_index = len(requestString)
            split_param = Tenor
            requestString.append(None)
        else:
            requestString.append(','.join(Tenor))
    else:
        requestString.append(Tenor)
    if not isinstance(CurveType, str) and not isinstance(CurveType, unicode):
        CurveType = str(CurveType)

    requestString.append("&CurveType=%s"%(CurveType))
    try:
        BeginDate = BeginDate.strftime('%Y%m%d')
    except:
        BeginDate = BeginDate.replace('-', '')
    requestString.append("&BeginDate=%s"%(BeginDate))
    try:
        EndDate = EndDate.strftime('%Y%m%d')
    except:
        EndDate = EndDate.replace('-', '')
    requestString.append("&EndDate=%s"%(EndDate))
    requestString.append("&field=")
    if hasattr(field,'__iter__') and not isinstance(field, str):
        if len(field) > 100 and split_param is None:
            split_index = len(requestString)
            split_param = field
            requestString.append(None)
        else:
            requestString.append(','.join(field))
    else:
        requestString.append(field)
    if split_param is None:
        csvString = api_base.__getCSV__(''.join(requestString), httpClient, gw=True)
        if csvString is None or len(csvString) == 0 or (csvString[0] == '-' and not api_base.is_no_data_warn(csvString, False)) or csvString[0] == '{':
            api_base.handle_error(csvString, -1)
        elif csvString[:2] == '-1':
            csvString = ''
    else:
        p_list = api_base.splist(split_param, 100)
        csvString = []
        for index, item in enumerate(p_list):
            requestString[split_index] = ','.join(item)
            temp_result = api_base.__getCSV__(''.join(requestString), httpClient, gw=True)
            if temp_result is None or len(temp_result) == 0 or temp_result[0] == '{' or (temp_result[0] == '-' and not api_base.is_no_data_warn(temp_result, False)):
                api_base.handle_error(temp_result, -1)
            if temp_result[:2] != '-1':
                csvString.append(temp_result if len(csvString) == 0 else temp_result[temp_result.find('\n')+1:])
        csvString = ''.join(csvString)

    if len(csvString) == 0:
        if 'field' not in locals() or len(field) == 0:
            field = [u'CurveName', u'CurveType', u'Tenor', u'DataDate', u'Yield']
        if hasattr(field, '__iter__') and not isinstance(field, str):
            csvString = ','.join(field) + '\n'
        else:
            csvString = field + '\n'
    if pandas != "1":
        put_data_in_cache(func_name, cache_key, csvString)
        return csvString
    try:
        myIO = StringIO(csvString)
        pdFrame = pd.read_csv(myIO, dtype = {'CurveName': 'str','CurveType': 'str'},  )
        put_data_in_cache(func_name, cache_key, pdFrame)
        return pdFrame
    except Exception as e:
        raise e
    finally:
        myIO.close()

