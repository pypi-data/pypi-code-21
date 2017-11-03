# coding: utf-8

import json
import requests
import traceback
import datetime
import base64
import re
import sys
from pandas import DataFrame,Series
import pandas as pd
import numpy as np


class HsonBase():
    """
    根据开放平台获取数据，接口设计如下：
    1、接口权限：
        接口权限是通过token控制，目前是直接从另外个服务器获取，没有加密小心别漏出去
    """
    # host = 'sandbox.hscloud.cn'
    host = 'open.hscloud.cn'
    host_v1 = 'https://' + 'open.hscloud.cn' + '/quote/v1'
    host_v2 = 'https://' + 'open.hscloud.cn' + '/quote/v2'
    host_info_v2 = 'https://' + 'open.hscloud.cn' + '/info/v2'
    g_token = None

    # def getAccessToken_hson(self):
    #     '''
    #     废弃，使用下面的hack
    #     '''
    #     #     key='d952ac95-5875-4254-8cc6-e250b340d883'
    #     #     secret='8a59e2f4-3c32-46c3-a74b-8d031d6de2ab'
    #
    #     key = 'a9b86543-9dfd-4ceb-b37e-9e698bc6fb2f'
    #     secret = '41043417-fe94-438a-9700-9698b1c333e3'
    #     url = 'https://sandbox.hscloud.cn/oauth2/oauth2/token'
    #     # py3使用
    #     authoriz = 'Basic ' + base64.b64encode(bytes(key + ":" + secret, 'utf8')).decode()
    #     # py2使用
    #     #     authoriz = 'Basic '+ base64.b64encode(key+":"+secret).decode()
    #     print(authoriz)
    #     # 头部Authorization应填写对“app_key:app_secret”进行Base64编码后的字符串（不包括双引号，字符采用UTF-8编码）。
    #     my_headers = {'Host': self.host,
    #                   'Content-type': 'application/x-www-form-urlencoded',
    #                   'Authorization': authoriz,
    #                   'Accept-Encoding': 'gzip, deflate'
    #                   }
    #     # 参数“grant_type”应填写“client_credentials”
    #     body = {"grant_type": "client_credentials"}
    #
    #     try:
    #         r = requests.post(url, headers=my_headers, data=body, timeout=5)
    #         #         print(r.text)
    #         if (r.status_code == 200):
    #             rs = r.json()
    #             return rs["access_token"]
    #     except:
    #         print("get Authorization exception ", sys.exc_info())
    #     return 'error'

    def get_access_token_hack(self):
        """
            所有接口的权限获取，都依赖它
        :return:
        """
        if self.g_token is not None:
            return self.g_token
        url_token = 'http://www.ziruxing.com:9003/api/cjj/dtzq/data/token'
        my_headers = {}
        r = requests.get(url_token, headers=my_headers, params=None, timeout=5)
        if (r.status_code == 200):
            rs = json.loads(r.text)
            token = rs['data']
            return token

    def http_get_hsopen(self, url, params):
        """
        请求接口的基类，所有请求接口都调用这个get方法，不用担心权限的获取
        :param url:
        :param params:
        :return:
        """
        try:
            accessToken = self.get_access_token_hack()
            #                 https://open.hscloud.cn/quote/v1/real?en_prod_code=603031.SS,603268.SS,&fields=prod_name,last_px&access_token=87CCBDA1385E48989CB8D7C98AE1C47E201710141738555FBA0802&t=1507985332927
            my_headers = {'Host': self.host,
                          'Authorization': 'Bearer ' + accessToken
                          }
            #         params.update({'access_token':accessToken})
            r = requests.get(url, headers=my_headers, params=params, timeout=5)
            #         print(r.text)
            if (r.status_code == 200):
                rs = r.json()
                return rs
        except:
            print("get exception ", sys.exc_info())
        return 'error'

    def get_stock_id_hson(self, stock_code):
        """
        转换成股票代码id,600136.XSHG->6001361
        """
        code = stock_code
        idx = stock_code.find('.')
        if idx > 0:
            code = code[0:idx]
        if code.startswith("60"):
            code = code + ".SS";
        elif code.startswith("00"):
            code = code + ".SZ";
        elif code.startswith("300"):
            code = code + ".SZ";
        return code


class HsonData(HsonBase):
    """
    1、接口权限：
    2、获取交易日
        get_trade_days
    3、获取资金流数据
        3.1 天
        3.2 分钟
    4、获取K线数据
        4.1 天
        4.2 周
        4.3 月
        4.4 分钟(1,5,15)
        4.5 支持股票和指数
    5、获取所有股票列表
        5.1 获取所有列表
        5.2 获取大盘股 小盘股 创业板列表
        5.3
    6、获取板块列表
        6.1 概念板块列表
        6.2 行业板块列表
        6.3 指数列表
    7、根据板块获取成分股列表
        7.1 概念板块
        7.2 行业板块
        7.3 指数
    8、根据股票获取相关板块
        8.1 概念板块列表
        8.2 行业板块列表
        8.3 地域板块列表
    9、根据股票获取上市日期
    10、分红送转查询
        10.1 送股，转增，派息，除权日，股权登记日，分红日
    11、查询基本面
        11.1 市盈率，市净率，流通市值，总股本

    12、今日申购新股

    13、获取证券信息
        13.1 证券代码	、证券简称、上市日期、证券类型、证券市场、上市板块

    14、查询前10大流通股东

    15、当前行情报价
        15.1 open_px,high_px,low_px,last_px,business_amount,business_balance,offer_grp,bid_grp

    16、分时数据

    16、板块成份股排序（block/sort）

    17、关联代码（codes）



    恒生开放平台API文档：https://www.hscloud.cn/wiki/api/1_quote_v1_kline.html

    """

    def get_holiday(self, year, finance_mic='SS'):
        """
        获取节假日
        return:
            ['20160101', '20160102',...]
        """
        url = self.host_v1 + '/market/holiday'
        params = dict(finance_mic=finance_mic,
                      date=year)
        result = self.http_get_hsopen(url, params)
        return result['data']['en_holiday'].split(',')

    def get_trade_days(self, start_date, end_date):
        '''
        获取两个日期之间的交易日
        包含 start_date
        不包含 end_date
        '''
        trade_days = []

        year1 = start_date.year
        year2 = end_date.year
        holidays = []
        for i in range(year2 - year1 + 1):
            holiday = self.get_holiday(year1 + i)
            holidays.extend(holiday)

        date1 = start_date
        while date1 < end_date:
            date1_str = datetime.datetime.strftime(date1, '%Y%m%d')
            if date1_str not in holidays:
                trade_days.append(date1_str)
            date1 = date1 + datetime.timedelta(days=1)
        return trade_days

    def get_stock_list(self):
        """
        获取证券列表
        :return:
        """
        pass


    def get_money_flow_day(self, stock_code):
        """
        获取资金流
        :param stock_code:
        :return:
        """
        stock_code = self.get_stock_id_hson(stock_code)
        url = self.host_v2 + '/fundflow'
        params = {"en_prod_code": stock_code, "get_type": "byorder"}
        self.http_get_hsopen(url, params)

    def get_money_flow_minute(self, stock_code, date, time):
        """
        获取分钟级别的资金流

        :param stock_code:
        :param date:
        :param time:
        :return:
            ["min_time","super_in","super_out","large_in","large_out","medium_in","medium_out","little_in","little_out"]
        """
        stock_code = self.get_stock_id_hson(stock_code)
        url = self.host_v2 + '/fundflow_trademin'
        params = {"prod_code": stock_code, "date": date}
        data = self.http_get_hsopen(url, params)
        fundflow_trademin_grp = data['data']['fundflow_trademin_grp']
        mflow_dt = []
        for mflow in fundflow_trademin_grp:
            if mflow[0] == time:
                mflow_dt = mflow
        if len(mflow_dt) == 0:
            for mflow in fundflow_trademin_grp:
                if mflow[0] == time - 1:
                    mflow_dt = mflow
        return mflow_dt


    def get_boards_of_stock(self, stock_code, type='GN'):
        """
        根据股票获取概念板块或者行业板块
        :param stock_code:
        :param type:
        :return:
        """
        stock_code = self.get_stock_id_hson(stock_code)
        url = self.host_v1 + '/block/query'
        params = {"prod_code": stock_code}
        data = self.http_get_hsopen(url, params)
        boards = data['data'][stock_code]
        filter_boards = []
        for board in boards:
            if board[2].find("." + type) != -1:
                filter_boards.append(board)
        return filter_boards

    def get_board_name_of_stock(self, stock):
        try:
            boards = self.get_boards_of_stock_hson(stock)
            rs_str = ''
            for board in boards:
                rs_str += (board[1] + ',')
            return rs_str[0:-1]
        except:
            print("get_board_name_of_stock exception ", traceback.print_exc())
            return ''

    def get_kline(self,
                  stock_code,
                  date,
                  data_count=10,
                  candle_period=6, #默认日K
                  candle_mode=1, #默认前复权
                  get_type='offset',#默认按照便宜值查询
                  min_time = None,#分钟级别需要
                  fields=None #默认全部字段
                  ):
        '''
        获取K线数据，基类，需要封装成好用的
        其余参数参考：https://www.hscloud.cn/wiki/api/1_quote_v1_kline.html
        根据需要改写此函数
        stock_code：
            有且仅能有 1 个代码；证券代码包含交易所代码做后缀，作为该代码的唯一标识。如：600570.SS
        get_type:
            offset 按偏移查找；
            range 按日期区间查找；
            必须输入其中一个值
        candle_period:取值可以是数字1-9，表示含义如下：
            1：1分钟K线
            2：5分钟K线
            3：15分钟K线
            4：30分钟K线
            5：60分钟K线
            6：日K线
            7：周K线
            8：月K线
            9：年K线
        candle_mode:K线模式
            0：原始K线
            1：前复权K线
            2：后复权K线
        fields: 允许的字段：
            开盘价：open_px
            最高价：high_px
            最低价：low_px
            收盘价：close_px
            成交量：business_amount
            成交额：business_balance
            如果没有指定任何有效的字段，则返回所有字段
        date:不输入默认为当前日期；请求日K线时，如果输入日期，不返回该日期的K线
            get_type=offset时有效
        min_time:分钟 K 线的时间 HHMM,对于 短 周期 K 线 类型 使用(1min,5min 等)，
            不填写表示最新的市场时间，若填写必须同时填写 date 字段。
            请求分钟K线时，如果输入该字段，不返回输入分钟的K线
            仅在 get_type=offset 且candle_period=1~5（分钟 K线）时有效。
        data_count:需要取得的 K 线的根数
            如果该字段不存在，取值范围[1, 1000]，默认为 10 个。
            仅在 get_type=offset 时有效。
        start_date:
            1、 start_date 和 end_date 均不填， 返回距离当前日期的1000 根 K 线；
            2、 仅填 start_date， 当 start_date和最新日期之间的数据不足1000 根，返回 start_date 和最新日期之间的数据；如果数据超过 1000 根 K 线， 则返回距离当前日期的 1000 根 K线；
            3、 仅填 end_date ， 返 回end_date 之前存在的的最多1000 根 K 线；
            4、 start_date 和 end_date 均填充，返回该日期区间（闭区间）的数据，最多 1000 根。
            仅在 get_type=range 时有效。
        end_date:默认为当前日期；
            1、 start_date 和 end_date 均不填， 返回距离当前日期的1000 根 K 线；
            2、 仅填 start_date， 当 start_date和最新日期之间的数据不足1000 根，返回 start_date 和最新日期之间的数据；如果数据超过 1000 根 K 线， 则返回距离当前日期的 1000 根 K线；
            3、 仅填 end_date ， 返 回end_date 之前存在的的最多1000 根 K 线；
            4、 start_date 和 end_date 均填充，返回该日期区间（闭区间）的数据，最多 1000 根。
            仅在 get_type=range 时有效。

        '''
        #     https://sandbox.hscloud.cn/quote/v1/kline
        stock_code = self.get_stock_id_hson(stock_code)
        url = self.host_v1 + '/kline'
        params = dict(get_type = get_type,
                  prod_code = stock_code,
                  date = date,
                  data_count=data_count,
                  candle_period = candle_period,
                  candle_mode =  candle_mode,
                  )
        if min_time is not None:
            params.setdefault("min_time",min_time)
        # if fields is not None:
        #     params['fields'] = fields
        data = self.http_get_hsopen(url, params)
        columns = data['data']['candle']['fields']
        row_data = data['data']['candle'][stock_code]
        df_data = DataFrame(row_data, columns=columns)
        return df_data

    def get_kline_day(self,stock_code
                          ,end_date
                          , count
                          # , fields=['close', 'volume', 'open', 'high', 'low', 'pre_close']
                          # , skip_paused=True
                          # , fq='pre'
                      ):
        """
        获取日级别K线数据
        :param stock:
        :param end_date:
        :param count:
        :param frequency:
        :param fields:
        :param skip_paused:
        :param fq:
        :return:
            pd.DataFrame
            min_time  open_px  high_px  low_px  close_px  business_amount  business_balance
        0  20171019    28.12    28.66   27.89     28.26         16641711    16641711
        1  20171020    28.24    29.07   28.02     29.03         19339570    19339570
        """
        stock_code = self.get_stock_id_hson(stock_code)
        data = self.get_kline(stock_code,end_date,count)
        return data

    def get_kline_minute(self,
                         stock_code,
                         end_date,
                         end_time,
                         count,
                         # frequency='1m',
                         # fields=['close', 'volume', 'open', 'high', 'low','pre_close'],
                         # skip_paused=True,
                         fq='pre'
                         ):
        """
        获取日级别K线数据
        :param stock:
        :param end_date:
        :param count:
        :param frequency:
        :param fields:
        :param skip_paused:
        :param fq:
        :return:
            pd.DataFrame
            min_time  open_px  high_px  low_px  close_px  business_amount  business_balance
        0  201711011451    28.09    28.11   28.09     28.11    52570        1477244
        1  201711011452    28.10    28.12   28.10     28.11    52600        1478546
        """
        stock_code = self.get_stock_id_hson(stock_code)

        df_data = self.get_kline(stock_code, end_date, count,candle_period=1,min_time=end_time)
        return df_data

    def get_stock_info(self, stock):
        '''
        获取证券信息
        证券代码、证券简称、上市日期、证券类型、证券市场、上市板块
        :param stock: 600549
        :return: {"issue_price":"11.6000","listed_date":"2002-11-07","listed_sector":"主板","secu_abbr":"厦门钨业","secu_category":"A股","secu_code":"600549","secu_market":"上海证券交易所"}
        issue_price 发行价
        listed_date 上市日期
        listed_sector 上市板块
        secu_code 证券代码
        secu_abbr 证券简称
        secu_category 证券类型
        secu_market 证券市场
        '''
        try:
            stock_info = self.get_stock_info_hson(stock)
            rs = {
                'issue_price': stock_info['issue_price'],
                'listed_date': stock_info['listed_date'],
                'listed_sector': stock_info['listed_sector'],
                'secu_code': stock_info['secu_code'],
                'secu_abbr': stock_info['secu_abbr'],
                'secu_category': stock_info['secu_category'],
                'secu_market': stock_info['secu_market']
            }
            return rs
        except:
            print("get_stock_info_of_stock exception ", traceback.print_exc())
            return {}

    def get_stock_info_hson(self, stock_code):
        stock_code = self.get_stock_id_hson(stock_code)
        url = self.host_info_v2 + '/query/f10_secu_info'
        params = {"en_prod_code": stock_code}
        data = self.http_get_hsopen(url, params)
        stock_info = data['data'][0]['20101013'][0][stock_code][0]
        return stock_info


if __name__ == "__main__":
    print("想测试？去test文件夹下找对应测试类")

